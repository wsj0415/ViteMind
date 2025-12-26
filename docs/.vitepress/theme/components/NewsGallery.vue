<script setup>
import { ref, onMounted } from 'vue'
import { withBase } from 'vitepress'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt()
const news = ref([])
const selectedNews = ref(null)
const loading = ref(true)

// 预定义一组好看的渐变色
const gradients = [
  'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  'linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%, #fecfef 100%)',
  'linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%)',
  'linear-gradient(120deg, #fccb90 0%, #d57eeb 100%)',
  'linear-gradient(120deg, #e0c3fc 0%, #8ec5fc 100%)',
  'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
]

const getRandomGradient = (id) => {
  // 根据 ID 确定性地选择颜色，避免刷新变色
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
  document.body.style.overflow = 'hidden' // 禁止背景滚动
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
  <div class="news-gallery">
    <div v-if="loading" class="loading">正在加载情报...</div>
    
    <div v-else-if="news.length === 0" class="empty">
      暂无情报，请等待下次更新。
    </div>

    <div v-else class="grid">
      <div 
        v-for="item in news" 
        :key="item.id" 
        class="card"
        @click="openNews(item)"
      >
        <div class="card-bg" :style="{ background: getRandomGradient(item.id) }"></div>
        <div class="card-content">
          <div class="card-header">
            <span class="date">{{ item.date }}</span>
            <div class="tags">
              <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </div>
          <h3 class="title">{{ item.title }}</h3>
          <p class="summary">{{ item.summary }}</p>
        </div>
      </div>
    </div>

    <!-- Modal -->
    <Transition name="modal">
      <div v-if="selectedNews" class="modal-mask" @click="closeNews">
        <div class="modal-container" @click.stop>
          <div class="modal-header">
            <h3>{{ selectedNews.title }}</h3>
            <button class="close-btn" @click="closeNews">×</button>
          </div>
          <div class="modal-body" v-html="renderMarkdown(selectedNews.detail)"></div>
          <div class="modal-footer">
            <a :href="selectedNews.link" target="_blank" class="source-link">阅读原文 ↗</a>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.news-gallery {
  padding: 20px 0;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.card {
  position: relative;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  background: var(--vp-c-bg-soft);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  height: 320px;
  display: flex;
  flex-direction: column;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.1);
}

.card-bg {
  height: 120px;
  width: 100%;
}

.card-content {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 12px;
}

.date {
  color: var(--vp-c-text-2);
}

.tag {
  background: var(--vp-c-bg-mute);
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: 4px;
}

.title {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 10px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.summary {
  font-size: 14px;
  color: var(--vp-c-text-2);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Modal Styles */
.modal-mask {
  position: fixed;
  z-index: 9998;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(4px);
}

.modal-container {
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  background: var(--vp-c-bg);
  border-radius: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.33);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--vp-c-divider);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
}

.close-btn {
  font-size: 24px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--vp-c-text-2);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  line-height: 1.8;
  font-size: 16px;
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--vp-c-divider);
  text-align: right;
}

.source-link {
  display: inline-block;
  padding: 8px 16px;
  background: var(--vp-c-brand);
  color: white;
  border-radius: 20px;
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.2s;
}

.source-link:hover {
  opacity: 0.9;
}

/* Transitions */
.modal-enter-from, .modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-container,
.modal-leave-to .modal-container {
  transform: scale(0.95);
}
</style>
