<script setup>
import { ref, onMounted, computed } from 'vue'
import { getAnonymousSupabaseClient } from '../utils/supabase'

// --- State ---
const messages = ref([])
const newMessage = ref('')
const isLoading = ref(true)
const isSending = ref(false)
const errorMsg = ref('')
const successMsg = ref('')
const supabase = getAnonymousSupabaseClient()
let userId = null

// --- Constants ---
const MAX_LENGTH = 200
const MAX_FETCH = 100

// --- Computed ---
const charCount = computed(() => newMessage.value.length)
const isOverLimit = computed(() => charCount.value > MAX_LENGTH)

// --- Helpers ---
const initUser = () => {
  if (typeof window === 'undefined') return
  const stored = localStorage.getItem('vitemind_user_id')
  if (stored) {
    userId = stored
  } else {
    userId = crypto.randomUUID ? crypto.randomUUID() : 'user_' + Math.random().toString(36).substr(2, 9)
    localStorage.setItem('vitemind_user_id', userId)
  }
}

const formatTime = (ts) => {
  if (!ts) return ''
  const date = new Date(ts)
  const now = new Date()
  const diff = (now - date) / 1000 // seconds

  if (diff < 60) return '刚刚'
  if (diff < 3600) return `${Math.floor(diff / 60)} 分钟前`
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小时前`
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

// Generate a consistent avatar color based on user_id
const getAvatarColor = (uid) => {
  if (!uid) return '#ccc'
  let hash = 0
  for (let i = 0; i < uid.length; i++) {
    hash = uid.charCodeAt(i) + ((hash << 5) - hash)
  }
  const c = (hash & 0x00ffffff).toString(16).toUpperCase()
  return '#' + '00000'.substring(0, 6 - c.length) + c
}

// --- Actions ---
const fetchMessages = async () => {
  if (!supabase) {
    isLoading.value = false
    return
  }
  try {
    const { data, error } = await supabase
      .from('guestbook_messages')
      .select('*')
      .eq('is_hidden', false)
      .order('created_at', { ascending: false })
      .limit(MAX_FETCH)

    if (error) throw error
    messages.value = data
  } catch (e) {
    console.warn('[Guestbook] Fetch failed:', e)
    // Don't show critical error on UI for fetch failure, just empty state or cached
  } finally {
    isLoading.value = false
  }
}

const postMessage = async () => {
  errorMsg.value = ''
  successMsg.value = ''

  if (!newMessage.value.trim()) return
  if (isOverLimit.value) {
    errorMsg.value = '内容超过 200 字限制'
    return
  }
  if (!supabase) {
    errorMsg.value = '数据库连接失败'
    return
  }

  isSending.value = true

  try {
    const { error } = await supabase
      .from('guestbook_messages')
      .insert([
        {
          user_id: userId,
          content: newMessage.value.trim()
        }
      ])

    if (error) {
      // Check for custom trigger error message
      if (error.message && error.message.includes('Rate limit exceeded')) {
        throw new Error('发送太频繁了，请休息一下 (每小时限 5 条)')
      }
      throw error
    }

    // Success
    successMsg.value = '留言发送成功！'
    newMessage.value = ''
    await fetchMessages() // Refresh list

    // Auto clear success message
    setTimeout(() => { successMsg.value = '' }, 3000)

  } catch (e) {
    console.error('[Guestbook] Post failed:', e)
    errorMsg.value = e.message || '发送失败，请稍后再试'
  } finally {
    isSending.value = false
  }
}

onMounted(() => {
  initUser()
  fetchMessages()
})
</script>

<template>
  <div class="guestbook-container">

    <!-- Input Section -->
    <div class="input-card">
      <div class="input-header">
        <h3>✍️ 写下你的留言...</h3>
        <span :class="{ 'text-red': isOverLimit }">{{ charCount }} / {{ MAX_LENGTH }}</span>
      </div>
      <textarea
        v-model="newMessage"
        placeholder="无论是建议、吐槽还是打招呼，都欢迎告诉我们！(支持 Markdown 纯文本)"
        rows="4"
        :disabled="isSending"
      ></textarea>

      <div class="action-bar">
        <div class="status-msg">
          <span v-if="errorMsg" class="error">{{ errorMsg }}</span>
          <span v-if="successMsg" class="success">{{ successMsg }}</span>
        </div>
        <button
          @click="postMessage"
          :disabled="isSending || !newMessage.trim() || isOverLimit"
          class="submit-btn"
        >
          {{ isSending ? '发送中...' : '发布留言' }}
        </button>
      </div>
    </div>

    <!-- Messages Wall (Masonry) -->
    <div v-if="isLoading" class="loading">加载中...</div>

    <div v-else-if="messages.length === 0" class="empty-state">
      还没有留言，来抢沙发吧！🛋️
    </div>

    <div v-else class="masonry-wall">
      <div v-for="msg in messages" :key="msg.id" class="msg-card">
        <div class="msg-header">
          <div class="avatar" :style="{ backgroundColor: getAvatarColor(msg.user_id) }"></div>
          <span class="time">{{ formatTime(msg.created_at) }}</span>
        </div>
        <div class="msg-content">{{ msg.content }}</div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.guestbook-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px 0;
}

/* Input Card */
.input-card {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 40px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}

.input-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
}

textarea {
  width: 100%;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  padding: 12px;
  color: var(--vp-c-text-1);
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.2s;
}

textarea:focus {
  border-color: var(--vp-c-brand);
  outline: none;
}

.action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}

.status-msg {
  font-size: 0.9rem;
}
.error { color: var(--vp-c-danger); }
.success { color: var(--vp-c-success); }
.text-red { color: var(--vp-c-danger); }

.submit-btn {
  background: var(--vp-c-brand);
  color: white;
  border: none;
  padding: 8px 24px;
  border-radius: 20px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Masonry Layout */
.masonry-wall {
  column-count: 1;
  column-gap: 20px;
}

@media (min-width: 640px) {
  .masonry-wall { column-count: 2; }
}

@media (min-width: 1024px) {
  .masonry-wall { column-count: 3; }
}

.msg-card {
  break-inside: avoid;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
  transition: transform 0.2s;
}

.msg-card:hover {
  transform: translateY(-2px);
  border-color: var(--vp-c-brand-dimm);
}

.msg-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  gap: 10px;
}

.avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  opacity: 0.8;
}

.time {
  font-size: 0.8rem;
  color: var(--vp-c-text-3);
}

.msg-content {
  font-size: 0.95rem;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--vp-c-text-1);
}

.loading, .empty-state {
  text-align: center;
  padding: 40px;
  color: var(--vp-c-text-3);
}
</style>
