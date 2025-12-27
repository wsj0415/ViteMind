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
  <div class="swiss-gallery">
    <!-- Control Bar (Swiss Style) -->
    <div class="control-bar">
      <div class="search-container">
        <span class="search-icon">🔍</span>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="SEARCH PROMPTS..." 
          class="search-input"
        />
      </div>
      
      <div class="filter-row">
        <div class="filter-tags">
          <button 
            v-for="cat in categories" 
            :key="cat"
            class="filter-tag"
            :class="{ active: selectedCategory === cat }"
            @click="selectedCategory = cat"
          >
            {{ cat }}
          </button>
        </div>

        <!-- Action Buttons -->
        <div class="action-row">
          <button class="action-btn" @click="isModalOpen = true">
            + SUBMIT PROMPT
          </button>
          <button 
            v-if="pendingPrompts.length > 0"
            class="action-btn secondary"
            :class="{ active: showPending }"
            @click="showPending = !showPending"
          >
            PENDING ({{ pendingPrompts.length }})
          </button>
        </div>
      </div>
    </div>

    <!-- Pending Section -->
    <div v-if="showPending && filteredPending.length > 0" class="pending-container">
      <h3 class="section-title">PENDING REVIEW</h3>
      <div class="grid-container">
        <div 
          v-for="prompt in filteredPending" 
          :key="prompt.created_at"
          class="prompt-item pending"
        >
          <div class="item-header">
            <span class="meta-cat">{{ prompt.category }}</span>
            <span class="status-badge">PENDING</span>
          </div>
          <div class="item-body">
            <h3 class="item-title">{{ prompt.title }}</h3>
            <p class="item-summary">{{ prompt.content }}</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="status-msg">LOADING PROMPTS...</div>
    
    <div v-else-if="filteredPrompts.length === 0" class="status-msg">NO MATCHING PROMPTS FOUND</div>

    <!-- Main Grid -->
    <div v-else class="grid-container">
      <div 
        v-for="prompt in filteredPrompts" 
        :key="prompt.id" 
        class="prompt-item"
      >
        <div class="item-header">
          <span class="meta-cat">{{ prompt.category }}</span>
          <button class="copy-icon" @click="copyToClipboard(prompt.content)" title="Copy">
            📋
          </button>
        </div>
        
        <div class="item-body">
          <h3 class="item-title">{{ prompt.title }}</h3>
          <p class="item-summary">{{ prompt.content }}</p>
        </div>

        <div class="item-footer">
          <div class="meta-tags">
            <span v-for="tag in prompt.tags?.slice(0, 3)" :key="tag" class="meta-tag">#{{ tag }}</span>
          </div>
          <button class="copy-btn" @click="copyToClipboard(prompt.content)">
            COPY
          </button>
        </div>
      </div>
    </div>

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
/* --- Swiss Style Variables (Matching NewsGallery) --- */
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

.action-row {
  display: flex;
  gap: 16px;
  margin-top: 16px;
}

.action-btn {
  font-family: monospace;
  font-size: 12px;
  font-weight: 700;
  padding: 8px 16px;
  background: var(--vp-c-brand);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.action-btn.secondary {
  background: transparent;
  border: 1px solid var(--vp-c-divider);
  color: var(--vp-c-text-2);
}

.action-btn.secondary:hover,
.action-btn.secondary.active {
  border-color: var(--vp-c-brand);
  color: var(--vp-c-brand);
}

.status-msg {
  font-family: monospace;
  text-align: center;
  padding: 40px;
  font-size: 14px;
  letter-spacing: 1px;
  border: 1px dashed var(--vp-c-divider);
}

.section-title {
  font-family: monospace;
  font-size: 14px;
  font-weight: 700;
  margin: 40px 0 20px;
  text-align: center;
  color: var(--vp-c-text-2);
}

/* --- Grid System --- */
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  border-top: 1px solid var(--vp-c-divider);
  border-left: 1px solid var(--vp-c-divider);
}

.prompt-item {
  border-right: 1px solid var(--vp-c-divider);
  border-bottom: 1px solid var(--vp-c-divider);
  padding: 32px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 320px;
  transition: background-color 0.2s ease;
  background: var(--vp-c-bg);
}

.prompt-item:hover {
  background-color: var(--vp-c-bg-soft);
}

.prompt-item.pending {
  border-style: dashed;
  opacity: 0.8;
}

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

.meta-cat {
  text-transform: uppercase;
  font-weight: 700;
  color: var(--vp-c-brand);
}

.copy-icon {
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.copy-icon:hover {
  opacity: 1;
}

.item-title {
  font-size: 20px;
  font-weight: 700;
  line-height: 1.3;
  margin: 0 0 16px 0;
  letter-spacing: -0.02em;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-summary {
  font-size: 14px;
  line-height: 1.6;
  color: var(--vp-c-text-2);
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-family: monospace;
  white-space: pre-wrap;
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

.meta-tags {
  display: flex;
  gap: 8px;
}

.meta-tag {
  color: var(--vp-c-text-3);
}

.copy-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--vp-c-text-1);
  font-weight: 700;
  font-family: monospace;
  transition: color 0.2s;
}

.copy-btn:hover {
  color: var(--vp-c-brand);
  text-decoration: underline;
}

/* Mobile Responsiveness */
@media (max-width: 768px) {
  .grid-container {
    border-left: none;
    border-right: none;
  }
  
  .prompt-item {
    border-right: none;
    height: auto;
    min-height: 280px;
  }
}
</style>
