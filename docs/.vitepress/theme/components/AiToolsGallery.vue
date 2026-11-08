<script setup>
import { ref, computed, onMounted } from 'vue'
import { createClient } from '@supabase/supabase-js'
import SubmitToolModal from './SubmitToolModal.vue'
import BaseIcon from './BaseIcon.vue'

// Supabase Client (lazy initialization for SSR compatibility)
const supabaseUrl = import.meta.env.SUPABASE_URL
const supabaseKey = import.meta.env.SUPABASE_KEY
let supabase = null

const isAtlas = false
const atlasImage = import.meta.env.BASE_URL + 'ai-tools-atlas.png'
const tools = ref([])
const pendingTools = ref([])
const loading = ref(true)
const loadError = ref('')
const categories = ['ALL', 'Coding', 'Image', 'Video', 'Writing', 'Audio', 'Productivity']
const selectedCategory = ref('ALL')
const selectedPrices = ref([])
const prices = ['Free', 'Paid', 'Freemium']
const categoryLabels = { ALL: '全部', Coding: '编程', Image: '图像', Video: '视频', Writing: '写作', Audio: '音频', Productivity: '效率' }
const priceLabels = { Free: '免费', Paid: '付费', Freemium: '免费增值' }
const hasPrice = (tool, price) => (tool.tags || []).some(tag => tag.toLowerCase() === price.toLowerCase())
// Facet counts include the other active filters, but exclude the facet itself.
const matchesQuery = tool => {
  const query = searchQuery.value.toLowerCase().trim()
  return !query || tool.name?.toLowerCase().includes(query) ||
    tool.desc?.toLowerCase().includes(query) ||
    tool.tags?.some(tag => tag.toLowerCase().includes(query))
}
const matchesPrices = tool => !selectedPrices.value.length || selectedPrices.value.some(price => hasPrice(tool, price))
const priceCount = price => tools.value.filter(tool => matchesQuery(tool) && (selectedCategory.value === 'ALL' || tool.category === selectedCategory.value) && hasPrice(tool, price)).length
const categoryCount = category => tools.value.filter(tool => matchesQuery(tool) && matchesPrices(tool) && (category === 'ALL' || tool.category === category)).length
const clearFilters = () => { selectedCategory.value = 'ALL'; selectedPrices.value = []; searchQuery.value = '' }

const searchQuery = ref('')
const isModalOpen = ref(false)
const showPending = ref(false)
const showBackToTop = ref(false)
const sortBy = ref('default') // 'default' | 'name-asc' | 'name-desc'

// Compute popular tags
const popularTags = computed(() => {
  const tagCounts = {}
  tools.value.forEach(tool => {
    if (tool.tags) {
      tool.tags.forEach(tag => {
        tagCounts[tag] = (tagCounts[tag] || 0) + 1
      })
    }
  })

  return Object.entries(tagCounts)
    .sort((a, b) => b[1] - a[1]) // Sort by count desc
    .slice(0, 10) // Top 10
    .map(([tag]) => tag)
})

// Scroll event handler for back to top button
const handleScroll = () => {
  if (typeof window !== 'undefined') {
    showBackToTop.value = window.scrollY > 300
  }
}

