<script setup>
import { ref, computed, onMounted } from 'vue'
import { createClient } from '@supabase/supabase-js'
import BaseIcon from './BaseIcon.vue'
import SubmitResourceModal from './SubmitResourceModal.vue'

// Supabase Client (lazy initialization for SSR compatibility)
const supabaseUrl = import.meta.env.SUPABASE_URL
const supabaseKey = import.meta.env.SUPABASE_KEY
let supabase = null

const resources = ref([])
const loading = ref(true)
const loadError = ref('')
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
        loadError.value = '资源数据源未配置，请联系站点管理员。'
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
        loadError.value = '资源数据暂时无法加载，请检查网络连接或稍后重试。'
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
const matchesQuery = resource => {
    const query = searchQuery.value.trim().toLowerCase()
    return !query || resource.title?.toLowerCase().includes(query) || resource.description?.toLowerCase().includes(query) || resource.tags?.some(tag => tag.toLowerCase().includes(query))
}
const categoryCount = category => resources.value.filter(resource => matchesQuery(resource) && (category === 'ALL' || resource.category === category)).length
const clearFilters = () => { selectedCategory.value = 'ALL'; searchQuery.value = '' }
</script>

<template>
<div class="editorial-directory">
<header class="directory-intro"><div><span class="eyebrow">DESIGN DIRECTORY</span><h1>设计资源</h1><p>精选的 UI/UX 设计工具和资源导航</p></div><label class="search-container"><BaseIcon name="Search" :size="20"/><input v-model="searchQuery" type="search" placeholder="搜索资源、功能或标签…" aria-label="搜索设计资源"/><button v-if="searchQuery" @click.prevent="clearSearch" aria-label="清除搜索">清除</button></label></header>
<nav class="category-nav" aria-label="资源分类"><button v-for="cat in categories" :key="cat" :class="{active: selectedCategory === cat}" :aria-pressed="selectedCategory === cat" @click="selectedCategory = cat">{{ cat === 'ALL' ? '全部 All' : cat }}</button></nav>
<div class="directory-layout"><aside class="filters"><div class="filter-heading"><h2>筛选 <small>Filters</small></h2><button @click="clearFilters">清除全部</button></div><fieldset><legend>分类 <small>Category</small></legend><label v-for="cat in categories" :key="cat" class="filter-option"><input type="radio" name="resource-category" :value="cat" v-model="selectedCategory"/><span>{{ cat === 'ALL' ? '全部 All' : cat }}</span><span class="filter-count">({{ categoryCount(cat) }})</span></label></fieldset></aside>
<main class="results"><div class="results-bar"><p>{{ loading ? '正在加载资源…' : loadError ? '数据暂不可用' : `共找到 ${filteredResources.length} 个资源` }}</p><div class="actions"><span v-if="searchQuery.trim()" class="query">搜索：{{ searchQuery }} <button @click="clearSearch">清除</button></span><label>排序 <select v-model="sortBy" aria-label="排序"><option value="default">默认排序</option><option value="name-asc">名称 A-Z</option><option value="name-desc">名称 Z-A</option><option value="date-desc">最新添加</option></select></label><button class="submit-btn" @click="isModalOpen = true"><BaseIcon name="Plus" :size="16"/> 提交资源</button></div></div>
<div v-if="loading" class="state">正在加载资源…</div><div v-else-if="loadError" class="state" role="alert">{{ loadError }}</div><div v-else-if="!filteredResources.length" class="state"><p>未找到匹配的资源</p><button @click="clearFilters">清除筛选</button></div>
<section v-else aria-label="资源列表"><article v-for="resource in filteredResources" :key="resource.id" class="resource-row"><div class="resource-logo"><BaseIcon name="ALL" :size="30"/><img v-if="resource.logo_url" :src="resource.logo_url" alt="" @error="$event.target.style.visibility = 'hidden'"/></div><div class="resource-body"><h2><a :href="resource.url" target="_blank" rel="noopener noreferrer">{{ resource.title }} <BaseIcon name="ArrowUpRight" :size="15"/></a></h2><p>{{ resource.description }}</p><div class="tags"><span class="tag">{{ resource.category }}</span><span v-if="resource.language" class="tag">{{ resource.language }}</span><span v-if="resource.license" class="tag">{{ resource.license }}</span><span v-for="tag in resource.tags?.slice(0, 3)" :key="tag" class="tag">{{ tag }}</span></div></div><div class="resource-actions"><span v-if="resource.is_featured" class="featured">精选</span><a :href="resource.url" target="_blank" rel="noopener noreferrer" class="visit">访问资源 <BaseIcon name="ArrowUpRight" :size="15"/></a><a v-if="resource.github_url" :href="resource.github_url" target="_blank" rel="noopener noreferrer" class="github">GitHub</a></div></article></section></main></div>
<SubmitResourceModal :is-open="isModalOpen" :categories="categories.filter(c => c !== 'ALL')" @close="isModalOpen = false" @submit="handleSubmission" />
<button v-if="showBackToTop" class="back-to-top" @click="scrollToTop">返回顶部</button>
</div>
</template>
<style scoped src="./editorial-resources.css"></style>
