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

// 🎨 Ultrathink Palette: Mesh Gradients
// 这些渐变旨在模仿极光和流体，而非僵硬的线性过渡
const gradients = [
  'radial-gradient(circle at 0% 0%, #a18cd1 0%, #fbc2eb 100%)',
  'linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%)',
  'linear-gradient(to top, #cfd9df 0%, #e2ebf0 100%)',
  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  'linear-gradient(to right, #4facfe 0%, #00f2fe 100%)',
  'linear-gradient(to right, #43e97b 0%, #38f9d7 100%)',
  'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
  'linear-gradient(to top, #a8edea 0%, #fed6e3 100%)'
]

const getRandomGradient = (id) => {
  const index = parseInt(id.slice(-1)) % gradients.length
  return gradients[index]
}

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
  <div class="news-gallery-container">
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在接入情报网络...</p>
    </div>
    
    <div v-else-if="news.length === 0" class="empty-state">
      <div class="empty-icon">📡</div>
      <p>暂无最新情报，请稍候再来。</p>
    </div>

    <div v-else class="gallery-grid">
      <div 
        v-for="item in news" 
        :key="item.id" 
        class="news-card"
        @click="openNews(item)"
      >
        <div class="card-visual" :style="{ background: getRandomGradient(item.id) }">
          <div class="card-overlay"></div>
          <div class="card-date">{{ item.date }}</div>
        </div>
        
        <div class="card-body">
          <div class="tags-row">
            <span v-for="tag in item.tags" :key="tag" class="tag-pill">{{ tag }}</span>
          </div>
          <h3 class="card-title">{{ item.title }}</h3>
          <p class="card-summary">{{ item.summary }}</p>
          
          <div class="card-footer">
            <span class="read-more">阅读详情 <span class="arrow">→</span></span>
          </div>
        </div>
      </div>
    </div>

    <!-- Teleport Modal to Body for better z-index management -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="selectedNews" class="modal-backdrop" @click="closeNews">
          <div class="modal-glass-panel" @click.stop>
            
            <div class="modal-header">
              <div class="modal-meta">
                <span class="modal-date">{{ selectedNews.date }}</span>
                <div class="modal-tags">
                  <span v-for="tag in selectedNews.tags" :key="tag" class="modal-tag">{{ tag }}</span>
                </div>
              </div>
              <button class="close-button" @click="closeNews">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>

            <div class="modal-scroll-content">
              <h2 class="modal-title">{{ selectedNews.title }}</h2>
              <div class="modal-markdown" v-html="renderMarkdown(selectedNews.detail)"></div>
              
              <div class="modal-actions">
                <a :href="selectedNews.link" target="_blank" class="action-button primary">
                  访问原始来源
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-left: 6px;">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
                    <polyline points="15 3 21 3 21 9"></polyline>
                    <line x1="10" y1="14" x2="21" y2="3"></line>
                  </svg>
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
/* --- Variables & Reset --- */
.news-gallery-container {
  padding: 40px 0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* --- Loading & Empty States --- */
.loading-state, .empty-state {
  text-align: center;
  padding: 60px 0;
  color: var(--vp-c-text-2);
  animation: fadeIn 0.5s ease;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(0,0,0,0.1);
  border-radius: 50%;
  border-top-color: var(--vp-c-brand);
  animation: spin 1s ease-in-out infinite;
  margin: 0 auto 20px;
}

@keyframes spin { to { transform: rotate(360deg); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

/* --- Grid Layout --- */
.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 32px;
}

/* --- Card Design (The "Art Piece") --- */
.news-card {
  background: var(--vp-c-bg-soft);
  border-radius: 20px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
  border: 1px solid rgba(128, 128, 128, 0.1);
  display: flex;
  flex-direction: column;
  height: 420px;
  position: relative;
}

.news-card:hover {
  transform: translateY(-8px) scale(1.01);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.12);
  border-color: rgba(128, 128, 128, 0.2);
}

.news-card:hover .read-more {
  color: var(--vp-c-brand);
  transform: translateX(4px);
}

.card-visual {
  height: 160px;
  position: relative;
  overflow: hidden;
}

.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, rgba(0,0,0,0) 0%, rgba(0,0,0,0.05) 100%);
  mix-blend-mode: multiply;
}

.card-date {
  position: absolute;
  bottom: 12px;
  right: 16px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  color: #333;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card-body {
  padding: 24px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.tag-pill {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--vp-c-brand);
  background: var(--vp-c-bg-mute);
  padding: 4px 10px;
  border-radius: 100px;
}

