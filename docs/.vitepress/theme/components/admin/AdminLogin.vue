<script setup>
import { ref } from 'vue'
import { createClient } from '@supabase/supabase-js'
import { useRouter } from 'vitepress'

const supabaseUrl = import.meta.env.SUPABASE_URL
const supabaseKey = import.meta.env.SUPABASE_KEY
const supabase = createClient(supabaseUrl, supabaseKey)
const router = useRouter()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

const handleLogin = async () => {
    if (!email.value || !password.value) {
        errorMsg.value = '请输入邮箱和密码'
        return
    }

    loading.value = true
    errorMsg.value = ''

    try {
        const { data, error } = await supabase.auth.signInWithPassword({
            email: email.value,
            password: password.value
        })

        if (error) throw error

        // Login successful
        // VitePress router doesn't support full page reload, but we might need it to refresh auth state
        // For now, just redirect to dashboard
        window.location.href = '/admin/index'
    } catch (e) {
        console.error('Login error:', e)
        errorMsg.value = '登录失败: ' + e.message
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <div class="login-container">
        <div class="login-card">
            <h1 class="login-title">ViteMind Admin</h1>
            <p class="login-subtitle">请登录以管理内容</p>

            <div class="form-group">
                <label>邮箱</label>
                <input v-model="email" type="email" placeholder="admin@example.com" class="swiss-input"
                    @keyup.enter="handleLogin" />
            </div>

            <div class="form-group">
                <label>密码</label>
                <input v-model="password" type="password" placeholder="••••••••" class="swiss-input"
                    @keyup.enter="handleLogin" />
            </div>

            <div v-if="errorMsg" class="error-msg">
                {{ errorMsg }}
            </div>

            <button class="login-btn" :disabled="loading" @click="handleLogin">
                {{ loading ? '登录中...' : '登 录' }}
            </button>
        </div>
    </div>
</template>

<style scoped>
.login-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 60vh;
    padding: 20px;
}

.login-card {
    width: 100%;
    max-width: 400px;
    padding: 40px;
    background: var(--vp-c-bg);
    border: 1px solid var(--vp-c-divider);
    border-radius: 12px;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.05);
}

.login-title {
    font-size: 24px;
    font-weight: 700;
    text-align: center;
    margin-bottom: 8px;
    background: linear-gradient(120deg, #bd34fe 30%, #41d1ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.login-subtitle {
    text-align: center;
    color: var(--vp-c-text-2);
    margin-bottom: 32px;
    font-size: 14px;
}

.form-group {
    margin-bottom: 20px;
}

label {
    display: block;
    margin-bottom: 8px;
    font-size: 12px;
    font-weight: 600;
    color: var(--vp-c-text-2);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.swiss-input {
    width: 100%;
    padding: 12px;
    background: var(--vp-c-bg-alt);
    border: 1px solid var(--vp-c-divider);
    border-radius: 8px;
    color: var(--vp-c-text-1);
    font-size: 14px;
    transition: all 0.2s;
}

.swiss-input:focus {
    border-color: var(--vp-c-brand);
    outline: none;
    box-shadow: 0 0 0 2px var(--vp-c-brand-soft);
}

.error-msg {
    color: #ef4444;
    font-size: 13px;
    margin-bottom: 20px;
    text-align: center;
    padding: 8px;
    background: rgba(239, 68, 68, 0.1);
    border-radius: 6px;
}

.login-btn {
    width: 100%;
    padding: 14px;
    background: var(--vp-c-brand);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.login-btn:hover {
    background: var(--vp-c-brand-dark);
    transform: translateY(-1px);
}

.login-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
    transform: none;
}
</style>
