<script setup>
import { ref, computed, onMounted } from 'vue'
import { createClient } from '@supabase/supabase-js'

// Supabase Client
// Lazy initialize in onMounted to support SSG
let supabase = null

const prompts = ref([])
const loading = ref(true)
const categories = ['ALL', 'Coding', 'Image', 'Writing', 'Marketing', 'SEO', 'Productivity']
const selectedCategory = ref('ALL')
const searchQuery = ref('')
const selectedPrompt = ref(null)
const selectedTag = ref('ALL')
const isEditing = ref(false)
const editContent = ref('')

// Copy to clipboard
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    alert('Prompt copied to clipboard!')
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

// Start Edit Mode
const startEdit = () => {
  if (selectedPrompt.value) {
    editContent.value = selectedPrompt.value.content
    isEditing.value = true
  }
}

// Cancel Edit
const cancelEdit = () => {
  isEditing.value = false
  editContent.value = ''
}

// Save Edit
const saveEdit = async () => {
  if (!selectedPrompt.value || !supabase) return

  const newContent = editContent.value
  if (newContent !== selectedPrompt.value.content) {
    try {
      const { error } = await supabase
        .from('ai_prompts')
        .update({
          content: newContent,
          version: (selectedPrompt.value.version || 1) + 1,
          updated_at: new Date().toISOString()
        })
        .eq('id', selectedPrompt.value.id)

      if (error) throw error

      // Update local state
      const index = prompts.value.findIndex(p => p.id === selectedPrompt.value.id)
      if (index !== -1) {
        prompts.value[index].content = newContent
        prompts.value[index].version = (selectedPrompt.value.version || 1) + 1
      }

      // Update selected prompt
      selectedPrompt.value.content = newContent
      selectedPrompt.value.version = (selectedPrompt.value.version || 1) + 1

      alert('Prompt updated successfully!')
      isEditing.value = false
    } catch (e) {
      console.error('Update failed:', e)
      alert('Failed to update prompt.')
    }
  } else {
    isEditing.value = false
  }
}

// Handle Delete
const handleDelete = async (id) => {
  if (!supabase) return
  if (confirm('Are you sure you want to delete this prompt?')) {
    try {
      const { error } = await supabase
        .from('ai_prompts')
        .update({ is_deleted: true })
        .eq('id', id)

      if (error) throw error

      // Remove from local state
      prompts.value = prompts.value.filter(p => p.id !== id)
      alert('Prompt deleted.')
    } catch (e) {
      console.error('Delete failed:', e)
      alert('Failed to delete prompt.')
    }
  }
}

