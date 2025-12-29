<script setup>
import { ref, computed, onMounted } from 'vue'
import { createClient } from '@supabase/supabase-js'
import SubmitResourceModal from './SubmitResourceModal.vue'

// Supabase Client (lazy initialization for SSR compatibility)
const supabaseUrl = import.meta.env.SUPABASE_URL
const supabaseKey = import.meta.env.SUPABASE_KEY
let supabase = null

const resources = ref([])
const loading = ref(true)
const categories = ['ALL', 'Design Tools', 'UI Libraries', 'Icons & Fonts', 'Colors', 'Design Systems', 'Learning', 'Inspiration', 'Prototyping']
const selectedCategory = ref('ALL')
const searchQuery = ref('')
const isModalOpen = ref(false)
const showBackToTop = ref(false)
const sortBy = ref('default') // 'default' | 'name-asc' | 'name-desc' | 'date-desc'

// Category icons mapping
const categoryIcons = {
    'ALL': '🌐',
    'Design Tools': '🎨',
    'UI Libraries': '🧩',
    'Icons & Fonts': '🔤',
    'Colors': '🎨',
    'Design Systems': '📚',
    'Learning': '📖',
    'Inspiration': '✨',
    'Prototyping': '🔧'
}

// Scroll event handler
const handleScroll = () => {
    if (typeof window !== 'undefined') {
        showBackToTop.value = window.scrollY > 300
    }
}

// Scroll to top
const scrollToTop = () => {
    if (typeof window !== 'undefined') {
        window.scrollTo({ top: 0, behavior: 'smooth' })
    }
}

// Clear search
const clearSearch = () => {
    searchQuery.value = ''
}

// Get favicon
const getFavicon = (url) => {
    try {
        const domain = new URL(url).hostname
        return `https://www.google.com/s2/favicons?domain=${domain}&sz=128`
    } catch {
        return null
    }
}

// Fetch resources from Supabase
onMounted(async () => {
    if (typeof window === 'undefined') {
        loading.value = false
        return
    }

    window.addEventListener('scroll', handleScroll)

    if (supabaseUrl && supabaseKey) {
        supabase = createClient(supabaseUrl, supabaseKey)
    }

    if (!supabase) {
        loading.value = false
        return
    }

    try {
        loading.value = true
        const { data, error } = await supabase
            .from('design_resources')
            .select('*')
            .order('is_featured', { ascending: false })
            .order('created_at', { ascending: false })

        if (error) throw error
        resources.value = data || []
    } catch (e) {
        console.error('Error fetching resources:', e)
    } finally {
        loading.value = false
    }
})

// Handle new submission
const handleSubmission = async (resource) => {
    if (!supabase) return

    try {
        const { error } = await supabase
            .from('design_resources')
            .insert([resource])

        if (error) throw error

        alert('资源提交成功！')
        isModalOpen.value = false

        // Refresh resources
        const { data } = await supabase
            .from('design_resources')
            .select('*')
            .order('is_featured', { ascending: false })
            .order('created_at', { ascending: false })

        if (data) resources.value = data
    } catch (e) {
        console.error('Error submitting resource:', e)
        alert('提交失败，请重试')
    }
}

// Filtered and sorted resources
const filteredResources = computed(() => {
    const query = searchQuery.value.toLowerCase().trim()
    let result = resources.value.filter(r => {
        const matchesCat = selectedCategory.value === 'ALL' || r.category === selectedCategory.value
        const matchesSearch = !query ||
            r.title?.toLowerCase().includes(query) ||
            r.description?.toLowerCase().includes(query) ||
            r.tags?.some(tag => tag.toLowerCase().includes(query))
        return matchesCat && matchesSearch
    })

    // Apply sorting
    if (sortBy.value === 'name-asc') {
        result = [...result].sort((a, b) => a.title.localeCompare(b.title))
    } else if (sortBy.value === 'name-desc') {
        result = [...result].sort((a, b) => b.title.localeCompare(a.title))
    } else if (sortBy.value === 'date-desc') {
        result = [...result].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    }

    return result
})

