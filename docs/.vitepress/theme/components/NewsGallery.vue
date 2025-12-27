<script setup>
import { ref, onMounted } from 'vue'
import { withBase } from 'vitepress'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

const news = ref([])
const selectedNews = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await fetch(withBase('/data/news.json'))
    if (res.ok) {
      news.value = await res.json()
    }
  } catch (e) {
    console.error('Failed to load news:', e)
  } finally {
    loading.value = false
  }
})

const openNews = (item) => {
  selectedNews.value = item
  document.body.style.overflow = 'hidden'
}

const closeNews = () => {
  selectedNews.value = null
  document.body.style.overflow = ''
}

const renderMarkdown = (text) => {
  return md.render(text || '')
}
</script>

<template>
  <div class="swiss-gallery">
    <div v-if="loading" class="status-msg">LOADING DATA...</div>
    
    <div v-else-if="news.length === 0" class="status-msg">NO DATA AVAILABLE</div>

    <div v-else class="grid-container">
      <div 
        v-for="item in news" 
        :key="item.id" 
        class="news-item"
        @click="openNews(item)"
      >
        <div class="item-header">
          <span class="meta-date">{{ item.date }}</span>
          <div class="meta-tags">
            <span v-for="tag in item.tags" :key="tag" class="meta-tag">#{{ tag }}</span>
          </div>
        </div>
        
        <div class="item-body">
          <h3 class="item-title">{{ item.title }}</h3>
          <p class="item-summary">{{ item.summary }}</p>
        </div>

        <div class="item-footer">
          <span class="read-indicator">READ MORE</span>
          <span class="arrow">→</span>
        </div>
      </div>
    </div>

    <!-- Minimalist Modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="selectedNews" class="modal-overlay" @click="closeNews">
          <div class="modal-panel" @click.stop>
            
            <div class="modal-top-bar">
              <span class="modal-id">ID: {{ selectedNews.id.slice(-6) }}</span>
              <button class="close-btn" @click="closeNews">CLOSE [ESC]</button>
            </div>

            <div class="modal-content-scroll">
              <div class="article-header">
                <div class="article-meta">
                  <span>{{ selectedNews.date }}</span>
                  <span class="separator">/</span>
                  <span v-for="tag in selectedNews.tags" :key="tag">#{{ tag }} </span>
                </div>
                <h1 class="article-title">{{ selectedNews.title }}</h1>
              </div>

              <div class="article-body markdown-body" v-html="renderMarkdown(selectedNews.detail)"></div>
              
              <div class="article-footer">
                <a :href="selectedNews.link" target="_blank" class="source-link">
                  SOURCE LINK ↗
                </a>
              </div>
            </div>

          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
/* --- Swiss Style Variables --- */
.swiss-gallery {
  padding: 40px 0;
  font-family: "Inter", "Helvetica Neue", Helvetica, Arial, sans-serif;
  color: var(--vp-c-text-1);
}

.status-msg {
  font-family: monospace;
  text-align: center;
  padding: 40px;
  font-size: 14px;
  letter-spacing: 1px;
}

/* --- Grid System --- */
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  border-top: 1px solid var(--vp-c-divider);
  border-left: 1px solid var(--vp-c-divider);
}

.news-item {
  border-right: 1px solid var(--vp-c-divider);
  border-bottom: 1px solid var(--vp-c-divider);
  padding: 32px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 360px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  background: var(--vp-c-bg);
}

.news-item:hover {
  background-color: var(--vp-c-bg-soft);
}

.news-item:hover .read-indicator {
  text-decoration: underline;
}

/* --- Typography & Layout --- */
.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  font-size: 12px;
  font-family: monospace;
  color: var(--vp-c-text-2);
  letter-spacing: 0.05em;
}

.meta-tags {
  text-transform: uppercase;
}

.item-title {
  font-size: 24px;
  font-weight: 700;
  line-height: 1.2;
  margin: 0 0 16px 0;
  letter-spacing: -0.02em;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-summary {
  font-size: 15px;
  line-height: 1.5;
  color: var(--vp-c-text-2);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-weight: 400;
}

.item-footer {
  margin-top: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.05em;
}

/* --- Modal (Minimalist) --- */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(255, 255, 255, 0.95);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Dark mode adjustment for overlay */
:root.dark .modal-overlay {
  background: rgba(0, 0, 0, 0.95);
}

.modal-panel {
  width: 100%;
  max-width: 800px;
  height: 100%;
  background: var(--vp-c-bg);
  display: flex;
  flex-direction: column;
  border-left: 1px solid var(--vp-c-divider);
  border-right: 1px solid var(--vp-c-divider);
}

.modal-top-bar {
  padding: 20px 40px;
  border-bottom: 1px solid var(--vp-c-divider);
  display: flex;
  justify-content: space-between;
  font-family: monospace;
  font-size: 12px;
  text-transform: uppercase;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  color: inherit;
  font-weight: 700;
}

.close-btn:hover {
  text-decoration: underline;
}

.modal-content-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 60px 80px;
}

.article-header {
  margin-bottom: 60px;
}

.article-meta {
  font-family: monospace;
  font-size: 14px;
  color: var(--vp-c-text-2);
  margin-bottom: 20px;
}

.separator {
  margin: 0 8px;
}

.article-title {
  font-size: 48px;
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.article-body {
  font-size: 18px;
  line-height: 1.6;
  max-width: 65ch;
}

/* Markdown Styles override for Swiss look */
.markdown-body :deep(h2) {
  font-size: 24px;
  margin-top: 2em;
  margin-bottom: 1em;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.markdown-body :deep(p) {
  margin-bottom: 1.5em;
}

.markdown-body :deep(a) {
  color: var(--vp-c-text-1);
  text-decoration: underline;
  text-underline-offset: 4px;
}

.markdown-body :deep(blockquote) {
  border-left: 2px solid var(--vp-c-text-1);
  padding-left: 20px;
  margin: 2em 0;
  font-style: italic;
}

.article-footer {
  margin-top: 80px;
  padding-top: 40px;
  border-top: 1px solid var(--vp-c-divider);
}

.source-link {
  font-family: monospace;
  font-size: 14px;
  color: var(--vp-c-text-1);
  text-decoration: none;
  border: 1px solid var(--vp-c-divider);
  padding: 12px 24px;
  display: inline-block;
  transition: all 0.2s;
}

.source-link:hover {
  background: var(--vp-c-text-1);
  color: var(--vp-c-bg);
}

/* --- Transitions --- */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .grid-container {
    border-left: none;
    border-right: none;
  }
  
  .news-item {
    border-right: none;
    height: auto;
    min-height: 300px;
  }

  .modal-panel {
    border: none;
  }

  .modal-content-scroll {
    padding: 30px 20px;
  }

  .article-title {
    font-size: 32px;
  }
}
</style>
