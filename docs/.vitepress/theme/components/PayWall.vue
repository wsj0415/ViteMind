<script setup>
import { ref } from 'vue'

const props = defineProps({
  price: {
    type: String,
    default: '9.9'
  },
  id: {
    type: String,
    required: true
  }
})

const isUnlocked = ref(false)
const password = ref('')
const error = ref('')

// 模拟解锁逻辑
// 在实际生产中，这里应该调用后端 API 验证 Token 或 License
const checkPassword = () => {
  if (password.value === 'vip888') {
    isUnlocked.value = true
    error.value = ''
    // 可以将解锁状态保存在 localStorage
    localStorage.setItem(`vitemind_unlocked_${props.id}`, 'true')
  } else {
    error.value = '密码错误，请重试'
  }
}

// 初始化时检查是否已解锁
if (typeof window !== 'undefined') {
  const stored = localStorage.getItem(`vitemind_unlocked_${props.id}`)
  if (stored === 'true') {
    isUnlocked.value = true
  }
}
</script>

<template>
  <div class="paywall-container">
    <!-- 已解锁状态 -->
    <div v-if="isUnlocked" class="unlocked-content">
      <div class="success-banner">
        🎉 已解锁付费内容
      </div>
      <slot></slot>
    </div>

    <!-- 未解锁状态 -->
    <div v-else class="locked-content">
      <div class="lock-icon">🔒</div>
      <h3>本内容为付费专享</h3>
      <p class="price">解锁价格: <span class="amount">¥{{ price }}</span></p>
      
      <div class="preview-text">
        <slot name="preview">
          这里是付费内容的预览部分...购买后查看完整干货。
        </slot>
      </div>

      <div class="unlock-form">
        <input 
          v-model="password" 
          type="password" 
          placeholder="请输入访问密码 (测试密码: vip888)"
          @keyup.enter="checkPassword"
        >
        <button @click="checkPassword">立即解锁</button>
      </div>
      <p v-if="error" class="error-msg">{{ error }}</p>
      
      <div class="payment-link">
        <a href="#" target="_blank">👉 点击这里获取访问密码</a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.paywall-container {
  margin: 2rem 0;
  border-radius: 8px;
  overflow: hidden;
}

.unlocked-content {
  animation: fadeIn 0.5s ease;
}

.success-banner {
  background-color: #e6fffa;
  color: #047857;
  padding: 0.5rem;
  text-align: center;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  border-radius: 4px;
}

.locked-content {
  background: linear-gradient(to bottom, var(--vp-c-bg-soft), var(--vp-c-bg-alt));
  border: 1px solid var(--vp-c-divider);
  padding: 2rem;
  text-align: center;
  border-radius: 12px;
}

.lock-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.price {
  font-size: 1.2rem;
  color: var(--vp-c-text-2);
  margin: 1rem 0;
}

.amount {
  color: var(--vp-c-brand);
  font-weight: bold;
  font-size: 1.5rem;
}

.preview-text {
  opacity: 0.6;
  filter: blur(0.5px);
  margin-bottom: 2rem;
  font-style: italic;
}

.unlock-form {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 1rem;
}

input {
  padding: 0.5rem 1rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 4px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
}

button {
  background-color: var(--vp-c-brand);
  color: white;
  padding: 0.5rem 1.5rem;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
}

button:hover {
  background-color: var(--vp-c-brand-dark);
}

.error-msg {
  color: #ef4444;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.payment-link {
  margin-top: 1.5rem;
  font-size: 0.9rem;
}

.payment-link a {
  color: var(--vp-c-brand);
  text-decoration: none;
}

.payment-link a:hover {
  text-decoration: underline;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