// Featured resources
const featuredResources = computed(() => {
    return filteredResources.value.filter(r => r.is_featured)
})

// Regular resources
const regularResources = computed(() => {
    return filteredResources.value.filter(r => !r.is_featured)
})
</script>

<template>
    <div class="resources-page">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="sidebar-header">
                <h2>分类</h2>
            </div>
            <nav class="category-nav">
                <button v-for="cat in categories" :key="cat" class="cat-item"
                    :class="{ active: selectedCategory === cat }" @click="selectedCategory = cat">
                    <span class="cat-icon">{{ categoryIcons[cat] }}</span>
                    <span class="cat-name">{{ cat }}</span>
                </button>
            </nav>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
            <!-- Header -->
            <header class="content-header">
                <div class="search-wrapper">
                    <div class="search-container">
                        <span class="search-icon">🔍</span>
                        <input v-model="searchQuery" type="text" placeholder="搜索设计资源..." class="search-input" />
                        <button v-if="searchQuery" class="clear-btn" @click="clearSearch">✕</button>
                    </div>
                    <span class="resources-count">找到 {{ filteredResources.length }} 个资源</span>
                </div>
                <div class="header-actions">
                    <select v-model="sortBy" class="sort-select">
                        <option value="default">默认排序</option>
                        <option value="name-asc">名称 A-Z</option>
                        <option value="name-desc">名称 Z-A</option>
                        <option value="date-desc">最新添加</option>
                    </select>
                    <button class="submit-btn" @click="isModalOpen = true">
                        <span>+</span> 提交资源
                    </button>
                </div>
            </header>

            <!-- Loading State -->
            <div v-if="loading" class="loading-state">
                <div class="spinner"></div>
                <p>加载中...</p>
            </div>

            <!-- Resources Section -->
            <section v-else class="resources-section">
                <!-- Featured Resources -->
                <div v-if="featuredResources.length > 0" class="featured-section">
                    <h3 class="section-title">
                        <span class="featured-badge">✨ 精选资源</span>
                    </h3>
                    <div class="resources-grid">
                        <a v-for="resource in featuredResources" :key="resource.id" :href="resource.url" target="_blank"
                            class="resource-card featured">
                            <div class="card-header">
                                <img v-if="resource.logo_url" :src="resource.logo_url" class="resource-favicon"
                                    @error="$event.target.style.display = 'none'" />
                                <div v-else class="resource-icon">
                                    {{ resource.title.charAt(0).toUpperCase() }}
                                </div>
                                <span class="resource-arrow">↗</span>
                            </div>
                            <div class="card-body">
                                <h4 class="resource-name">{{ resource.title }}</h4>
                                <p class="resource-desc">{{ resource.description }}</p>
                            </div>
                            <div class="card-footer">
                                <span class="resource-category">{{ resource.category }}</span>
                                <div class="resource-tags">
                                    <span v-for="tag in resource.tags?.slice(0, 2)" :key="tag" class="tag">{{ tag
                                    }}</span>
                                </div>
                            </div>
                        </a>
                    </div>
                </div>

                <!-- Regular Resources -->
                <div v-if="regularResources.length > 0" class="regular-section">
                    <h3 v-if="featuredResources.length > 0" class="section-title">
                        <span class="regular-badge">所有资源</span>
                    </h3>
                    <div class="resources-grid">
                        <a v-for="resource in regularResources" :key="resource.id" :href="resource.url" target="_blank"
                            class="resource-card">
                            <div class="card-header">
                                <img v-if="resource.logo_url" :src="resource.logo_url" class="resource-favicon"
                                    @error="$event.target.style.display = 'none'" />
                                <div v-else class="resource-icon">
                                    {{ resource.title.charAt(0).toUpperCase() }}
                                </div>
                                <span class="resource-arrow">↗</span>
                            </div>
                            <div class="card-body">
                                <h4 class="resource-name">{{ resource.title }}</h4>
                                <p class="resource-desc">{{ resource.description }}</p>
                            </div>
                            <div class="card-footer">
                                <span class="resource-category">{{ resource.category }}</span>
                                <div class="resource-tags">
                                    <span v-for="tag in resource.tags?.slice(0, 2)" :key="tag" class="tag">{{ tag
                                    }}</span>
                                </div>
                            </div>
                        </a>
                    </div>
                </div>

                <div v-if="filteredResources.length === 0 && !loading" class="no-results">
                    <p>未找到匹配的资源</p>
                </div>
            </section>
        </main>

        <!-- Submission Modal -->
        <SubmitResourceModal :is-open="isModalOpen" :categories="categories.filter(c => c !== 'ALL')"
            @close="isModalOpen = false" @submit="handleSubmission" />

        <!-- Back to Top Button -->
        <Transition name="fade">
            <button v-if="showBackToTop" class="back-to-top" @click="scrollToTop" aria-label="回到顶部">
                ↑
            </button>
        </Transition>
    </div>
