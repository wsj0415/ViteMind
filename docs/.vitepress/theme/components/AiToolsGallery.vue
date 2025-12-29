<script setup>
import { ref, computed, onMounted } from 'vue'
import { createClient } from '@supabase/supabase-js'
import SubmitToolModal from './SubmitToolModal.vue'
import BaseIcon from './BaseIcon.vue'

// Supabase Client (lazy initialization for SSR compatibility)
const supabaseUrl = import.meta.env.SUPABASE_URL
const supabaseKey = import.meta.env.SUPABASE_KEY
let supabase = null

const tools = ref([])
const pendingTools = ref([])
const loading = ref(true)
const categories = ['ALL', 'Coding', 'Image', 'Video', 'Writing', 'Audio', 'Productivity']
const selectedCategory = ref('ALL')
const searchQuery = ref('')
const isModalOpen = ref(false)
const showPending = ref(false)
const showBackToTop = ref(false)
const sortBy = ref('default') // 'default' | 'name-asc' | 'name-desc'

// Compute popular tags
const popularTags = computed(() => {
  const tagCounts = {}
  tools.value.forEach(tool => {
    if (tool.tags) {
      tool.tags.forEach(tag => {
        tagCounts[tag] = (tagCounts[tag] || 0) + 1
      })
    }
  })

  return Object.entries(tagCounts)
    .sort((a, b) => b[1] - a[1]) // Sort by count desc
    .slice(0, 10) // Top 10
    .map(([tag]) => tag)
})

// Scroll event handler for back to top button
const handleScroll = () => {
  if (typeof window !== 'undefined') {
    showBackToTop.value = window.scrollY > 300
  }
}

// Scroll to top function
const scrollToTop = () => {
  if (typeof window !== 'undefined') {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// Clear search
const clearSearch = () => {
  searchQuery.value = ''
}

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
  
  // Only run client-side code
  if (typeof window === 'undefined') {
    loading.value = false
    return
  }
  
  window.addEventListener('scroll', handleScroll)
  
  // Initialize Supabase client on client side
  if (supabaseUrl && supabaseKey) {
    supabase = createClient(supabaseUrl, supabaseKey)
  }
  
  // Only fetch if supabase is initialized
  if (!supabase) {
    loading.value = false
    return
  }
  
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

      // Cleanup pending tools that have been approved
      if (pendingTools.value.length > 0) {
        const approvedLinks = new Set(tools.value.map(t => t.link))
        const initialCount = pendingTools.value.length

        pendingTools.value = pendingTools.value.filter(t => !approvedLinks.has(t.link))

        if (pendingTools.value.length < initialCount) {
          localStorage.setItem('vitemind_user_submissions', JSON.stringify(pendingTools.value))
        }
      }
    }
  } catch (e) {
    console.error('Error fetching tools:', e)
  } finally {
    loading.value = false
  }
})

const filteredTools = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  let result = tools.value.filter(t => {
    const matchesCat = selectedCategory.value === 'ALL' || t.category === selectedCategory.value
    const matchesSearch = !query || 
                          t.name?.toLowerCase().includes(query) || 
                          t.desc?.toLowerCase().includes(query)
    return matchesCat && matchesSearch
  })
  
  // Apply sorting
  if (sortBy.value === 'name-asc') {
    result = [...result].sort((a, b) => a.name.localeCompare(b.name))
  } else if (sortBy.value === 'name-desc') {
    result = [...result].sort((a, b) => b.name.localeCompare(a.name))
  }
  
  return result
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
          <BaseIcon :name="cat" :size="20" class="cat-icon" />
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
          <BaseIcon name="Pending" :size="16" />
          <span>Pending ({{ pendingTools.length }})</span>
        </button>
      </div>

      <!-- Popular Tags -->
      <div v-if="popularTags.length > 0" class="sidebar-section">
        <div class="sidebar-header">
          <h2>Popular Tags</h2>
        </div>
        <div class="tags-cloud">
          <button
            v-for="tag in popularTags"
            :key="tag"
            class="tag-chip"
            @click="searchQuery = tag"
          >
            #{{ tag }}
          </button>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Header -->
      <header class="content-header">
        <div class="search-wrapper">
          <div class="search-container">
            <BaseIcon name="Search" :size="16" class="search-icon" />
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search AI tools..." 
              class="search-input"
            />
            <button 
              v-if="searchQuery" 
              class="clear-btn" 
              @click="clearSearch"
            >
              <BaseIcon name="Close" :size="12" />
            </button>
          </div>
          <span class="tools-count">找到 {{ filteredTools.length }} 个工具</span>
        </div>
        <div class="header-actions">
          <select v-model="sortBy" class="sort-select">
            <option value="default">默认排序</option>
            <option value="name-asc">名称 A-Z</option>
            <option value="name-desc">名称 Z-A</option>
          </select>
          <button class="submit-btn" @click="isModalOpen = true">
            <BaseIcon name="Plus" :size="16" /> Submit Tool
          </button>
        </div>
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
              <div class="favicon-wrapper">
                <img
                  :src="getFavicon(tool.link)"
                  class="tool-favicon"
                  width="48"
                  height="48"
                  loading="lazy"
                  @error="$event.target.style.opacity='0'"
                />
              </div>
              <BaseIcon name="ArrowUpRight" :size="16" class="tool-arrow" />
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
                <span v-for="tag in tool.tags?.slice(0, 3)" :key="tag" class="tag">{{ tag }}</span>
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

    <!-- Back to Top Button -->
    <Transition name="fade">
      <button 
        v-if="showBackToTop" 
        class="back-to-top" 
        @click="scrollToTop"
        aria-label="回到顶部"
      >
        ↑
      </button>
    </Transition>
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
  white-space: nowrap; /* Prevent wrapping in horizontal mode */
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