.card-title {
  font-size: 18px;
  font-weight: 700;
  line-height: 1.4;
  margin: 0 0 12px 0;
  color: var(--vp-c-text-1);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-summary {
  font-size: 14px;
  line-height: 1.6;
  color: var(--vp-c-text-2);
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 20px;
}

.card-footer {
  border-top: 1px solid var(--vp-c-divider);
  padding-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.read-more {
  font-size: 13px;
  font-weight: 600;
  color: var(--vp-c-text-2);
  display: flex;
  align-items: center;
  transition: all 0.3s ease;
}

.arrow {
  margin-left: 4px;
  transition: transform 0.3s ease;
}

/* --- Modal (Glassmorphism 2.0) --- */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(12px); /* Heavy blur for focus */
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-glass-panel {
  width: 100%;
  max-width: 720px;
  max-height: 85vh;
  background: var(--vp-c-bg);
  border-radius: 24px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid var(--vp-c-divider);
  transform-origin: center center;
}

.modal-header {
  padding: 24px 32px;
  border-bottom: 1px solid var(--vp-c-divider);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: var(--vp-c-bg-soft);
}

.modal-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.modal-date {
  font-size: 13px;
  color: var(--vp-c-text-3);
  font-weight: 500;
}

.modal-tags {
  display: flex;
  gap: 8px;
}

.modal-tag {
  font-size: 12px;
  color: var(--vp-c-text-1);
  background: var(--vp-c-bg-mute);
  padding: 2px 8px;
  border-radius: 4px;
}

.close-button {
  background: transparent;
  border: none;
  color: var(--vp-c-text-2);
  cursor: pointer;
  padding: 4px;
  border-radius: 50%;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  background: var(--vp-c-bg-mute);
  color: var(--vp-c-text-1);
}

.modal-scroll-content {
  padding: 32px;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.modal-title {
  font-size: 28px;
  font-weight: 800;
  line-height: 1.3;
  margin-bottom: 24px;
  background: linear-gradient(120deg, var(--vp-c-brand-light), var(--vp-c-brand-dark));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  display: inline-block;
}

.modal-markdown {
  font-size: 17px;
  line-height: 1.8;
  color: var(--vp-c-text-1);
}

/* Markdown Content Styling */
.modal-markdown :deep(h1),
.modal-markdown :deep(h2),
.modal-markdown :deep(h3) {
  margin-top: 1.5em;
  margin-bottom: 0.8em;
  font-weight: 700;
  color: var(--vp-c-text-1);
}

.modal-markdown :deep(p) {
  margin-bottom: 1.2em;
}

.modal-markdown :deep(ul),
.modal-markdown :deep(ol) {
  padding-left: 1.5em;
  margin-bottom: 1.2em;
}

.modal-markdown :deep(li) {
  margin-bottom: 0.5em;
}

.modal-markdown :deep(a) {
  color: var(--vp-c-brand);
  text-decoration: none;
  border-bottom: 1px dashed var(--vp-c-brand);
}

.modal-markdown :deep(blockquote) {
  border-left: 4px solid var(--vp-c-brand);
  padding-left: 16px;
  margin: 1.5em 0;
  color: var(--vp-c-text-2);
  font-style: italic;
}

.modal-actions {
  margin-top: 40px;
  padding-top: 24px;
  border-top: 1px solid var(--vp-c-divider);
  display: flex;
  justify-content: flex-end;
}

.action-button {
  display: inline-flex;
  align-items: center;
  padding: 10px 24px;
  border-radius: 100px;
  font-weight: 600;
  font-size: 14px;
  text-decoration: none;
  transition: all 0.2s ease;
}

.action-button.primary {
  background: var(--vp-c-brand);
  color: white;
  box-shadow: 0 4px 12px rgba(var(--vp-c-brand-rgb), 0.3);
}

.action-button.primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(var(--vp-c-brand-rgb), 0.4);
}

/* --- Animations --- */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .modal-glass-panel {
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1); /* Spring-like */
}

.modal-fade-leave-active .modal-glass-panel {
  transition: transform 0.3s ease-in;
}

.modal-fade-enter-from .modal-glass-panel {
  transform: scale(0.9) translateY(20px);
}

.modal-fade-leave-to .modal-glass-panel {
  transform: scale(0.95) translateY(10px);
}
</style>