</template>

<style scoped>
.resources-page {
    display: flex;
    min-height: calc(100vh - 64px);
    font-family: "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Sidebar */
.sidebar {
    width: 240px;
    padding: 24px 16px;
    border-right: 1px solid var(--vp-c-divider);
    position: sticky;
    top: 64px;
    height: calc(100vh - 64px);
    overflow-y: auto;
    background: var(--vp-c-bg);
}

.sidebar-header h2 {
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--vp-c-text-3);
    margin: 0 0 16px 12px;
}

.category-nav {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.cat-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 12px;
    border: none;
    background: transparent;
    border-radius: 8px;
    cursor: pointer;
    color: var(--vp-c-text-2);
    font-size: 14px;
    font-weight: 500;
    transition: all 0.15s ease;
    text-align: left;
}

.cat-item:hover {
    background: var(--vp-c-bg-soft);
    color: var(--vp-c-text-1);
}

.cat-item.active {
    background: var(--vp-c-brand-soft);
    color: var(--vp-c-brand);
}

.cat-icon {
    font-size: 18px;
}

/* Main Content */
.main-content {
    flex: 1;
    padding: 24px 32px;
    max-width: calc(100% - 240px);
}

.content-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32px;
    gap: 16px;
}

.search-wrapper {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.search-container {
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 1;
    max-width: 480px;
    padding: 0 16px;
    border: 1px solid var(--vp-c-divider);
    border-radius: 12px;
    background: var(--vp-c-bg-soft);
    transition: all 0.2s ease;
}

.search-container:focus-within {
    border-color: var(--vp-c-brand);
    box-shadow: 0 0 0 3px var(--vp-c-brand-soft);
}

.search-icon {
    font-size: 14px;
    opacity: 0.6;
}

.resources-count {
    font-size: 12px;
    color: var(--vp-c-text-3);
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
}

.sort-select {
    padding: 10px 16px;
    font-size: 14px;
    border: 1px solid var(--vp-c-divider);
    border-radius: 10px;
    background: var(--vp-c-bg-soft);
    color: var(--vp-c-text-1);
    cursor: pointer;
    transition: all 0.2s ease;
}

.sort-select:hover {
    border-color: var(--vp-c-brand);
}

.clear-btn {
    padding: 4px 8px;
    font-size: 12px;
    background: transparent;
    border: none;
    color: var(--vp-c-text-3);
    cursor: pointer;
    transition: all 0.2s ease;
}

.clear-btn:hover {
    color: var(--vp-c-brand);
}

.search-input {
    flex: 1;
    padding: 12px 0;
    font-size: 14px;
    border: none;
    background: transparent;
    color: var(--vp-c-text-1);
    outline: none;
}

.search-input::placeholder {
    color: var(--vp-c-text-3);
}

.submit-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 12px 20px;
    font-size: 14px;
    font-weight: 600;
    color: white;
    background: var(--vp-c-brand);
    border: none;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
}

.submit-btn:hover {
    background: var(--vp-c-brand-dark);
    transform: translateY(-1px);
}

/* Sections */
.featured-section,
.regular-section {
    margin-bottom: 40px;
}

.section-title {
    margin: 0 0 16px 0;
    font-size: 14px;
}