// Scroll to top function
const scrollToTop = () => {
  if (typeof window !== 'undefined') {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const reloadTools = () => window.location.reload()

// Clear search
const clearSearch = () => {
  searchQuery.value = ''
}

// Get favicon URL from website link
const getFavicon = (url) => {
  try {
    const domain = new URL(url).hostname
    return `https://www.google.com/s2/favicons?domain=${domain}&sz=128`
  } catch {
    return null
  }
}

// Load pending submissions from localStorage
const loadPendingSubmissions = () => {
  try {
    const stored = localStorage.getItem('vitemind_user_submissions')
    if (stored) {
      pendingTools.value = JSON.parse(stored)
    }
  } catch (e) {
    console.error('Error loading pending submissions:', e)
  }
}

// Handle new submission
const handleSubmission = (tool) => {
  pendingTools.value.unshift(tool)
  localStorage.setItem('vitemind_user_submissions', JSON.stringify(pendingTools.value))
}

// Fetch approved tools from Supabase
onMounted(async () => {
  loadPendingSubmissions()

  // Only run client-side code
  if (typeof window === 'undefined') {
    loading.value = false
    return
  }

  window.addEventListener('scroll', handleScroll)

  // Initialize Supabase client on client side
  if (supabaseUrl && supabaseKey) {
    supabase = createClient(supabaseUrl, supabaseKey)
  }

  // Only fetch if supabase is initialized
  if (!supabase) {
    loadError.value = '工具数据源未配置，请联系站点管理员。'
    loading.value = false
    return
  }

  try {
    loading.value = true
    const { data, error } = await supabase
      .from('ai_tools')
      .select('*')
      .eq('approved', true)
      .order('submitted_at', { ascending: false })

    if (error) throw error

    if (data) {
      tools.value = data.map(item => ({
        category: item.category || 'Productivity',
        name: item.name,
        desc: item.description,
        link: item.link,
        tags: item.tags || []
      }))

      // Cleanup pending tools that have been approved
      if (pendingTools.value.length > 0) {
        const approvedLinks = new Set(tools.value.map(t => t.link))
        const initialCount = pendingTools.value.length

        pendingTools.value = pendingTools.value.filter(t => !approvedLinks.has(t.link))

        if (pendingTools.value.length < initialCount) {
          localStorage.setItem('vitemind_user_submissions', JSON.stringify(pendingTools.value))
        }
      }
    }
  } catch (e) {
    console.error('Error fetching tools:', e)
    loadError.value = '工具数据暂时无法加载，请检查网络连接或稍后重试。'
  } finally {
    loading.value = false
  }
})

const filteredTools = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  let result = tools.value.filter(t => {
    const matchesCat = selectedCategory.value === 'ALL' || t.category === selectedCategory.value
    const matchesSearch = !query ||
      t.name?.toLowerCase().includes(query) ||
      t.desc?.toLowerCase().includes(query) ||
      t.tags?.some(tag => tag.toLowerCase().includes(query))
    return matchesCat && matchesSearch && (!selectedPrices.value.length || selectedPrices.value.some(price => hasPrice(t, price)))
  })

  // Apply sorting
  if (sortBy.value === 'name-asc') {
    result = [...result].sort((a, b) => a.name.localeCompare(b.name))
  } else if (sortBy.value === 'name-desc') {
    result = [...result].sort((a, b) => b.name.localeCompare(a.name))
  }

  return result
})

const filteredPending = computed(() => {
  const query = searchQuery.value.toLowerCase().trim()
  return pendingTools.value.filter(t => {
    const matchesCat = selectedCategory.value === 'ALL' || t.category === selectedCategory.value
    const matchesSearch = !query ||
      t.name?.toLowerCase().includes(query) ||
      t.desc?.toLowerCase().includes(query) ||
      t.tags?.some(tag => tag.toLowerCase().includes(query))
    return matchesCat && matchesSearch && (!selectedPrices.value.length || selectedPrices.value.some(price => hasPrice(t, price)))
  })
})
</script>

