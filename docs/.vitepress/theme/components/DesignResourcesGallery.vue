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
const selectedResource = ref(null)

// Get or create Supabase client
const getSupabase = () => {
    if (!supabase) {
        if (!supabaseUrl || !supabaseKey) {
            console.error('Supabase credentials not found')
            return null
        }
        supabase = createClient(supabaseUrl, supabaseKey)
    }
    return supabase
}

// Fetch resources from Supabase
const fetchResources = async () => {
    const client = getSupabase()
    if (!client) {
        loading.value = false
        return
    }

    try {
        const { data, error } = await client
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
}

// Handle new submission
const handleSubmission = async (resource) => {
    const client = getSupabase()
    if (!client) return

    try {
        const { error } = await client
            .from('design_resources')
            .insert([resource])

        if (error) throw error

        alert('Resource submitted successfully!')
        isModalOpen.value = false
        await fetchResources()
    } catch (e) {
        console.error('Error submitting resource:', e)
        alert('Failed to submit resource. Please try again.')
    }
}

// Filtered resources
const filteredResources = computed(() => {
    return resources.value.filter(r => {
        const matchesCat = selectedCategory.value === 'ALL' || r.category === selectedCategory.value
        const matchesSearch = r.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
            r.description.toLowerCase().includes(searchQuery.value.toLowerCase())
        return matchesCat && matchesSearch
    })
})

// Featured resources
const featuredResources = computed(() => {
    return filteredResources.value.filter(r => r.is_featured)
})

// Regular resources
const regularResources = computed(() => {
    return filteredResources.value.filter(r => !r.is_featured)
})

onMounted(() => {
    fetchResources()
})
</script>

<template>
    <div class="design-resources-gallery">
        <!-- Header -->
        <div class="gallery-header">
            <h1 class="gallery-title">前端设计资源</h1>
            <p class="gallery-subtitle">精选的 UI/UX 设计工具和资源导航</p>
        </div>

        <!-- Controls -->
        <div class="controls">
            <!-- Search -->
            <div class="search-box">
                <input v-model="searchQuery" type="text" placeholder="搜索资源..." class="search-input" />
            </div>

            <!-- Categories -->
            <div class="category-tabs">
                <button v-for="cat in categories" :key="cat" class="category-tab"
                    :class="{ active: selectedCategory === cat }" @click="selectedCategory = cat">
                    {{ cat }}
                </button>
            </div>

            <!-- Submit Button -->
            <div class="action-row">
                <button class="submit-btn" @click="isModalOpen = true">
                    + 提交资源
                </button>
            </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="status-msg">加载中...</div>

        <!-- Empty State -->
        <div v-else-if="filteredResources.length === 0" class="status-msg">
            未找到匹配的资源
        </div>

        <!-- Resources Grid -->
        <div v-else class="resources-container">
            <!-- Featured Resources -->
            <div v-if="featuredResources.length > 0" class="featured-section">
                <h2 class="section-title">✨ 精选资源</h2>
                <div class="resources-grid">
                    <div v-for="resource in featuredResources" :key="resource.id" class="resource-card featured"
                        @click="selectedResource = resource">
                        <div class="card-header">
                            <img v-if="resource.logo_url" :src="resource.logo_url" :alt="resource.title"
                                class="resource-logo" @error="(e) => e.target.style.display = 'none'" />
                            <div class="resource-icon" v-else>
                                {{ resource.title.charAt(0).toUpperCase() }}
                            </div>
                        </div>
                        <div class="card-body">
                            <h3 class="resource-title">{{ resource.title }}</h3>
                            <p class="resource-description">{{ resource.description }}</p>
                            <div class="resource-meta">
                                <span class="resource-category">{{ resource.category }}</span>
                                <span v-for="tag in resource.tags" :key="tag" class="resource-tag">
                                    {{ tag }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Regular Resources -->
            <div class="regular-section">
                <h2 v-if="featuredResources.length > 0" class="section-title">所有资源</h2>
                <div class="resources-grid">
                    <div v-for="resource in regularResources" :key="resource.id" class="resource-card"
                        @click="selectedResource = resource">
                        <div class="card-header">
                            <img v-if="resource.logo_url" :src="resource.logo_url" :alt="resource.title"
                                class="resource-logo" @error="(e) => e.target.style.display = 'none'" />
                            <div class="resource-icon" v-else>
                                {{ resource.title.charAt(0).toUpperCase() }}
                            </div>
                        </div>
                        <div class="card-body">
                            <h3 class="resource-title">{{ resource.title }}</h3>
                            <p class="resource-description">{{ resource.description }}</p>
                            <div class="resource-meta">
                                <span class="resource-category">{{ resource.category }}</span>
                                <span v-for="tag in resource.tags" :key="tag" class="resource-tag">
                                    {{ tag }}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Detail Modal -->
        <Teleport to="body">
            <Transition name="modal">
                <div v-if="selectedResource" class="modal-overlay" @click="selectedResource = null">
                    <div class="modal-panel" @click.stop>
                        <button class="modal-close" @click="selectedResource = null">×</button>

                        <div class="modal-header">
                            <img v-if="selectedResource.logo_url" :src="selectedResource.logo_url"
                                :alt="selectedResource.title" class="modal-logo"
                                @error="(e) => e.target.style.display = 'none'" />
                            <div class="modal-icon" v-else>
                                {{ selectedResource.title.charAt(0).toUpperCase() }}
                            </div>
                            <div class="modal-title-group">
                                <h2 class="modal-title">{{ selectedResource.title }}</h2>
                                <span class="modal-category">{{ selectedResource.category }}</span>
                            </div>
                        </div>

                        <div class="modal-body">
                            <p class="modal-description">{{ selectedResource.description }}</p>

                            <div class="modal-tags">
                                <span v-for="tag in selectedResource.tags" :key="tag" class="modal-tag">
                                    {{ tag }}
                                </span>
                            </div>

                            <a :href="selectedResource.url" target="_blank" rel="noopener noreferrer"
                                class="modal-visit-btn">
                                访问资源 →
                            </a>

                            <div class="modal-meta">
                                <span class="meta-item">来源: {{ selectedResource.source }}</span>
                                <span class="meta-item">添加于: {{ new
                                    Date(selectedResource.created_at).toLocaleDateString('zh-CN') }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </Transition>
        </Teleport>

        <!-- Submit Modal -->
        <SubmitResourceModal :is-open="isModalOpen" :categories="categories.filter(c => c !== 'ALL')"
            @close="isModalOpen = false" @submit="handleSubmission" />
    </div>
</template>

<style scoped>
.design-resources-gallery {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem 1rem;
}

.gallery-header {
    text-align: center;
    margin-bottom: 3rem;
}

.gallery-title {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.gallery-subtitle {
    font-size: 1.2rem;
    color: var(--vp-c-text-2);
}

.controls {
    margin-bottom: 2rem;
}

.search-box {
    margin-bottom: 1.5rem;
}

.search-input {
    width: 100%;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    border: 2px solid var(--vp-c-divider);
    border-radius: 8px;
    transition: border-color 0.3s;
}

.search-input:focus {
    outline: none;
    border-color: #667eea;
}

.category-tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
}

.category-tab {
    padding: 0.5rem 1rem;
    border: 2px solid var(--vp-c-divider);
    border-radius: 20px;
    background: transparent;
    cursor: pointer;
    transition: all 0.3s;
    font-size: 0.9rem;
}

.category-tab:hover {
    border-color: #667eea;
    color: #667eea;
}

.category-tab.active {
    background: #667eea;
    color: white;
    border-color: #667eea;
}

.action-row {
    display: flex;
    justify-content: flex-end;
}

.submit-btn {
    padding: 0.75rem 1.5rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 600;
    transition: transform 0.2s;
}

.submit-btn:hover {
    transform: translateY(-2px);
}

.status-msg {
    text-align: center;
    padding: 3rem;
    color: var(--vp-c-text-2);
    font-size: 1.1rem;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1.5rem;
    color: var(--vp-c-text-1);
}

.featured-section {
    margin-bottom: 3rem;
}

.resources-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
}

.resource-card {
    background: var(--vp-c-bg-soft);
    border: 2px solid var(--vp-c-divider);
    border-radius: 12px;
    padding: 1.5rem;
    cursor: pointer;
    transition: all 0.3s;
}

.resource-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    border-color: #667eea;
}

.resource-card.featured {
    border-color: #ffd700;
    background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(255, 215, 0, 0.05) 100%);
}