// Fetch approved prompts from Supabase
onMounted(async () => {
  const supabaseUrl = import.meta.env.SUPABASE_URL
  const supabaseKey = import.meta.env.SUPABASE_KEY

  if (supabaseUrl && supabaseKey) {
      supabase = createClient(supabaseUrl, supabaseKey)

      try {
        loading.value = true
        const { data, error } = await supabase
          .from('ai_prompts')
          .select('*')
          .eq('approved', true)
          .eq('is_deleted', false) // Filter out deleted
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
  } else {
      console.warn('Supabase credentials missing')
      loading.value = false
  }
})

// Computed: Extract all unique tags
const allTags = computed(() => {
  const tags = new Set(['ALL'])
  prompts.value.forEach(p => {
    if (p.tags) {
      p.tags.forEach(tag => tags.add(tag))
    }
  })
  return Array.from(tags)
})

const filteredPrompts = computed(() => {
  return prompts.value.filter(p => {
    const matchesCat = selectedCategory.value === 'ALL' || p.category === selectedCategory.value
    const matchesTag = selectedTag.value === 'ALL' || (p.tags && p.tags.includes(selectedTag.value))
    const matchesSearch = p.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
      p.content.toLowerCase().includes(searchQuery.value.toLowerCase())
    return matchesCat && matchesTag && matchesSearch
  })
})

</script>

<template>
  <div class="swiss-gallery">
    <!-- Control Bar (Swiss Style) -->
    <div class="control-bar">
      <div class="search-container">
        <span class="search-icon">🔍</span>
        <input v-model="searchQuery" type="text" placeholder="SEARCH PROMPTS..." class="search-input" />
      </div>

      <div class="filter-row">
        <div class="filter-tags">
          <button v-for="cat in categories" :key="cat" class="filter-tag" :class="{ active: selectedCategory === cat }"
            @click="selectedCategory = cat">
            {{ cat }}
          </button>
        </div>

        <!-- Tag Cloud -->
        <div class="tag-cloud" v-if="allTags.length > 1">
          <button v-for="tag in allTags" :key="tag" class="cloud-tag" :class="{ active: selectedTag === tag }"
            @click="selectedTag = tag">
            #{{ tag }}
          </button>
        </div>

      </div>
    </div>
  </div>


  <div v-if="loading" class="status-msg">LOADING PROMPTS...</div>

  <div v-else-if="filteredPrompts.length === 0" class="status-msg">NO MATCHING PROMPTS FOUND</div>

  <!-- Main Grid -->
  <div v-else class="grid-container">
    <div v-for="prompt in filteredPrompts" :key="prompt.id" class="prompt-item" @click="selectedPrompt = prompt">
      <div class="item-header">
        <span class="meta-cat">{{ prompt.category }}</span>
        <div class="header-actions">
          <button class="icon-btn action-btn" @click.stop="copyToClipboard(prompt.content)" title="Copy">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
          </button>
          <button class="icon-btn delete-btn" @click.stop="handleDelete(prompt.id)" title="Delete">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
          </button>
        </div>
      </div>

      <div class="item-body">
        <h3 class="item-title">{{ prompt.title }}</h3>
        <p class="item-summary">{{ prompt.content }}</p>
      </div>

      <div class="item-footer">
        <div class="meta-tags-row">
          <span class="version-badge" v-if="prompt.version > 1">v{{ prompt.version }}</span>
          <span v-for="tag in prompt.tags?.slice(0, 4)" :key="tag" class="meta-tag" @click.stop="selectedTag = tag">
            #{{ tag }}
          </span>
        </div>
      </div>
    </div>
  </div>

  <!-- Detail Modal -->
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="selectedPrompt" class="modal-overlay" @click="selectedPrompt = null">
        <div class="modal-panel" @click.stop>

          <div class="modal-top-bar">
            <span class="modal-id">ID: {{ selectedPrompt.id.slice(-6) }}</span>
            <button class="close-btn" @click="selectedPrompt = null">CLOSE [ESC]</button>
          </div>

          <div class="modal-content-scroll">
            <div class="article-header">
              <div class="header-top">
                <span class="meta-cat-badge">{{ selectedPrompt.category }}</span>
                <span class="version-badge" v-if="selectedPrompt.version > 1">v{{ selectedPrompt.version }}</span>
              </div>
              <h1 class="article-title">{{ selectedPrompt.title }}</h1>
              <div class="meta-tags-row large">
                <span v-for="tag in selectedPrompt.tags" :key="tag" class="meta-tag">#{{ tag }}</span>
              </div>
            </div>

            <div class="prompt-content-box">
              <textarea v-if="isEditing" v-model="editContent" class="prompt-editor"
                placeholder="Enter prompt content..."></textarea>
              <pre v-else>{{ selectedPrompt.content }}</pre>
            </div>

            <div class="modal-actions-bar">
              <div v-if="isEditing" class="editing-actions">
                <button class="action-btn primary large" @click="saveEdit">
                  SAVE CHANGES
                </button>
                <button class="action-btn text" @click="cancelEdit">
                  CANCEL
                </button>
              </div>
              <div v-else class="view-actions">
                <button class="action-btn primary large" @click="copyToClipboard(selectedPrompt.content)">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                  </svg>
                  COPY PROMPT
                </button>
                <div class="secondary-actions">
                  <button class="action-btn text" @click="startEdit">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none"
                      stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
                    </svg>
                    EDIT
                  </button>
                  <button class="action-btn text danger"
                    @click="handleDelete(selectedPrompt.id); selectedPrompt = null">
                    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none"
                      stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <polyline points="3 6 5 6 21 6"></polyline>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    </svg>
                    DELETE
                  </button>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>

</template>

<style scoped>
/* ... existing styles ... */

/* Modal Styles (Reused/Adapted from NewsGallery) */
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

.modal-content-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 60px 80px;
}

.article-header {
  margin-bottom: 40px;
}

.article-meta {
  font-family: monospace;
  font-size: 14px;
  color: var(--vp-c-text-2);
  margin-bottom: 20px;
}

