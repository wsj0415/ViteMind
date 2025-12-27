<script setup>
import { ref, onMounted, computed } from 'vue'
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
const searchQuery = ref('')
const selectedTag = ref('ALL')
const viewMode = ref('grid') // 'grid' | 'timeline'

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

// Computed: Extract all unique tags
const allTags = computed(() => {
  const tags = new Set(['ALL'])
  news.value.forEach(item => {
    if (item.tags) {
      item.tags.forEach(tag => tags.add(tag))
    }
  })
  return Array.from(tags)
})

// Computed: Filter news based on search and tag
const filteredNews = computed(() => {
  return news.value.filter(item => {
    const matchesSearch = (item.title + item.summary).toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesTag = selectedTag.value === 'ALL' || (item.tags && item.tags.includes(selectedTag.value))
    return matchesSearch && matchesTag
  })
})

// Computed: Group filtered news by Month for Timeline
const groupedNews = computed(() => {
  const groups = {}
  filteredNews.value.forEach(item => {
    const date = new Date(item.date)
    const monthKey = date.toLocaleString('en-US', { month: 'short', year: 'numeric' }).toUpperCase() // e.g. DEC 2025
    if (!groups[monthKey]) {
      groups[monthKey] = []
    }
    groups[monthKey].push(item)
  })
  return groups
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
    <!-- Control Bar (Swiss Style) -->
    <div class="control-bar">
      <div class="search-container">
        <span class="search-icon">🔍</span>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="SEARCH INTELLIGENCE..." 
          class="search-input"
        />
      </div>
      
      <div class="filter-row">
        <div class="filter-tags">
          <button 
            v-for="tag in allTags" 
            :key="tag"
            class="filter-tag"
            :class="{ active: selectedTag === tag }"
            @click="selectedTag = tag"
          >
            {{ tag }}
          </button>
        </div>

        <!-- View Toggle -->
        <div class="view-toggle">
          <button 
            class="toggle-btn" 
            :class="{ active: viewMode === 'grid' }"
            @click="viewMode = 'grid'"
          >
            GRID
          </button>
          <span class="toggle-sep">/</span>
          <button 
            class="toggle-btn" 
            :class="{ active: viewMode === 'timeline' }"
            @click="viewMode = 'timeline'"
          >
            TIMELINE
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="status-msg">LOADING DATA...</div>
    
    <div v-else-if="filteredNews.length === 0" class="status-msg">NO MATCHING INTELLIGENCE FOUND</div>

    <!-- Grid View -->
    <div v-else-if="viewMode === 'grid'" class="grid-container">
      <div 
        v-for="item in filteredNews" 
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

    <!-- Timeline View -->
    <div v-else class="timeline-container">
      <div v-for="(items, month) in groupedNews" :key="month" class="timeline-group">
        <div class="timeline-month">{{ month }}</div>
        <div class="timeline-list">
          <div 
            v-for="item in items" 
            :key="item.id" 
            class="timeline-item"
            @click="openNews(item)"
          >
            <div class="tl-date">{{ item.date.split('-')[2] }}</div> <!-- Day only -->
            <div class="tl-content">
              <div class="tl-header">
                <span class="tl-title">{{ item.title }}</span>
                <div class="tl-tags">
                  <span v-for="tag in item.tags" :key="tag" class="tl-tag">#{{ tag }}</span>
                </div>
              </div>
              <p class="tl-summary">{{ item.summary }}</p>
            </div>
          </div>
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

/* --- Control Bar --- */
.control-bar {
  margin: 80px 0 50px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
}

.search-container {
  position: relative;
  width: 100%;
  max-width: 640px;
}

.search-icon {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
  opacity: 0.4;
}

.search-input {
  width: 100%;
  padding: 18px 18px 18px 54px;
  font-family: monospace;
  font-size: 16px;
  border: 2px solid var(--vp-c-text-1);
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  outline: none;
  transition: all 0.2s;
  border-radius: 0;
}

.search-input:focus {
  box-shadow: 4px 4px 0 var(--vp-c-brand);
  transform: translateY(-2px);
}

.filter-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  width: 100%;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: center;
}

.filter-tag {
  font-family: monospace;
  font-size: 12px;
  text-transform: uppercase;
  padding: 6px 12px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--vp-c-text-2);
  cursor: pointer;
  transition: all 0.2s;
}

.filter-tag:hover {
  color: var(--vp-c-text-1);
  text-decoration: underline;
}

.filter-tag.active {
  background: var(--vp-c-text-1);
  color: var(--vp-c-bg);
  border-color: var(--vp-c-text-1);
  font-weight: 700;
}

.filter-tag.active:hover {
  text-decoration: none;
}

/* --- View Toggle --- */
.view-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: monospace;
  font-size: 14px;
  border-top: 1px solid var(--vp-c-divider);
  padding-top: 24px;
  width: 100%;
  justify-content: center;
}

.toggle-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--vp-c-text-2);
  padding: 4px 8px;
  transition: all 0.2s;
}

.toggle-btn:hover {
  color: var(--vp-c-text-1);
}

.toggle-btn.active {
  color: var(--vp-c-text-1);
  font-weight: 700;
  text-decoration: underline;
  text-underline-offset: 4px;
}

.toggle-sep {
  color: var(--vp-c-divider);
}

.status-msg {
  font-family: monospace;
  text-align: center;
  padding: 40px;
  font-size: 14px;
  letter-spacing: 1px;
  border: 1px dashed var(--vp-c-divider);
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

/* --- Timeline System --- */
.timeline-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px 0;
}

.timeline-group {
  margin-bottom: 60px;
}

.timeline-month {
  font-family: monospace;
  font-size: 14px;
  font-weight: 700;
  color: var(--vp-c-text-2);
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--vp-c-text-1);
  letter-spacing: 0.1em;
}

.timeline-item {
  display: flex;
  gap: 24px;
  padding: 24px 0;
  border-bottom: 1px solid var(--vp-c-divider);
  cursor: pointer;
  transition: transform 0.2s;
}

.timeline-item:hover {
  transform: translateX(10px);
}

.tl-date {
  font-family: monospace;
  font-size: 24px;
  font-weight: 700;
  color: var(--vp-c-text-1);
  min-width: 40px;
  text-align: right;
  line-height: 1;
}

.tl-content {
  flex: 1;
}

.tl-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}

.tl-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.tl-tags {
  display: flex;
  gap: 8px;
}

.tl-tag {
  font-family: monospace;
  font-size: 10px;
  background: var(--vp-c-bg-soft);
  padding: 2px 6px;
  border-radius: 2px;
  color: var(--vp-c-text-2);
}

.tl-summary {
  font-size: 14px;
  color: var(--vp-c-text-2);
  line-height: 1.5;
  margin: 0;
}

/* --- Typography & Layout (Grid) --- */
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