<template>
<div class="directory">
  <header class="directory-intro">
    <div><span class="eyebrow">TOOLS DIRECTORY</span><h1>AI Tools</h1><p class="intro-title">AI 工具索引 · 发现、比较与了解适合你的 AI 工具</p><p class="intro-en">A directory to discover and compare AI tools.</p></div>
    <div class="intro-search"><label class="search-container"><BaseIcon name="Search" :size="20"/><input v-model="searchQuery" type="search" placeholder="搜索工具、功能或使用场景…" aria-label="搜索 AI 工具" /></label><div class="search-hint">热门标签： <button v-for="tag in popularTags.slice(0, 6)" :key="tag" @click="searchQuery = tag">{{ tag }}</button></div></div>
  </header>
  <nav class="category-nav" aria-label="工具分类"><button v-for="cat in categories" :key="cat" class="cat-item" :class="{ active: selectedCategory === cat }" :aria-pressed="selectedCategory === cat" @click="selectedCategory = cat"><BaseIcon :name="cat" :size="20"/><span>{{ categoryLabels[cat] }} <small>{{ cat === 'ALL' ? 'All' : cat }}</small></span></button></nav>
  <div class="directory-layout"><aside class="filters"><div class="filter-heading"><h2>筛选 <small>Filters</small></h2><button @click="clearFilters">清除全部</button></div>
    <fieldset class="filter-group"><legend>定价模式 <small>Pricing</small></legend><label v-for="price in prices" :key="price" class="filter-option"><input type="checkbox" :value="price" v-model="selectedPrices"/><span>{{ priceLabels[price] }} <small>{{ price }}</small></span><span class="filter-count">({{ priceCount(price) }})</span></label></fieldset>
    <fieldset class="filter-group"><legend>分类 <small>Category</small></legend><label class="filter-option"><input type="radio" name="category" value="ALL" v-model="selectedCategory"/><span>全部 <small>All</small></span><span class="filter-count">({{ categoryCount('ALL') }})</span></label><label v-for="cat in categories.slice(1)" :key="cat" class="filter-option"><input type="radio" name="category" :value="cat" v-model="selectedCategory"/><span>{{ categoryLabels[cat] }} <small>{{ cat }}</small></span><span class="filter-count">({{ categoryCount(cat) }})</span></label></fieldset>
    <div v-if="popularTags.length" class="filter-group tag-section"><h3>热门标签 <small>Tags</small></h3><div class="tags-cloud"><button v-for="tag in popularTags.filter(tag => !prices.includes(tag))" :key="tag" class="tag-chip" @click="searchQuery = tag">#{{ tag }}</button></div></div><button v-if="pendingTools.length" class="pending-btn" @click="showPending = !showPending">待审核 ({{ pendingTools.length }})</button>
  </aside>
  <main class="results"><div class="results-bar"><p>{{ loadError ? '数据暂不可用' : `共找到 ${filteredTools.length} 个 AI 工具` }}</p><div><span v-if="searchQuery.trim()" class="active-query">搜索：{{ searchQuery }} <button @click="clearSearch" aria-label="清除搜索">清除</button></span><label>排序 <select v-model="sortBy" aria-label="排序"><option value="default">默认排序</option><option value="name-asc">名称 A-Z</option><option value="name-desc">名称 Z-A</option></select></label><button class="submit-btn" @click="isModalOpen = true"><BaseIcon name="Plus" :size="16"/> 提交工具</button></div></div>
  <section v-if="showPending && filteredPending.length" class="pending-section"><h2>待审核</h2><div class="tools-grid"><a v-for="tool in filteredPending" :key="tool.link" :href="tool.link" target="_blank" rel="noopener noreferrer" class="pending-card">{{ tool.name }} · {{ tool.desc || tool.description }}</a></div></section>
  <div v-if="loading" class="state">正在加载 AI 工具…</div><div v-else-if="loadError" class="state" role="alert"><p>{{ loadError }}</p><button @click="reloadTools">重新加载</button></div><section v-else><div class="tools-grid"><article v-for="tool in filteredTools" :key="tool.link" class="tool-card"><img :src="getFavicon(tool.link)" alt="" class="tool-favicon" @error="$event.target.style.visibility = 'hidden'"/><div class="card-body"><h3><a :href="tool.link" target="_blank" rel="noopener noreferrer">{{ tool.name }} <BaseIcon name="ArrowUpRight" :size="15"/></a></h3><p>{{ tool.desc }}</p><div class="card-tags"><span class="category-tag">{{ categoryLabels[tool.category] || tool.category }} {{ tool.category }}</span><span v-for="tag in tool.tags?.filter(t => !prices.includes(t)).slice(0, 3)" :key="tag" class="tag">{{ tag }}</span></div></div><div class="card-action"><span v-for="price in prices.filter(price => hasPrice(tool, price))" :key="price" class="price-badge">{{ price }}</span><span v-if="!prices.some(price => hasPrice(tool, price))" class="price-unknown">定价信息未标注</span><a :href="tool.link" target="_blank" rel="noopener noreferrer" class="visit-btn">访问官网 <BaseIcon name="ArrowUpRight" :size="15"/></a></div></article></div><div v-if="!filteredTools.length" class="state"><p>没有找到匹配的工具。</p><button @click="clearFilters">清除筛选</button></div></section></main></div>
  <SubmitToolModal :is-open="isModalOpen" :categories="categories.filter(c => c !== 'ALL')" @close="isModalOpen = false" @submit="handleSubmission" />
  <button v-if="showBackToTop" class="back-to-top" @click="scrollToTop" aria-label="回到顶部">返回顶部</button>