.article-title {
  font-size: 40px;
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.prompt-full-content pre {
  white-space: pre-wrap;
  font-family: monospace;
  font-size: 16px;
  line-height: 1.6;
  background: var(--vp-c-bg-soft);
  padding: 24px;
  border-radius: 8px;
  border: 1px solid var(--vp-c-divider);
  margin-bottom: 24px;
}

.copy-btn.large {
  width: 100%;
  padding: 16px;
  font-size: 14px;
  background: var(--vp-c-text-1);
  color: var(--vp-c-bg);
  border-radius: 8px;
}

.copy-btn.large:hover {
  opacity: 0.9;
}

.action-group.large {
  display: flex;
  justify-content: flex-end;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Mobile */
@media (max-width: 768px) {
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
  line-clamp: 2;
  /* Standard property */
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-summary {
  font-size: 14px;
  line-height: 1.6;
  color: var(--vp-c-text-2);
  display: -webkit-box;
  -webkit-line-clamp: 4;
  line-clamp: 4;
  /* Standard property */
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-family: monospace;
  white-space: pre-wrap;
}

.item-footer {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.05em;
}

.meta-tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  min-height: 20px;
}

.action-group-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  border-top: 1px solid var(--vp-c-divider);
  padding-top: 16px;
}

.edit-actions {
  display: flex;
  gap: 12px;
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  max-width: 800px;
  margin: 0 auto;
}

.cloud-tag {
  font-family: monospace;
  font-size: 11px;
  color: var(--vp-c-text-2);
  background: var(--vp-c-bg-soft);
  padding: 4px 8px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.cloud-tag:hover,
.cloud-tag.active {
  background: var(--vp-c-text-1);
  color: var(--vp-c-bg);
}

.version-badge {
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
}

.icon-btn.small {
  font-size: 11px;
  padding: 6px 10px;
  opacity: 0.7;
  background: var(--vp-c-bg-soft);
  border-radius: 4px;
  border: 1px solid transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
  color: var(--vp-c-text-2);
}

.icon-btn.small:hover {
  opacity: 1;
  background: var(--vp-c-bg);
  border-color: var(--vp-c-divider);
  color: var(--vp-c-brand);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.meta-tag {
  font-family: monospace;
  font-size: 11px;
  color: var(--vp-c-text-2);
  background: var(--vp-c-bg-soft);
  padding: 2px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.meta-tag:hover {
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand);
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

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.action-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  opacity: 0.4;
  transition: all 0.2s;
  padding: 4px;
  border-radius: 4px;
  color: var(--vp-c-text-2);
}

.action-btn:hover {
  opacity: 1;
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-brand);
}

.delete-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  opacity: 0.3;
  transition: all 0.2s;
  padding: 4px;
  border-radius: 4px;
  color: var(--vp-c-text-2);
}

.delete-btn:hover {
  opacity: 1;
  background: var(--vp-c-danger-soft, rgba(239, 68, 68, 0.1));
  color: var(--vp-c-danger-1, #ef4444);
}

/* --- New Modal Styles --- */
.header-top {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.meta-cat-badge {
  font-family: monospace;
  font-size: 12px;
  font-weight: 700;
  color: var(--vp-c-brand);
  background: var(--vp-c-brand-soft);
  padding: 4px 8px;
  border-radius: 4px;
  text-transform: uppercase;
}

.meta-tags-row.large {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 16px;
}

.prompt-content-box {
  background: var(--vp-c-bg-alt);
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 24px;
  margin: 32px 0;
  font-family: monospace;
  font-size: 15px;
  line-height: 1.6;
  white-space: pre-wrap;
  color: var(--vp-c-text-1);
}

.modal-actions-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--vp-c-divider);
}

.action-btn.primary.large {
  background: var(--vp-c-brand);
  color: white;
  padding: 10px 20px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.action-btn.primary.large:hover {
  background: var(--vp-c-brand-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.secondary-actions {
  display: flex;
  gap: 16px;
}

.action-btn.text {
  background: none;
  border: none;
  color: var(--vp-c-text-2);
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 6px;
  transition: all 0.2s;
}

.action-btn.text:hover {
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-brand);
}

.action-btn.text.danger:hover {
  background: var(--vp-c-danger-soft);
  color: var(--vp-c-danger-1);
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

.prompt-content-box pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.prompt-editor {
  width: 100%;
  min-height: 200px;
  background: transparent;
  border: none;
  font-family: monospace;
  font-size: 15px;
  line-height: 1.6;
  color: var(--vp-c-text-1);
  resize: vertical;
  outline: none;
}

.editing-actions {
  display: flex;
  gap: 12px;
}

.view-actions {
  display: flex;
  justify-content: space-between;
  width: 100%;
  align-items: center;
}
</style>
