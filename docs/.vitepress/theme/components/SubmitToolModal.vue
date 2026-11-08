<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { createClient } from '@supabase/supabase-js'
import { isValidUrl } from '../utils/validation.js'

const props = defineProps({
  isOpen: Boolean,
  categories: Array
})

const emit = defineEmits(['close', 'submit'])

// Supabase Client (lazy initialization for SSR compatibility)
const supabaseUrl = import.meta.env.SUPABASE_URL
const supabaseKey = import.meta.env.SUPABASE_KEY
let supabase = null

// Get or create Supabase client
const getSupabase = () => {
  if (!supabase && typeof window !== 'undefined' && supabaseUrl && supabaseKey) {
    supabase = createClient(supabaseUrl, supabaseKey)
  }
  return supabase
}

// Form State
const form = ref({
  name: '',
  link: '',
  desc: '',
  category: 'Coding'
})

const loading = ref(false)
const message = ref('')
const isSuccess = ref(false)

const submitTool = async () => {
  if (!form.value.name || !form.value.link) {
    message.value = 'NAME AND LINK ARE REQUIRED.'
    return
  }

  // Sentinel Security: Validate URL Protocol (Prevent XSS)
  if (!isValidUrl(form.value.link)) {
    message.value = 'INVALID URL. USE HTTP OR HTTPS.'
    return
  }

  const client = getSupabase()
  if (!client) {
    message.value = 'DATABASE CONNECTION NOT AVAILABLE.'
    return
  }

  loading.value = true
  message.value = ''

  try {
    const { error } = await client
      .from('ai_tools')
      .insert([
        {
          name: form.value.name,
          link: form.value.link,
          description: form.value.desc,
          category: form.value.category,
          approved: false // Default to unapproved
        }
      ])

    if (error) throw error

    isSuccess.value = true
    message.value = 'SUBMISSION SUCCESSFUL. PENDING APPROVAL.'
    
    // Emit the submission for localStorage
    emit('submit', {
      name: form.value.name,
      link: form.value.link,
      description: form.value.desc,
      category: form.value.category,
      submittedAt: new Date().toISOString()
    })
    
    // Reset form
    form.value = { name: '', link: '', desc: '', category: 'Coding' }
    
    // Auto close after 2s
    setTimeout(() => {
      close()
    }, 2000)

  } catch (e) {
    console.error(e)
    message.value = 'SUBMISSION FAILED: ' + e.message
    isSuccess.value = false
  } finally {
    loading.value = false
  }
}

const close = () => {
  emit('close')
  message.value = ''
  isSuccess.value = false
}

const handleKeydown = (e) => {
  if (e.key === 'Escape' && props.isOpen) {
    close()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="isOpen" class="modal-overlay" @click="close" role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <div class="modal-panel" @click.stop>
          
          <div class="modal-header">
            <span id="modal-title" class="modal-title">SUBMIT NEW TOOL</span>
            <button class="close-btn" @click="close">CLOSE [ESC]</button>
          </div>

          <div class="modal-content">
            <div class="form-group">
              <label for="tool-name">TOOL NAME *</label>
              <input id="tool-name" v-model="form.name" type="text" placeholder="e.g. ChatGPT" class="swiss-input" />
            </div>

            <div class="form-group">
              <label for="tool-link">LINK *</label>
              <input id="tool-link" v-model="form.link" type="text" placeholder="https://..." class="swiss-input" />
            </div>

            <div class="form-group">
              <label for="tool-category">CATEGORY</label>
              <select id="tool-category" v-model="form.category" class="swiss-select">
                <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>

            <div class="form-group">
              <label for="tool-desc">DESCRIPTION</label>
              <textarea id="tool-desc" v-model="form.desc" rows="3" placeholder="Brief description..." class="swiss-input"></textarea>
            </div>

            <div v-if="message" class="status-msg" :class="{ success: isSuccess, error: !isSuccess }">
              {{ message }}
            </div>

            <button 
              class="submit-btn" 
              :disabled="loading"
              @click="submitTool"
            >
              {{ loading ? 'SUBMITTING...' : 'SUBMIT TOOL' }}
            </button>
          </div>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
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
  max-width: 500px;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid var(--vp-c-divider);
  display: flex;
  justify-content: space-between;
  font-family: monospace;
  font-size: 12px;
  font-weight: 700;
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-family: inherit;
  color: inherit;
}

.modal-content {
  padding: 40px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-family: monospace;
  font-size: 11px;
  text-transform: uppercase;
  color: var(--vp-c-text-2);
}

.swiss-input, .swiss-select {
  padding: 12px;
  border: 1px solid var(--vp-c-divider);
  background: var(--vp-c-bg-alt);
  color: var(--vp-c-text-1);
  font-family: inherit;
  font-size: 14px;
  outline: none;
  border-radius: 0;
  width: 100%;
}

.swiss-input:focus, .swiss-select:focus {
  border-color: var(--vp-c-brand);
}

.submit-btn {
  margin-top: 10px;
  padding: 16px;
  background: var(--vp-c-text-1);
  color: var(--vp-c-bg);
  border: none;
  font-family: monospace;
  font-weight: 700;
  cursor: pointer;
  transition: opacity 0.2s;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.status-msg {
  font-family: monospace;
  font-size: 12px;
  padding: 10px;
  text-align: center;
}

.status-msg.success {
  color: #10b981;
  border: 1px solid #10b981;
}

.status-msg.error {
  color: #ef4444;
  border: 1px solid #ef4444;
}

/* Transitions */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
