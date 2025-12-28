<script setup>
import { ref, onMounted } from 'vue'
import { createClient } from '@supabase/supabase-js'

const props = defineProps({
    title: String
})

const supabaseUrl = import.meta.env.SUPABASE_URL
const supabaseKey = import.meta.env.SUPABASE_KEY
const supabase = createClient(supabaseUrl, supabaseKey)

const user = ref(null)
const loading = ref(true)
const isSidebarOpen = ref(true)

const menuItems = [
    { text: '仪表盘', link: '/admin/index', icon: '📊' },
    { text: 'AI 工具', link: '/admin/tools', icon: '🛠' },
    { text: '设计资源', link: '/admin/resources', icon: '🎨' },
    { text: 'AI 提示词', link: '/admin/prompts', icon: '💡' },
    { text: '每日新闻', link: '/admin/news', icon: '📰' }
]

onMounted(async () => {
    // Check auth status
    const { data: { session } } = await supabase.auth.getSession()

    if (!session) {
        // Redirect to login if not authenticated
        window.location.href = '/admin/login'
        return
    }

    user.value = session.user
    loading.value = false
})

const handleLogout = async () => {
    await supabase.auth.signOut()
    window.location.href = '/admin/login'
}
</script>

<template>
    <div v-if="loading" class="loading-screen">
        <div class="spinner"></div>
    </div>

    <div v-else class="admin-layout">
        <!-- Sidebar -->
        <aside class="admin-sidebar" :class="{ collapsed: !isSidebarOpen }">
            <div class="sidebar-header">
                <span class="logo-text" v-if="isSidebarOpen">ViteMind Admin</span>
                <span class="logo-icon" v-else>VM</span>
            </div>

            <nav class="sidebar-nav">
                <a v-for="item in menuItems" :key="item.link" :href="item.link" class="nav-item"
                    :class="{ active: $frontmatter.path === item.link }">
                    <span class="nav-icon">{{ item.icon }}</span>
                    <span class="nav-text" v-if="isSidebarOpen">{{ item.text }}</span>
                </a>
            </nav>

            <div class="sidebar-footer">
                <button class="logout-btn" @click="handleLogout">
                    <span class="nav-icon">🚪</span>
                    <span class="nav-text" v-if="isSidebarOpen">退出登录</span>
                </button>
            </div>
        </aside>

        <!-- Main Content -->
        <main class="admin-main">
            <header class="admin-header">
                <button class="toggle-btn" @click="isSidebarOpen = !isSidebarOpen">
                    ☰
                </button>
                <div class="user-info">
                    <span class="user-email">{{ user?.email }}</span>
                    <div class="user-avatar">
                        {{ user?.email?.charAt(0).toUpperCase() }}
                    </div>
                </div>
            </header>

            <div class="content-wrapper">
                <div class="page-header" v-if="title">
                    <h1>{{ title }}</h1>
                </div>
                <slot></slot>
            </div>
        </main>
    </div>
</template>

<style scoped>
.admin-layout {
    display: flex;
    min-height: 100vh;
    background: var(--vp-c-bg-alt);
    font-family: "Inter", sans-serif;
}

/* Sidebar */
.admin-sidebar {
    width: 240px;
    background: var(--vp-c-bg);
    border-right: 1px solid var(--vp-c-divider);
    display: flex;
    flex-direction: column;
    transition: width 0.3s ease;
    position: fixed;
    height: 100vh;
    z-index: 100;
}

.admin-sidebar.collapsed {
    width: 64px;
}

.sidebar-header {
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid var(--vp-c-divider);
    font-weight: 700;
    color: var(--vp-c-brand);
}

.sidebar-nav {
    flex: 1;
    padding: 16px 0;
    overflow-y: auto;
}

.nav-item {
    display: flex;
    align-items: center;
    padding: 12px 20px;
    color: var(--vp-c-text-2);
    text-decoration: none;
    transition: all 0.2s;
    white-space: nowrap;
    overflow: hidden;
}

.nav-item:hover {
    background: var(--vp-c-bg-soft);
    color: var(--vp-c-text-1);
}

.nav-item.active {
    background: var(--vp-c-brand-soft);
    color: var(--vp-c-brand);
    border-right: 3px solid var(--vp-c-brand);
}

.nav-icon {
    font-size: 18px;
    min-width: 24px;
    margin-right: 12px;
}

.sidebar-footer {
    padding: 16px;
    border-top: 1px solid var(--vp-c-divider);
}

.logout-btn {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 10px;
    background: transparent;
    border: none;
    color: #ef4444;
    cursor: pointer;
    border-radius: 6px;
    transition: background 0.2s;
}

.logout-btn:hover {
    background: rgba(239, 68, 68, 0.1);
}

/* Main Content */
.admin-main {
    flex: 1;
    margin-left: 240px;
    transition: margin-left 0.3s ease;
    display: flex;
    flex-direction: column;
}

.admin-sidebar.collapsed+.admin-main {
    margin-left: 64px;
}

.admin-header {
    height: 64px;
    background: var(--vp-c-bg);
    border-bottom: 1px solid var(--vp-c-divider);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
}

.toggle-btn {
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    color: var(--vp-c-text-2);
}

.user-info {
    display: flex;
    align-items: center;
    gap: 12px;
}

.user-email {
    font-size: 14px;
    color: var(--vp-c-text-2);
}

.user-avatar {
    width: 32px;
    height: 32px;
    background: var(--vp-c-brand);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 14px;
}

.content-wrapper {
    flex: 1;
    padding: 32px;
    overflow-y: auto;
}

.page-header {
    margin-bottom: 24px;
}

.page-header h1 {
    font-size: 24px;
    font-weight: 700;
    margin: 0;
}

/* Loading Screen */
.loading-screen {
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--vp-c-bg);
}

.spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--vp-c-divider);
    border-top-color: var(--vp-c-brand);
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}
</style>