</div>
</template><style scoped>
.directory{--accent:#173aaa;--paper:#faf7f1;--ink:#20242d;--line:#d8d8d3;max-width:1600px;margin:auto;padding:42px 38px 80px;background:var(--paper);color:var(--ink);min-height:90vh}.directory button{cursor:pointer}.directory-intro{display:grid;grid-template-columns:1fr 1.35fr;gap:50px;align-items:end;padding:12px 0 34px}.eyebrow{font-size:12px;letter-spacing:.18em;color:var(--accent);font-weight:700}.directory h1{font-family:Georgia,serif;font-size:clamp(48px,5vw,76px);line-height:1.1;letter-spacing:-.04em;margin:10px 0}.directory-intro p{font-size:17px;margin:0}.intro-search span{display:block;color:#6d727c;font-size:12px;margin-top:10px}.search-container{height:52px;display:flex;align-items:center;gap:12px;border:1px solid #8e939f;background:white;padding:0 16px}.search-container:focus-within{outline:2px solid var(--accent)}.search-container input{width:100%;outline:none;background:transparent;font-size:15px;color:#20242d}.category-nav{display:flex;overflow-x:auto;border-bottom:1px solid #818691;gap:4px}.cat-item{display:flex;gap:9px;align-items:center;white-space:nowrap;padding:14px 22px;color:var(--ink);font-weight:600}.cat-item.active{background:var(--accent);color:white}.directory-layout{display:grid;grid-template-columns:260px 1fr;gap:28px;padding-top:26px}.filters{border-right:1px solid var(--line);padding-right:25px}.filter-heading{display:flex;align-items:center;justify-content:space-between}.filter-heading h2{font-size:20px;margin:0}.filter-heading button{color:var(--accent);font-size:12px}.filter-group{border-top:1px solid var(--line);margin-top:20px;padding-top:20px}.filter-group h3{font-size:14px;margin:0 0 14px}.filter-link{display:block;width:100%;text-align:left;padding:7px 0;color:#565d69}.filter-link.chosen{color:var(--accent);font-weight:700}.tags-cloud{display:flex;flex-wrap:wrap;gap:6px}.tag-chip,.tag,.category-tag{font-size:11px;border-radius:4px;background:#e8eaf0;color:#535d70;padding:4px 8px}.tag-chip:hover{color:var(--accent)}.pending-btn{margin-top:18px;color:var(--accent)}.results-bar{display:flex;justify-content:space-between;align-items:center;gap:15px;border-bottom:1px solid var(--line);padding-bottom:16px}.results-bar p{font-weight:600;margin:0}.results-bar>div{display:flex;gap:10px}.results-bar select,.submit-btn{padding:9px 13px;border:1px solid #aeb4bf;background:transparent;border-radius:4px;font-size:13px}.submit-btn{background:var(--accent);border-color:var(--accent);color:white}.tool-card{display:flex;gap:20px;padding:22px 0;border-bottom:1px solid var(--line);text-decoration:none;color:inherit}.tool-card:hover h3{color:var(--accent)}.tool-favicon{width:66px;height:66px;object-fit:contain;border-radius:10px;background:white;flex:none}.card-body{min-width:0}.card-body h3{font-family:Georgia,serif;font-size:24px;margin:0 0 5px;line-height:1.2}.card-body h3 svg{color:var(--accent)}.card-body p{font-size:14px;line-height:1.6;color:#555d69;margin:0 0 12px;max-width:840px}.card-tags{display:flex;flex-wrap:wrap;gap:6px}.category-tag{color:var(--accent);font-weight:700;background:#e3e9f9}.state{padding:70px 10px;text-align:center;color:#687080}.state button{margin-top:12px;color:var(--accent)}.back-to-top{position:fixed;right:25px;bottom:25px;background:var(--accent);color:white;padding:10px 15px;border-radius:4px}.atlas-art{display:none}
@media(max-width:800px){.directory{padding:28px 18px 60px}.directory-intro{grid-template-columns:1fr;gap:20px}.category-nav{margin:0 -18px;padding:0 18px}.cat-item{padding:12px 16px}.directory-layout{grid-template-columns:1fr}.filters{border:0;padding:0}.filter-group{margin-top:12px;padding-top:12px}.filter-link{display:inline-block;width:auto;margin-right:18px}.results-bar{flex-wrap:wrap}.tool-favicon{width:48px;height:48px}.card-body h3{font-size:20px}}

.directory{padding-top:24px;font-family:Georgia,"Songti SC",serif}.directory-intro{padding:0 0 24px;align-items:center}.eyebrow{font-size:14px}.directory h1{font-size:clamp(52px,5vw,78px);font-weight:700;margin:3px 0}.directory-intro .intro-title{font-size:18px;font-weight:700}.directory-intro .intro-en{font-size:13px;margin-top:3px}.intro-search .search-hint{font-size:13px;color:var(--ink);margin-top:10px}.search-hint button{margin-right:12px}.search-container{background:transparent;border-radius:5px}.cat-item{flex:1;justify-content:center;font-size:16px}.cat-item small,.filter-group small,.filter-heading small{font-size:.8em;font-weight:400;margin-left:5px}.directory-layout{grid-template-columns:290px 1fr;gap:24px}.filter-heading h2{font-size:20px;font-weight:700}.filter-group{min-width:0;border:0;border-top:1px solid var(--line);padding:15px 0 0;margin:18px 0 0}.filter-group legend{float:none;width:auto;font-size:16px;font-weight:700;margin-bottom:10px;padding-right:10px}.filter-option input{color-scheme:light}.filter-option{display:flex;align-items:center;gap:10px;padding:5px 0;font-size:14px}.filter-option input{accent-color:var(--accent);width:16px;height:16px}.filter-count{margin-left:auto;color:#5b5b5b}.filter-group h3{font-size:16px}.results-bar p{font-size:17px}.active-query{font-size:12px;color:#4c566b;align-self:center}.active-query button{color:var(--accent);margin-left:4px}.results-bar label{display:flex;align-items:center;gap:8px;font-size:13px}.tool-card{display:grid;grid-template-columns:88px minmax(0,1fr) 190px;gap:20px;padding:18px 0}.tool-favicon{width:88px;height:88px;padding:5px;border:1px solid #e1ded8}.card-body h3{font-size:25px;font-weight:700}.card-body h3 a{color:inherit;text-decoration:none}.card-body p{color:#272727;line-height:1.5}.category-tag,.tag{border-radius:20px;color:#303a50;background:#e8eaf0}.card-action{display:flex;flex-direction:column;align-items:flex-start;gap:10px}.price-badge{background:#f7e6ce;border-radius:5px;padding:3px 10px;color:#68411d;font-weight:700;font-size:13px}.price-unknown{color:#6b6b6b;font-size:12px}.visit-btn{display:inline-flex;align-items:center;gap:6px;background:var(--accent);color:white;text-decoration:none;padding:8px 14px;border-radius:5px;font-size:13px}.pending-card{display:block;padding:12px 0}.directory button:focus-visible,.directory a:focus-visible,.directory input:focus-visible,.directory select:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
@media(max-width:1000px){.tool-card{grid-template-columns:64px minmax(0,1fr);gap:14px}.tool-favicon{width:64px;height:64px}.card-action{grid-column:2;flex-direction:row;align-items:center}.cat-item{padding:12px}.directory-layout{grid-template-columns:230px 1fr}}
@media(max-width:800px){.directory-layout{grid-template-columns:1fr}.filters{border:0}.filter-group{display:flex;flex-wrap:wrap;gap:4px 16px}.filter-group legend{float:none}.filter-option{min-width:115px}.filter-count{margin-left:2px}.cat-item{flex:none}.directory-intro{gap:15px}.results-bar{align-items:flex-start}.results-bar>div{flex-wrap:wrap}.card-action{grid-column:2}.tool-card{grid-template-columns:52px minmax(0,1fr)}.tool-favicon{width:52px;height:52px}}
</style>