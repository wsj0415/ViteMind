<script setup>
import { ref, computed, onMounted } from 'vue'
import { createClient } from '@supabase/supabase-js'
import SubmitToolModal from './SubmitToolModal.vue'

// Supabase Client
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseKey = import.meta.env.VITE_SUPABASE_KEY
const supabase = createClient(supabaseUrl, supabaseKey)

const tools = ref([])
const loading = ref(true)
const categories = ['ALL', 'Coding', 'Image', 'Video', 'Writing', 'Audio', 'Productivity']
const selectedCategory = ref('ALL')
const searchQuery = ref('')
const isModalOpen = ref(false)

// Fetch approved tools from Supabase
onMounted(async () => {
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
        icon: item.icon || '🚀', // Use DB icon or default
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
</script>

<template>
  <div class="tools-gallery">
    <!-- Search & Filter Bar -->
    <div class="control-bar">
      <div class="search-wrapper">
        <span class="search-icon">🔍</span>
        <input 
          v-model="searchQuery" 
          type="text" 
          placeholder="SEARCH TOOLS..." 
          class="search-input"
        />
      </div>

      <div class="category-filter">
        <button 
          v-for="cat in categories" 
          :key="cat"
          class="cat-btn"
          :class="{ active: selectedCategory === cat }"
          @click="selectedCategory = cat"
        >
          {{ cat }}
        </button>
      </div>

      <!-- Submit Button -->
      <button class="submit-trigger" @click="isModalOpen = true">
        + SUBMIT TOOL
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading AI Tools...</p>
    </div>

    <!-- Grid -->
    <div v-else class="tools-grid">
      <a 
        v-for="tool in filteredTools" 
        :key="tool.name" 
        :href="tool.link" 
        target="_blank"
        class="tool-card"
      >
        <div class="card-top">
          <div class="tool-icon">{{ tool.icon }}</div>
          <div class="tool-arrow">↗</div>
        </div>
        
        <div class="card-content">
          <h3 class="tool-name">{{ tool.name }}</h3>
          <p class="tool-desc">{{ tool.desc }}</p>
        </div>

        <div class="card-footer">
          <span class="tool-cat">{{ tool.category }}</span>
          <div class="tool-tags">
            <span v-for="tag in tool.tags" :key="tag" class="mini-tag">{{ tag }}</span>
          </div>
        </div>
      </a>
    </div>

    <div v-if="filteredTools.length === 0" class="no-results">
      NO TOOLS FOUND
    </div>

    <!-- Submission Modal -->
    <SubmitToolModal 
      :is-open="isModalOpen" 
      :categories="categories.filter(c => c !== 'ALL')"
      @close="isModalOpen = false"
    />
  </div>
</template>

<style scoped>
.tools-gallery {
  padding: 20px 0 60px;
  font-family: "Inter", sans-serif;
  color: var(--vp-c-text-1);
}

/* Controls */
.control-bar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
  margin-bottom: 60px;
}

.search-wrapper {
  position: relative;
  width: 100%;
  max-width: 500px;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.5;
}

.search-input {
  width: 100%;
  padding: 14px 14px 14px 44px;
  font-family: monospace;
  font-size: 14px;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg-alt);
  color: var(--vp-c-text-1);
  border-radius: 8px;
  transition: all 0.2s;
}

.search-input:focus {
  border-color: var(--vp-c-brand);
  box-shadow: 0 0 0 2px var(--vp-c-brand-dimm);
  outline: none;
}

.category-filter {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
}

.cat-btn {
  background: transparent;
  border: 1px solid transparent;
  padding: 6px 16px;
  font-size: 13px;
  font-weight: 500;
  border-radius: 20px;
  cursor: pointer;
  color: var(--vp-c-text-2);
  transition: all 0.2s;
  background: var(--vp-c-bg-alt);
}

.cat-btn:hover {
  color: var(--vp-c-text-1);
  background: var(--vp-c-bg-mute);
}

.cat-btn.active {
  background: var(--vp-c-text-1);
  color: var(--vp-c-bg);
  font-weight: 600;
}

.submit-trigger {
  font-family: monospace;
  font-size: 12px;
  font-weight: 700;
  color: var(--vp-c-brand);
  background: transparent;
  border: 1px dashed var(--vp-c-brand);
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.submit-trigger:hover {
  background: var(--vp-c-brand);
  color: white;
  border-style: solid;
}

/* Grid */
.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.tool-card {
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  text-decoration: none !important;
  color: var(--vp-c-text-1) !important;
  transition: all 0.2s ease;
  height: 220px;
}

.tool-card:hover {
  transform: translateY(-4px);
  border-color: var(--vp-c-brand);
  box-shadow: 0 8px 24px rgba(0,0,0,0.05);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.tool-icon {
  font-size: 36px;
  background: var(--vp-c-bg-alt);
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.tool-arrow {
  font-size: 14px;
  opacity: 0.3;
  transition: opacity 0.2s;
}

.tool-card:hover .tool-arrow {
  opacity: 1;
  color: var(--vp-c-brand);
}

.card-content {
  flex: 1;
}

.tool-name {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 6px 0;
}

.tool-desc {
  font-size: 13px;
  color: var(--vp-c-text-2);
  line-height: 1.4;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11px;
}

.tool-cat {
  font-weight: 600;
  text-transform: uppercase;
  color: var(--vp-c-text-3);
  letter-spacing: 0.5px;
}

.tool-tags {
  display: flex;
  gap: 6px;
}

.mini-tag {
  background: var(--vp-c-bg-alt);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--vp-c-text-2);
}

.no-results {
  text-align: center;
  padding: 60px;
  color: var(--vp-c-text-3);
  font-family: monospace;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
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
</style>
