<script setup>
import { ref, computed, onMounted } from 'vue'
import { createClient } from '@supabase/supabase-js'
import SubmitPromptModal from './SubmitPromptModal.vue'

// Supabase Client
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY
const supabase = createClient(supabaseUrl, supabaseKey)

const prompts = ref([])
const pendingPrompts = ref([])
const loading = ref(true)
const categories = ['ALL', 'Coding', 'Image', 'Writing', 'Marketing', 'SEO', 'Productivity']
const selectedCategory = ref('ALL')
const searchQuery = ref('')
const isModalOpen = ref(false)
const showPending = ref(false)

// Load pending submissions from localStorage
const loadPendingSubmissions = () => {
  try {
    const stored = localStorage.getItem('vitemind_user_prompts')
    if (stored) {
      pendingPrompts.value = JSON.parse(stored)
    }
  } catch (e) {
    console.error('Error loading pending prompts:', e)
  }
}

// Handle new submission
const handleSubmission = (prompt) => {
  pendingPrompts.value.unshift(prompt)
  localStorage.setItem('vitemind_user_prompts', JSON.stringify(pendingPrompts.value))
}

// Copy to clipboard
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    // Could add a toast here
    alert('Prompt copied to clipboard!')
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

// Fetch approved prompts from Supabase
onMounted(async () => {
  loadPendingSubmissions()
  
  try {
    loading.value = true
    const { data, error } = await supabase
      .from('ai_prompts')
      .select('*')
      .eq('approved', true)
      .order('created_at', { ascending: false })

    if (error) throw error

    if (data) {
      prompts.value = data
    }
  } catch (e) {
    console.error('Error fetching prompts:', e)
  } finally {
    loading.value = false
  }
})

const filteredPrompts = computed(() => {
  return prompts.value.filter(p => {
    const matchesCat = selectedCategory.value === 'ALL' || p.category === selectedCategory.value
    const matchesSearch = p.title.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          p.content.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesCat && matchesSearch
  })
})

const filteredPending = computed(() => {
  return pendingPrompts.value.filter(p => {
    const matchesCat = selectedCategory.value === 'ALL' || p.category === selectedCategory.value
    const matchesSearch = p.title.toLowerCase().includes(searchQuery.value.toLowerCase()) || 
                          p.content.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesCat && matchesSearch
  })
})
</script>

<template>
  <div class="prompts-page">
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
            {{ cat === 'ALL' ? '🌐' : cat === 'Coding' ? '💻' : cat === 'Image' ? '🎨' : cat === 'Writing' ? '✍️' : cat === 'Marketing' ? '📢' : cat === 'SEO' ? '🔍' : '⚡' }}
          </span>
          <span class="cat-name">{{ cat }}</span>
        </button>
      </nav>
      
      <!-- Pending Toggle -->
      <div v-if="pendingPrompts.length > 0" class="pending-toggle">
        <button 
          class="pending-btn"
          :class="{ active: showPending }"
          @click="showPending = !showPending"
        >
          <span>🕐</span>
          <span>Pending ({{ pendingPrompts.length }})</span>
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
            placeholder="Search prompts..." 
            class="search-input"
          />
        </div>
        <button class="submit-btn" @click="isModalOpen = true">
          <span>+</span> Submit Prompt
        </button>
      </header>

      <!-- Pending Submissions Section -->
      <section v-if="showPending && filteredPending.length > 0" class="pending-section">
        <h3 class="section-title">
          <span class="pending-badge">Pending Review</span>
        </h3>
        <div class="masonry-grid">
          <div 
            v-for="prompt in filteredPending" 
            :key="prompt.created_at"
            class="prompt-card pending"
          >
            <div class="card-header">
              <span class="cat-badge">{{ prompt.category }}</span>
            </div>
            <div class="card-body">
              <h4 class="prompt-title">{{ prompt.title }}</h4>
              <p class="prompt-preview">{{ prompt.content }}</p>
            </div>
            <div class="card-footer">
               <span class="status-text">Pending</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Loading State -->
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading Prompts...</p>
      </div>

      <!-- Prompts Grid -->
      <section v-else class="prompts-section">
        <div class="masonry-grid">
          <div 
            v-for="prompt in filteredPrompts" 
            :key="prompt.id" 
            class="prompt-card"
          >
            <div class="card-header">
              <span class="cat-badge">{{ prompt.category }}</span>
              <div class="card-actions">
                 <button class="icon-btn" @click="copyToClipboard(prompt.content)" title="Copy Prompt">
                   📋
                 </button>
              </div>
            </div>
            
            <div class="card-body">
              <h4 class="prompt-title">{{ prompt.title }}</h4>
              <div class="prompt-content-wrapper">
                <p class="prompt-preview">{{ prompt.content }}</p>
                <div class="fade-overlay"></div>
              </div>
            </div>

            <div class="card-footer">
              <div class="prompt-tags">
                <span v-for="tag in prompt.tags?.slice(0, 3)" :key="tag" class="tag">#{{ tag }}</span>
              </div>
              <button class="copy-btn" @click="copyToClipboard(prompt.content)">
                Copy
              </button>
            </div>
          </div>
        </div>

        <div v-if="filteredPrompts.length === 0 && !loading" class="no-results">
          <p>No prompts found matching your criteria.</p>
        </div>
      </section>
    </main>

    <!-- Submission Modal -->
    <SubmitPromptModal 
      :is-open="isModalOpen" 
      :categories="categories.filter(c => c !== 'ALL')"
      @close="isModalOpen = false"
      @submit="handleSubmission"
    />
  </div>
</template>

<style scoped>
.prompts-page {
  display: flex;
  min-height: calc(100vh - 64px);
  font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Sidebar (Reused from AI Tools, could be extracted) */
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

/* Masonry Grid */
.masonry-grid {
  column-count: 3;
  column-gap: 20px;
}

.prompt-card {
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  break-inside: avoid;
  display: flex;
  flex-direction: column;
  transition: all 0.2s ease;
}

.prompt-card:hover {
  border-color: var(--vp-c-brand);
  transform: translateY(-4px);
  box-shadow: 0 12px 32px -8px rgba(0, 0, 0, 0.1);
}

.prompt-card.pending {
  border-style: dashed;
  opacity: 0.8;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.cat-badge {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 4px 8px;
  background: var(--vp-c-bg-soft);
  border-radius: 6px;
  color: var(--vp-c-text-2);
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.icon-btn:hover {
  opacity: 1;
}

.card-body {
  margin-bottom: 16px;
}

.prompt-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--vp-c-text-1);
  line-height: 1.4;
}

.prompt-content-wrapper {
  position: relative;
  max-height: 120px;
  overflow: hidden;
}

.prompt-preview {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--vp-c-text-2);
  font-family: monospace;
  white-space: pre-wrap;
}

.fade-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 40px;
  background: linear-gradient(to bottom, transparent, var(--vp-c-bg));
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--vp-c-divider);
}

.prompt-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  font-size: 10px;
  color: var(--vp-c-text-3);
}

.copy-btn {
  font-size: 12px;
  font-weight: 600;
  color: var(--vp-c-brand);
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.copy-btn:hover {
  background: var(--vp-c-brand-soft);
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
@media (max-width: 1024px) {
  .masonry-grid {
    column-count: 2;
  }
}

@media (max-width: 768px) {
  .prompts-page {
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
  
  .masonry-grid {
    column-count: 1;
  }
}
</style>