.card-header {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1rem;
}

.resource-logo {
    width: 64px;
    height: 64px;
    object-fit: contain;
    border-radius: 8px;
}

.resource-icon {
    width: 64px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-size: 2rem;
    font-weight: 700;
    border-radius: 8px;
}

.card-body {
    text-align: center;
}

.resource-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: var(--vp-c-text-1);
}

.resource-description {
    font-size: 0.9rem;
    color: var(--vp-c-text-2);
    margin-bottom: 1rem;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.resource-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
}

.resource-category {
    padding: 0.25rem 0.75rem;
    background: #667eea;
    color: white;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
}

.resource-tag {
    padding: 0.25rem 0.75rem;
    background: var(--vp-c-bg-mute);
    color: var(--vp-c-text-2);
    border-radius: 12px;
    font-size: 0.75rem;
}

/* Modal Styles */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    padding: 1rem;
}

.modal-panel {
    background: var(--vp-c-bg);
    border-radius: 16px;
    max-width: 600px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    position: relative;
    padding: 2rem;
}

.modal-close {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 32px;
    height: 32px;
    border: none;
    background: var(--vp-c-bg-soft);
    border-radius: 50%;
    font-size: 1.5rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.3s;
}

.modal-close:hover {
    background: var(--vp-c-bg-mute);
}

