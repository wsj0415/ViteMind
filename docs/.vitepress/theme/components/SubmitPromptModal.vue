<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { createClient } from '@supabase/supabase-js'

const props = defineProps({
  isOpen: Boolean,
  categories: Array
})

const emit = defineEmits(['close', 'submit'])

// Supabase Client
const supabaseUrl = import.meta.env.SUPABASE_URL
const supabaseKey = import.meta.env.SUPABASE_KEY
const supabase = createClient(supabaseUrl, supabaseKey)

// Form State
const form = ref({
  title: '',
  content: '',
  category: 'Coding',
  tags: ''
})

const loading = ref(false)
const message = ref('')
const isSuccess = ref(false)

const submitPrompt = async () => {
  if (!form.value.title || !form.value.content) {
    message.value = 'TITLE AND CONTENT ARE REQUIRED.'
    return
  }

  loading.value = true
  message.value = ''

  try {
    const tagsArray = form.value.tags.split(',').map(t => t.trim()).filter(t => t)

    const { error } = await supabase
      .from('ai_prompts')
      .insert([
        {
          title: form.value.title,
          content: form.value.content,
          category: form.value.category,
          tags: tagsArray,
          approved: false // Default to unapproved
        }
      ])

    if (error) throw error

    isSuccess.value = true
    message.value = 'SUBMISSION SUCCESSFUL. PENDING APPROVAL.'

    // Emit the submission for localStorage
    emit('submit', {
      title: form.value.title,
      content: form.value.content,
      category: form.value.category,
      tags: tagsArray,
      created_at: new Date().toISOString()
    })

    // Reset form
    form.value = { title: '', content: '', category: 'Coding', tags: '' }

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
            <span id="modal-title" class="modal-title">SUBMIT NEW PROMPT</span>
            <button class="close-btn" @click="close">CLOSE [ESC]</button>
          </div>

          <div class="modal-content">
            <div class="form-group">
              <label for="prompt-title">TITLE *</label>
              <input id="prompt-title" v-model="form.title" type="text" placeholder="e.g. Python Code Optimizer" class="swiss-input" />
            </div>

            <div class="form-group">
              <label for="prompt-category">CATEGORY</label>
              <select id="prompt-category" v-model="form.category" class="swiss-select">
                <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
              </select>
            </div>

            <div class="form-group">
              <label for="prompt-content">PROMPT CONTENT *</label>
              <textarea id="prompt-content" v-model="form.content" rows="6" placeholder="Enter your prompt here..."
                class="swiss-input"></textarea>
            </div>

            <div class="form-group">
              <label for="prompt-tags">TAGS (Comma separated)</label>
              <input id="prompt-tags" v-model="form.tags" type="text" placeholder="e.g. python, optimization, coding"
                class="swiss-input" />
            </div>

            <div v-if="message" class="status-msg" :class="{ success: isSuccess, error: !isSuccess }">
              {{ message }}
            </div>

            <button class="submit-btn" :disabled="loading" @click="submitPrompt">
              {{ loading ? 'SUBMITTING...' : 'SUBMIT PROMPT' }}
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
  max-width: 600px;
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

.swiss-input,
.swiss-select {
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

.swiss-input:focus,
.swiss-select:focus {
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
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
