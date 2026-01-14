<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
    isOpen: Boolean,
    categories: Array
})

const emit = defineEmits(['close', 'submit'])

// Form State
const form = ref({
    title: '',
    url: '',
    description: '',
    category: 'Design Tools',
    tags: [],
    logo_url: ''
})

const availableTags = ['Free', 'Paid', 'Open Source', 'Premium', 'Trial']
const loading = ref(false)
const message = ref('')
const isSuccess = ref(false)

const toggleTag = (tag) => {
    const index = form.value.tags.indexOf(tag)
    if (index > -1) {
        form.value.tags.splice(index, 1)
    } else {
        form.value.tags.push(tag)
    }
}

const submitResource = async () => {
    if (!form.value.title || !form.value.url || !form.value.description) {
        message.value = '标题、链接和描述为必填项'
        return
    }

    // Sentinel Security: Validate URL Protocol (Prevent XSS)
    try {
        const url = new URL(form.value.url)
        const allowedProtocols = ['http:', 'https:']
        if (!allowedProtocols.includes(url.protocol)) {
            message.value = '链接格式错误：仅支持 http 或 https 协议'
            return
        }

        if (form.value.logo_url) {
            const logoUrl = new URL(form.value.logo_url)
            if (!allowedProtocols.includes(logoUrl.protocol)) {
                message.value = 'Logo 链接格式错误：仅支持 http 或 https 协议'
                return
            }
        }
    } catch (e) {
        message.value = '无效的链接格式'
        return
    }

    loading.value = true
    message.value = ''

    try {
        emit('submit', {
            title: form.value.title,
            url: form.value.url,
            description: form.value.description,
            category: form.value.category,
            tags: form.value.tags,
            logo_url: form.value.logo_url || null,
            source: 'User Submitted'
        })

        isSuccess.value = true
        message.value = '提交成功！'

        // Reset form
        form.value = {
            title: '',
            url: '',
            description: '',
            category: 'Design Tools',
            tags: [],
            logo_url: ''
        }

    } catch (e) {
        console.error(e)
        message.value = '提交失败: ' + e.message
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
                        <span id="modal-title" class="modal-title">提交设计资源</span>
                        <button class="close-btn" @click="close">关闭 [ESC]</button>
                    </div>

                    <div class="modal-content">
                        <div class="form-group">
                            <label for="resource-title">资源名称 *</label>
                            <input id="resource-title" v-model="form.title" type="text" placeholder="例如: Figma" class="swiss-input" />
                        </div>

                        <div class="form-group">
                            <label for="resource-url">资源链接 *</label>
                            <input id="resource-url" v-model="form.url" type="text" placeholder="https://..." class="swiss-input" />
                        </div>

                        <div class="form-group">
                            <label for="resource-desc">资源描述 *</label>
                            <textarea id="resource-desc" v-model="form.description" rows="3" placeholder="简要描述这个资源..."
                                class="swiss-input"></textarea>
                        </div>

                        <div class="form-group">
                            <label for="resource-category">分类</label>
                            <select id="resource-category" v-model="form.category" class="swiss-select">
                                <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label>标签</label>
                            <div class="tags-selector">
                                <button v-for="tag in availableTags" :key="tag" type="button" class="tag-btn"
                                    :class="{ active: form.tags.includes(tag) }" @click="toggleTag(tag)">
                                    {{ tag }}
                                </button>
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="resource-logo">Logo URL (可选)</label>
                            <input id="resource-logo" v-model="form.logo_url" type="text" placeholder="https://..." class="swiss-input" />
                        </div>

                        <div v-if="message" class="status-msg" :class="{ success: isSuccess, error: !isSuccess }">
                            {{ message }}
                        </div>

                        <button class="submit-btn" :disabled="loading" @click="submitResource">
                            {{ loading ? '提交中...' : '提交资源' }}
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
    padding: 1rem;
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
    max-height: 90vh;
    overflow-y: auto;
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

.tags-selector {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.tag-btn {
    padding: 0.5rem 1rem;
    border: 1px solid var(--vp-c-divider);
    background: transparent;
    color: var(--vp-c-text-2);
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.2s;
}

.tag-btn:hover {
    border-color: #667eea;
    color: #667eea;
}

.tag-btn.active {
    background: #667eea;
    color: white;
    border-color: #667eea;
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
