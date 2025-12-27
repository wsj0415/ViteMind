<script setup>
import { ref } from 'vue'

const email = ref('')
const status = ref('idle') // idle, loading, success, error

const subscribe = () => {
  if (!email.value || !email.value.includes('@')) {
    status.value = 'error'
    return
  }
  
  status.value = 'loading'
  
  // Simulate API call
  setTimeout(() => {
    status.value = 'success'
    email.value = ''
  }, 1500)
}
</script>

<template>
  <div class="newsletter-container">
    <div class="content-wrapper">
      <div class="icon">📧</div>
      <h1 class="title">INTELLIGENCE BRIEF</h1>
      <p class="subtitle">
        Join 10,000+ subscribers. Get the latest AI insights delivered to your inbox every morning.
        <br>
        <span class="highlight">No spam. Just signal.</span>
      </p>

      <div class="form-group">
        <input 
          v-model="email" 
          type="email" 
          placeholder="ENTER YOUR EMAIL" 
          class="email-input"
          :disabled="status === 'success'"
          @keyup.enter="subscribe"
        />
        <button 
          class="submit-btn" 
          :class="status"
          @click="subscribe"
          :disabled="status === 'loading' || status === 'success'"
        >
          <span v-if="status === 'loading'">PROCESSING...</span>
          <span v-else-if="status === 'success'">SUBSCRIBED ✓</span>
          <span v-else>SUBSCRIBE →</span>
        </button>
      </div>

      <p v-if="status === 'error'" class="error-msg">PLEASE ENTER A VALID EMAIL ADDRESS.</p>
      
      <div class="trust-badges">
        <span>DAILY UPDATES</span> • 
        <span>CURATED CONTENT</span> • 
        <span>UNSUBSCRIBE ANYTIME</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.newsletter-container {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: "Inter", sans-serif;
  color: var(--vp-c-text-1);
  padding: 40px 20px;
}

.content-wrapper {
  max-width: 500px;
  width: 100%;
  text-align: center;
}

.icon {
  font-size: 48px;
  margin-bottom: 24px;
}

.title {
  font-size: 32px;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin-bottom: 16px;
  text-transform: uppercase;
}

.subtitle {
  font-size: 16px;
  line-height: 1.6;
  color: var(--vp-c-text-2);
  margin-bottom: 40px;
}

.highlight {
  color: var(--vp-c-text-1);
  font-weight: 600;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 16px;
}

.email-input {
  width: 100%;
  padding: 16px;
  font-family: monospace;
  font-size: 16px;
  border: 2px solid var(--vp-c-text-1);
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  border-radius: 0;
  text-align: center;
  transition: all 0.2s;
}

.email-input:focus {
  outline: none;
  background: var(--vp-c-bg-soft);
}

.submit-btn {
  width: 100%;
  padding: 16px;
  font-family: monospace;
  font-size: 14px;
  font-weight: 700;
  background: var(--vp-c-text-1);
  color: var(--vp-c-bg);
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  text-transform: uppercase;
}

.submit-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: translateY(-2px);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.submit-btn.success {
  background: var(--vp-c-green-3);
  color: white;
}

.error-msg {
  color: var(--vp-c-red-1);
  font-family: monospace;
  font-size: 12px;
  margin-top: 8px;
}

.trust-badges {
  margin-top: 40px;
  font-family: monospace;
  font-size: 10px;
  color: var(--vp-c-text-3);
  letter-spacing: 1px;
}
</style>
