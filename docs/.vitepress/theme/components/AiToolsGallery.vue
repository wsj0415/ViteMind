<script setup>
import { ref, computed, onMounted } from 'vue'
import { createClient } from '@supabase/supabase-js'
import SubmitToolModal from './SubmitToolModal.vue'

// Supabase Client
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY
const supabase = createClient(supabaseUrl, supabaseKey)

const tools = ref([])
const pendingTools = ref([])
const loading = ref(true)
const categories = ['ALL', 'Coding', 'Image', 'Video', 'Writing', 'Audio', 'Productivity']
const selectedCategory = ref('ALL')
const searchQuery = ref('')
const isModalOpen = ref(false)
const showPending = ref(false)

// Get favicon URL from website link
const getFavicon = (url) => {
  try {
    const domain = new URL(url).hostname
    return `https://www.google.com/s2/favicons?domain=${domain}&sz=128`
  } catch {
    return null
  }
}

// Load pending submissions from localStorage
const loadPendingSubmissions = () => {
  try {
    const stored = localStorage.getItem('vitemind_user_submissions')
    if (stored) {
      pendingTools.value = JSON.parse(stored)
    }
  } catch (e) {
    console.error('Error loading pending submissions:', e)
  }
}

// Handle new submission
const handleSubmission = (tool) => {
  pendingTools.value.unshift(tool)
  localStorage.setItem('vitemind_user_submissions', JSON.stringify(pendingTools.value))
}

// Fetch approved tools from Supabase
onMounted(async () => {
  loadPendingSubmissions()
  
  try {
    loading.value = true
    const { data, error } = await supabase
      .from('ai_tools')
      .select('*')
      .eq('approved', true)
      .order('submitted_at', { ascending: false })

    if (error) throw error

    if (data) {
      tools.value = data.map(item => ({
        category: item.category || 'Productivity',
        name: item.name,
        desc: item.description,
        link: item.link,
        tags: item.tags || []
      }))
    }
  } catch (e) {
    console.error('Error fetching tools:', e)
  } finally {
    loading.value = false
  }
})

const filteredTools = computed(() => {
  return tools.value.filter(t => {
    const matchesCat = selectedCategory.value === 'ALL' || t.category === selectedCategory.value
    const matchesSearch = t.name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          t.desc.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesCat && matchesSearch
  })
})

const filteredPending = computed(() => {
  return pendingTools.value.filter(t => {
    const matchesCat = selectedCategory.value === 'ALL' || t.category === selectedCategory.value
    const matchesSearch = t.name.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          t.desc?.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesCat && matchesSearch
  })
})
</script>

<template>
  <div class="tools-page">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>Categories</h2>
      </div>
      <nav class="category-nav">
        <button 
          v-for="cat in categories" 
          :key="cat"
          class="cat-item"
          :class="{ active: selectedCategory === cat }"
          @click="selectedCategory = cat"
        >
          <span class="cat-icon">
            {{ cat === 'ALL' ? '🌐' : cat === 'Coding' ? '💻' : cat === 'Image' ? '🎨' : cat === 'Video' ? '🎬' : cat === 'Writing' ? '✍️' : cat === 'Audio' ? '🎵' : '⚡' }}
          </span>
          <span class="cat-name">{{ cat }}</span>
        </button>
      </nav>
      
      <!-- Pending Toggle -->
      <div v-if="pendingTools.length > 0" class="pending-toggle">
        <button 
          class="pending-btn"
          :class="{ active: showPending }"
          @click="showPending = !showPending"
        >
          <span>🕐</span>
          <span>Pending ({{ pendingTools.length }})</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Header -->
      <header class="content-header">
        <div class="search-container">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search AI tools..." 
            class="search-input"
          />
        </div>
        <button class="submit-btn" @click="isModalOpen = true">
          <span>+</span> Submit Tool
        </button>
      </header>

      <!-- Pending Submissions Section -->
      <section v-if="showPending && filteredPending.length > 0" class="pending-section">
        <h3 class="section-title">
          <span class="pending-badge">Pending Review</span>
        </h3>
        <div class="tools-grid">
          <a 
            v-for="tool in filteredPending" 
            :key="tool.link"
            :href="tool.link" 
            target="_blank"
            class="tool-card pending"
          >
            <div class="card-header">
              <img 
                :src="getFavicon(tool.link)" 
                class="tool-favicon"
                @error="$event.target.style.display='none'"
              />
              <span class="tool-arrow">↗</span>
            </div>
            <div class="card-body">
              <h4 class="tool-name">{{ tool.name }}</h4>
              <p class="tool-desc">{{ tool.desc || tool.description }}</p>
            </div>
            <div class="card-footer">
              <span class="tool-category">{{ tool.category }}</span>
            </div>
          </a>
        </div>
      </section>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading AI Tools...</p>
      </div>

      <!-- Tools Grid -->
      <section v-else class="tools-section">
        <div class="tools-grid">
          <a 
            v-for="tool in filteredTools" 
            :key="tool.name" 
            :href="tool.link" 
            target="_blank"
            class="tool-card"
          >
            <div class="card-header">
              <img 
                :src="getFavicon(tool.link)" 
                class="tool-favicon"
                @error="$event.target.style.display='none'"
              />
              <span class="tool-arrow">↗</span>
            </div>
            <div class="card-body">
              <h4 class="tool-name">{{ tool.name }}</h4>
              <p class="tool-desc">{{ tool.desc }}</p>
            </div>
            <div class="card-footer">
              <span class="tool-category">{{ tool.category }}</span>
              <div class="tool-tags">
                <span v-for="tag in tool.tags?.slice(0, 2)" :key="tag" class="tag">{{ tag }}</span>
              </div>
            </div>
          </a>
        </div>

        <div v-if="filteredTools.length === 0 && !loading" class="no-results">
          <p>No tools found matching your criteria.</p>
        </div>
      </section>
    </main>

    <!-- Submission Modal -->
    <SubmitToolModal 
      :is-open="isModalOpen" 
      :categories="categories.filter(c => c !== 'ALL')"
      @close="isModalOpen = false"
      @submit="handleSubmission"
    />
  </div>