.featured-badge {
    display: inline-block;
    padding: 4px 12px;
    background: linear-gradient(135deg, #fbbf24, #f59e0b);
    color: white;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

.regular-badge {
    display: inline-block;
    padding: 4px 12px;
    background: var(--vp-c-bg-soft);
    color: var(--vp-c-text-2);
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
}

/* Resources Grid */
.resources-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 20px;
}

.resource-card {
    background: linear-gradient(135deg, var(--vp-c-bg) 0%, var(--vp-c-bg-soft) 100%);
    border: 1px solid var(--vp-c-divider);
    border-radius: 16px;
    padding: 20px;
    text-decoration: none;
    color: var(--vp-c-text-1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    display: flex;
    flex-direction: column;
    min-height: 180px;
    position: relative;
    overflow: hidden;
    animation: fadeInUp 0.4s ease forwards;
}

.resource-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.08), transparent);
    transition: left 0.6s ease;
    pointer-events: none;
}

.resource-card:hover::before {
    left: 100%;
}

.resource-card:hover {
    border-color: var(--vp-c-brand);
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 20px 40px -12px rgba(139, 92, 246, 0.25);
}

.resource-card.featured {
    border-color: #fbbf24;
    background: linear-gradient(135deg, rgba(251, 191, 36, 0.05) 0%, var(--vp-c-bg-soft) 100%);
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 16px;
}

.resource-favicon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: var(--vp-c-bg-soft);
    object-fit: contain;
    padding: 4px;
}

.resource-icon {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-size: 24px;
    font-weight: 700;
    border-radius: 12px;
}

.resource-arrow {
    font-size: 16px;
    color: var(--vp-c-text-3);
    opacity: 0;
    transition: all 0.2s ease;
}

.resource-card:hover .resource-arrow {
    opacity: 1;
    color: var(--vp-c-brand);
}

.card-body {
    flex: 1;
}

.resource-name {
    margin: 0 0 8px 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--vp-c-text-1);
}

.resource-desc {
    margin: 0;
    font-size: 13px;
    line-height: 1.5;
    color: var(--vp-c-text-2);
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 16px;
    padding-top: 12px;
    border-top: 1px solid var(--vp-c-divider);
}

.resource-category {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--vp-c-text-3);
}

.resource-tags {
    display: flex;
    gap: 6px;
}

.tag {
    padding: 2px 8px;
    font-size: 11px;
    background: var(--vp-c-bg-soft);
    border-radius: 4px;
    color: var(--vp-c-text-2);
}

/* Loading & Empty States */
.loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 0;
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
    to {
        transform: rotate(360deg);
    }
}

.no-results {
    text-align: center;
    padding: 60px 0;
    color: var(--vp-c-text-3);
}

/* Responsive */
@media (max-width: 768px) {
    .resources-page {
        flex-direction: column;
    }

    .sidebar {
        width: 100%;
        height: auto;
        position: static;
        border-right: none;
        border-bottom: 1px solid var(--vp-c-divider);
        padding: 16px;
    }

    .category-nav {
        flex-direction: row;
        flex-wrap: wrap;
        gap: 8px;
    }

    .cat-item {
        padding: 8px 12px;
    }

    .cat-name {
        display: none;
    }

    .cat-icon {
        font-size: 20px;
    }

    .main-content {
        max-width: 100%;
        padding: 16px;
    }

    .content-header {
        flex-direction: column;
        align-items: stretch;
    }

    .search-container {
        max-width: 100%;
    }

    .submit-btn {
        justify-content: center;
    }

    .resources-grid {
        grid-template-columns: 1fr;
    }

    .header-actions {
        flex-direction: column;
        width: 100%;
    }

    .sort-select {
        width: 100%;
    }
}

/* Back to Top Button */
.back-to-top {
    position: fixed;
    bottom: 32px;
    right: 32px;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--vp-c-brand), var(--vp-c-brand-dark));
    color: white;
    border: none;
    font-size: 20px;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4);
    transition: all 0.3s ease;
    z-index: 100;
}

.back-to-top:hover {
    transform: translateY(-4px);
    box-shadow: 0 6px 30px rgba(139, 92, 246, 0.5);
}

.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>