.modal-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

.modal-logo {
    width: 80px;
    height: 80px;
    object-fit: contain;
    border-radius: 12px;
}

.modal-icon {
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-size: 2.5rem;
    font-weight: 700;
    border-radius: 12px;
}

.modal-title-group {
    flex: 1;
}

.modal-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: var(--vp-c-text-1);
}

.modal-category {
    padding: 0.25rem 0.75rem;
    background: #667eea;
    color: white;
    border-radius: 12px;
    font-size: 0.85rem;
    font-weight: 600;
}

.modal-body {
    padding-top: 1rem;
}

.modal-description {
    font-size: 1rem;
    line-height: 1.6;
    color: var(--vp-c-text-2);
    margin-bottom: 1.5rem;
}

.modal-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
}

.modal-tag {
    padding: 0.5rem 1rem;
    background: var(--vp-c-bg-soft);
    color: var(--vp-c-text-2);
    border-radius: 16px;
    font-size: 0.9rem;
}

.modal-visit-btn {
    display: block;
    width: 100%;
    padding: 1rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-align: center;
    text-decoration: none;
    border-radius: 8px;
    font-weight: 600;
    font-size: 1rem;
    margin-bottom: 1.5rem;
    transition: transform 0.2s;
}

.modal-visit-btn:hover {
    transform: translateY(-2px);
}

.modal-meta {
    display: flex;
    justify-content: space-between;
    padding-top: 1rem;
    border-top: 1px solid var(--vp-c-divider);
    font-size: 0.85rem;
    color: var(--vp-c-text-3);
}

.modal-enter-active,
.modal-leave-active {
    transition: opacity 0.3s;
}

.modal-enter-from,
.modal-leave-to {
    opacity: 0;
}

@media (max-width: 768px) {
    .gallery-title {
        font-size: 2rem;
    }

    .resources-grid {
        grid-template-columns: 1fr;
    }

    .modal-panel {
        padding: 1.5rem;
    }
}
</style>