</template>

<style scoped>
.tools-page {
  display: flex;
  min-height: calc(100vh - 64px);
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Sidebar */
.sidebar {
  width: 240px;
  padding: 24px 16px;
  border-right: 1px solid var(--vp-c-divider);
  position: sticky;
  top: 64px;
  height: calc(100vh - 64px);
  overflow-y: auto;
  background: var(--vp-c-bg);
}

.sidebar-header h2 {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--vp-c-text-3);
  margin: 0 0 16px 12px;
}

.category-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.cat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border: none;
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  color: var(--vp-c-text-2);
  font-size: 14px;
  font-weight: 500;
  transition: all 0.15s ease;
  text-align: left;
}

.cat-item:hover {
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
}

.cat-item.active {
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand);
}

.cat-icon {
  font-size: 18px;
}

.pending-toggle {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--vp-c-divider);
}

.pending-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 10px 12px;
  border: 1px dashed var(--vp-c-divider);
  background: transparent;
  border-radius: 8px;
  cursor: pointer;
  color: var(--vp-c-text-2);
  font-size: 13px;
  transition: all 0.15s ease;
}

.pending-btn:hover,
.pending-btn.active {
  border-color: var(--vp-c-brand);
  color: var(--vp-c-brand);
  background: var(--vp-c-brand-soft);
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 24px 32px;
  max-width: calc(100% - 240px);
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
  gap: 16px;
}

.search-container {
  flex: 1;
  max-width: 480px;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  font-size: 14px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--vp-c-brand);
  box-shadow: 0 0 0 3px var(--vp-c-brand-soft);
}

.search-input::placeholder {
  color: var(--vp-c-text-3);
}

.submit-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 12px 20px;
  font-size: 14px;
  font-weight: 600;
  color: white;
  background: var(--vp-c-brand);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.submit-btn:hover {
  background: var(--vp-c-brand-dark);
  transform: translateY(-1px);
}

/* Sections */
.pending-section {
  margin-bottom: 40px;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 14px;
}

.pending-badge {
  display: inline-block;
  padding: 4px 12px;
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: white;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

/* Tools Grid */
.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.tool-card {
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 16px;
  padding: 20px;
  text-decoration: none;
  color: var(--vp-c-text-1);
  transition: all 0.2s ease;
  display: flex;
  flex-direction: column;
  min-height: 180px;
}

.tool-card:hover {
  border-color: var(--vp-c-brand);
  transform: translateY(-4px);
  box-shadow: 0 12px 32px -8px rgba(0, 0, 0, 0.1);
}

.tool-card.pending {
  border-style: dashed;
  opacity: 0.8;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.tool-favicon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--vp-c-bg-soft);
  object-fit: contain;
  padding: 4px;
}

.tool-arrow {
  font-size: 16px;
  color: var(--vp-c-text-3);
  opacity: 0;
  transition: all 0.2s ease;
}

.tool-card:hover .tool-arrow {
  opacity: 1;
  color: var(--vp-c-brand);
}

.card-body {
  flex: 1;
}

.tool-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--vp-c-text-1);
}

.tool-desc {
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
  color: var(--vp-c-text-2);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--vp-c-divider);
}

.tool-category {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--vp-c-text-3);
}

.tool-tags {
  display: flex;
  gap: 6px;
}

.tag {
  padding: 2px 8px;
  font-size: 11px;
  background: var(--vp-c-bg-soft);
  border-radius: 4px;
  color: var(--vp-c-text-2);
}

/* Loading & Empty States */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: var(--vp-c-text-2);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--vp-c-divider);
  border-top-color: var(--vp-c-brand);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.no-results {
  text-align: center;
  padding: 60px 0;
  color: var(--vp-c-text-3);
}

/* Responsive */
@media (max-width: 768px) {
  .tools-page {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: auto;
    position: static;
    border-right: none;
    border-bottom: 1px solid var(--vp-c-divider);
    padding: 16px;
  }
  
  .category-nav {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .cat-item {
    padding: 8px 12px;
  }
  
  .cat-name {
    display: none;
  }
  
  .cat-icon {
    font-size: 20px;
  }
  
  .main-content {
    max-width: 100%;
    padding: 16px;
  }
  
  .content-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-container {
    max-width: 100%;
  }
  
  .submit-btn {
    justify-content: center;
  }
  
  .tools-grid {
    grid-template-columns: 1fr;
  }
}
</style>