.sidebar-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--vp-c-divider);
}

.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 0 12px;
}

.tag-chip {
  font-size: 11px;
  padding: 4px 10px;
  background: var(--vp-c-bg-soft);
  border: 1px solid transparent;
  border-radius: 12px;
  color: var(--vp-c-text-2);
  cursor: pointer;
  transition: all 0.2s ease;
}

.tag-chip:hover {
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand);
  border-color: var(--vp-c-brand-light);
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

.search-wrapper {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.search-container {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  max-width: 480px;
  padding: 0 16px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  background: var(--vp-c-bg-soft);
  transition: all 0.2s ease;
}

.search-container:focus-within {
  border-color: var(--vp-c-brand);
  box-shadow: 0 0 0 3px var(--vp-c-brand-soft);
}

.search-icon {
  font-size: 14px;
  opacity: 0.6;
}

.tools-count {
  font-size: 12px;
  color: var(--vp-c-text-3);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.sort-select {
  padding: 10px 16px;
  font-size: 14px;
  border: 1px solid var(--vp-c-divider);
  border-radius: 10px;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
  cursor: pointer;
  transition: all 0.2s ease;
}

.sort-select:hover {
  border-color: var(--vp-c-brand);
}

.clear-btn {
  padding: 4px 8px;
  font-size: 12px;
  background: transparent;
  border: none;
  color: var(--vp-c-text-3);
  cursor: pointer;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  color: var(--vp-c-brand);
}

.search-input {
  flex: 1;
  padding: 12px 0;
  font-size: 14px;
  border: none;
  background: transparent;
  color: var(--vp-c-text-1);
  outline: none;
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
  background: linear-gradient(135deg, var(--vp-c-bg) 0%, var(--vp-c-bg-soft) 100%);
  border: 1px solid var(--vp-c-divider);
  border-radius: 16px;
  padding: 20px;
  text-decoration: none;
  color: var(--vp-c-text-1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  flex-direction: column;
  min-height: 180px;
  position: relative;
  overflow: hidden;
  animation: fadeInUp 0.4s ease forwards;
}

.tool-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(139,92,246,0.08), transparent);
  transition: left 0.6s ease;
  pointer-events: none;
}

.tool-card:hover::before {
  left: 100%;
}

.tool-card:hover {
  border-color: var(--vp-c-brand);
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 20px 40px -12px rgba(139, 92, 246, 0.25);
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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

.favicon-wrapper {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--vp-c-bg-soft);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}

.tool-favicon {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 4px;
  transition: opacity 0.2s ease;
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
  line-clamp: 2;
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
    position: sticky; /* Keep it sticky on mobile too if desired, or static */
    top: 64px;
    z-index: 10;
    border-right: none;
    border-bottom: 1px solid var(--vp-c-divider);
    padding: 12px 16px;
    background: var(--vp-c-bg);
  }
  
  .sidebar-header {
    display: none; /* Hide header on mobile to save space */
  }

  .category-nav {
    flex-direction: row;
    flex-wrap: nowrap; /* Prevent wrapping */
    gap: 12px;
    overflow-x: auto; /* Horizontal scroll */
    padding-bottom: 4px; /* Space for scrollbar if any */
    scroll-snap-type: x mandatory;
    -webkit-overflow-scrolling: touch;
    /* Hide scrollbar */
    scrollbar-width: none;
    -ms-overflow-style: none;
  }

  .category-nav::-webkit-scrollbar {
    display: none;
  }
  
  .cat-item {
    padding: 8px 16px;
    flex-shrink: 0; /* Prevent shrinking */
    scroll-snap-align: start;
    background: var(--vp-c-bg-soft); /* Adding background to make them look like chips */
    border-radius: 20px;
  }
  
  .cat-item.active {
    background: var(--vp-c-brand);
    color: white;
  }

  .cat-name {
    display: inline-block; /* Show name again */
    font-size: 13px;
  }
  
  .cat-icon {
    font-size: 16px;
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

  .header-actions {
    flex-direction: column;
    width: 100%;
  }

  .sort-select {
    width: 100%;
  }
}

/* Back to Top Button */
.back-to-top {
  position: fixed;
  bottom: 32px;
  right: 32px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--vp-c-brand), var(--vp-c-brand-dark));
  color: white;
  border: none;
  font-size: 20px;
  font-weight: bold;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4);
  transition: all 0.3s ease;
  z-index: 100;
}

.back-to-top:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(139, 92, 246, 0.5);
}

/* Fade Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
