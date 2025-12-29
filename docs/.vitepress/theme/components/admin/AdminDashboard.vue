<script setup>
import { ref, onMounted } from 'vue'
import { createClient } from '@supabase/supabase-js'
import { withBase } from 'vitepress'

const stats = ref({
    tools: { total: 0, pending: 0 },
    resources: { total: 0 },
    prompts: { total: 0, pending: 0 },
    devResources: { total: 0 }
})
const loading = ref(true)

const fetchStats = async () => {
    try {
        const supabaseUrl = import.meta.env.SUPABASE_URL
        const supabaseKey = import.meta.env.SUPABASE_KEY

        if (!supabaseUrl || !supabaseKey) {
            console.warn('Supabase credentials missing')
            loading.value = false
            return
        }

        const supabase = createClient(supabaseUrl, supabaseKey)

        // AI Tools
        const { count: toolsTotal } = await supabase
            .from('ai_tools')
            .select('*', { count: 'exact', head: true })

        const { count: toolsPending } = await supabase
            .from('ai_tools')
            .select('*', { count: 'exact', head: true })
            .eq('approved', false)

        // Design Resources
        const { count: resourcesTotal } = await supabase
            .from('design_resources')
            .select('*', { count: 'exact', head: true })

        // AI Prompts
        const { count: promptsTotal } = await supabase
            .from('ai_prompts')
            .select('*', { count: 'exact', head: true })

        const { count: promptsPending } = await supabase
            .from('ai_prompts')
            .select('*', { count: 'exact', head: true })
            .eq('approved', false)

        // Dev Resources
        const { count: devResourcesTotal } = await supabase
            .from('dev_resources')
            .select('*', { count: 'exact', head: true })

        stats.value = {
            tools: { total: toolsTotal || 0, pending: toolsPending || 0 },
            resources: { total: resourcesTotal || 0 },
            prompts: { total: promptsTotal || 0, pending: promptsPending || 0 },
            devResources: { total: devResourcesTotal || 0 }
        }
    } catch (e) {
        console.error('Error fetching stats:', e)
    } finally {
        loading.value = false
    }
}

onMounted(fetchStats)
</script>

<template>
    <div class="dashboard-welcome">
        <h2>欢迎回来，管理员 👋</h2>
        <p>请从左侧菜单选择要管理的内容。</p>

        <div class="quick-stats">
            <div class="stat-card">
                <h3>AI 工具</h3>
                <div class="stat-numbers" v-if="!loading">
                    <div class="stat-item">
                        <span class="count">{{ stats.tools.total }}</span>
                        <span class="label">总数</span>
                    </div>
                    <div class="stat-item pending" v-if="stats.tools.pending > 0">
                        <span class="count">{{ stats.tools.pending }}</span>
                        <span class="label">待审核</span>
                    </div>
                </div>
                <div class="loading-stats" v-else>加载中...</div>
                <div class="card-action">
                    <a :href="withBase('/admin/tools')">去管理 →</a>
                </div>
            </div>

            <div class="stat-card">
                <h3>设计资源</h3>
                <div class="stat-numbers" v-if="!loading">
                    <div class="stat-item">
                        <span class="count">{{ stats.resources.total }}</span>
                        <span class="label">总数</span>
                    </div>
                </div>
                <div class="loading-stats" v-else>加载中...</div>
                <div class="card-action">
                    <a :href="withBase('/admin/resources')">去管理 →</a>
                </div>
            </div>

            <div class="stat-card">
                <h3>AI 提示词</h3>
                <div class="stat-numbers" v-if="!loading">
                    <div class="stat-item">
                        <span class="count">{{ stats.prompts.total }}</span>
                        <span class="label">总数</span>
                    </div>
                    <div class="stat-item pending" v-if="stats.prompts.pending > 0">
                        <span class="count">{{ stats.prompts.pending }}</span>
                        <span class="label">待审核</span>
                    </div>
                </div>
                <div class="loading-stats" v-else>加载中...</div>
                <div class="card-action">
                    <a :href="withBase('/admin/prompts')">去管理 →</a>
                </div>
            </div>

            <div class="stat-card">
                <h3>AI 开发</h3>
                <div class="stat-numbers" v-if="!loading">
                    <div class="stat-item">
                        <span class="count">{{ stats.devResources.total }}</span>
                        <span class="label">总数</span>
                    </div>
                </div>
                <div class="loading-stats" v-else>加载中...</div>
                <div class="card-action">
                    <a :href="withBase('/admin/dev-resources')">去管理 →</a>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.dashboard-welcome {
    padding: 20px;
}

.quick-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 20px;
    margin-top: 40px;
}

.stat-card {
    background: var(--vp-c-bg);
    border: 1px solid var(--vp-c-divider);
    border-radius: 12px;
    padding: 24px;
    transition: all 0.2s;
    display: flex;
    flex-direction: column;
}

.stat-card:hover {
    border-color: var(--vp-c-brand);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.stat-card h3 {
    margin: 0 0 16px 0;
    font-size: 18px;
    color: var(--vp-c-text-1);
}

.stat-numbers {
    display: flex;
    gap: 24px;
    margin-bottom: 20px;
}

.stat-item {
    display: flex;
    flex-direction: column;
}

.stat-item .count {
    font-size: 28px;
    font-weight: 700;
    color: var(--vp-c-text-1);
    line-height: 1.2;
}

.stat-item .label {
    font-size: 13px;
    color: var(--vp-c-text-2);
}

.stat-item.pending .count {
    color: #f59e0b;
}

.loading-stats {
    height: 60px;
    display: flex;
    align-items: center;
    color: var(--vp-c-text-3);
    font-size: 14px;
}

.card-action {
    margin-top: auto;
}

.card-action a {
    color: var(--vp-c-brand);
    font-weight: 600;
    text-decoration: none;
    font-size: 14px;
}

.card-action a:hover {
    text-decoration: underline;
}
</style>
