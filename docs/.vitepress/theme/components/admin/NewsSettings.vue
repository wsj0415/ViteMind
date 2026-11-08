<script setup>
import { onMounted, ref } from 'vue'
import { createClient } from '@supabase/supabase-js'

const loading = ref(true)
const allowed = ref(false)
const busy = ref(false)
const error = ref('')
const reviewRequired = ref(false)
const rules = ref([])
const keyword = ref('')
const scope = ref('')
const types = [
  { value: 'technical_update', label: '技术动态' },
  { value: 'tutorial', label: '实操教程' },
  { value: 'project', label: '项目推荐' },
  { value: 'opinion', label: '观点分析' }
]
let client

function describeError(err) {
  return err?.message || '请求失败，请稍后重试。'
}

async function refresh() {
  const [settingsResult, rulesResult] = await Promise.all([
    client.from('news_review_settings').select('review_required').eq('id', true).single(),
    client.from('news_blocked_keywords').select('id, keyword, content_type, enabled').order('created_at', { ascending: false })
  ])
  if (settingsResult.error) throw settingsResult.error
  if (rulesResult.error) throw rulesResult.error
  reviewRequired.value = settingsResult.data.review_required
  rules.value = rulesResult.data
}

async function perform(action) {
  if (busy.value) return
  busy.value = true
  error.value = ''
  try {
    await action()
    await refresh()
  } catch (err) {
    error.value = describeError(err)
    try { await refresh() } catch { /* Preserve the original error. */ }
  } finally {
    busy.value = false
  }
}

function setReview(value) {
  return perform(async () => {
    const { data, error: requestError } = await client.from('news_review_settings')
      .update({ review_required: value }).eq('id', true).select('id').single()
    if (requestError || !data) throw requestError || new Error('设置未保存。')
  })
}

function addRule() {
  const word = keyword.value.trim()
  if (!word) { error.value = '请输入屏蔽关键词。'; return }
  return perform(async () => {
    const { error: requestError } = await client.from('news_blocked_keywords')
      .insert({ keyword: word, content_type: scope.value || null })
    if (requestError) throw requestError
    keyword.value = ''
  })
}

function toggleRule(rule) {
  return perform(async () => {
    const { data, error: requestError } = await client.from('news_blocked_keywords')
      .update({ enabled: !rule.enabled }).eq('id', rule.id).select('id').single()
    if (requestError || !data) throw requestError || new Error('规则未更新。')
  })
}

function label(type) {
  return types.find(item => item.value === type)?.label || '所有类型'
}

onMounted(async () => {
  try {
    const url = import.meta.env.SUPABASE_URL
    const key = import.meta.env.SUPABASE_KEY
    if (!url || !key) throw new Error('尚未配置数据库连接。')
    client = createClient(url, key)
    const { data: auth, error: authError } = await client.auth.getUser()
    if (authError || !auth.user) throw new Error('请先登录管理员账号。')
    const { data: membership, error: memberError } = await client.from('news_admins')
      .select('user_id').eq('user_id', auth.user.id).maybeSingle()
    if (memberError) throw memberError
    if (!membership) throw new Error('当前账号没有新闻管理权限。')
    await refresh()
    allowed.value = true
  } catch (err) {
    error.value = describeError(err)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="news-settings">
    <p v-if="loading">正在读取订阅设置…</p>
    <p v-if="error" class="notice" role="alert">{{ error }}</p>
    <template v-if="allowed">
      <div class="panel">
        <div>
          <h2>发布方式</h2>
          <p>关闭审核时，符合条件的新内容可自动发布；已进入待审核队列的内容不会随开关改变。</p>
        </div>
        <label class="toggle">
          <input type="checkbox" :checked="reviewRequired" :disabled="busy" @change="setReview($event.target.checked)">
          <span>发布前人工审核</span>
        </label>
        <p class="mode">当前：{{ reviewRequired ? '人工审核' : '自动发布' }}</p>
      </div>
      <div class="panel">
        <h2>屏蔽关键词</h2>
        <p>匹配标题、摘要和来源摘录，不区分大小写。规则可作用于所有内容或指定类型。</p>
        <form class="rule-form" @submit.prevent="addRule">
          <label>关键词<input v-model="keyword" maxlength="200" placeholder="例如：广告" :disabled="busy"></label>
          <label>内容类型<select v-model="scope" :disabled="busy"><option value="">所有类型</option><option v-for="type in types" :key="type.value" :value="type.value">{{ type.label }}</option></select></label>
          <button type="submit" :disabled="busy">添加规则</button>
        </form>
        <p v-if="!rules.length" class="empty">暂无屏蔽规则</p>
        <ul v-else class="rules">
          <li v-for="rule in rules" :key="rule.id">
            <div><strong>{{ rule.keyword }}</strong><span>{{ label(rule.content_type) }}</span></div>
            <button type="button" class="secondary" :disabled="busy" @click="toggleRule(rule)">{{ rule.enabled ? '停用' : '启用' }}</button>
          </li>
        </ul>
      </div>
    </template>
  </section>
</template>

<style scoped>
.news-settings { max-width: 820px; display: grid; gap: 20px; }
.panel { padding: 24px; border: 1px solid var(--vp-c-divider); border-radius: 12px; background: var(--vp-c-bg); }
h2 { margin: 0 0 8px; font-size: 18px; }
p { margin: 0 0 16px; color: var(--vp-c-text-2); font-size: 14px; }
.notice { padding: 12px; border-radius: 8px; color: var(--vp-c-danger-1); background: var(--vp-c-danger-soft); }
.toggle { display: flex; gap: 10px; align-items: center; font-weight: 600; }
.mode { margin: 8px 0 0 23px; }
.rule-form { display: flex; align-items: end; gap: 12px; flex-wrap: wrap; }
.rule-form label { display: grid; gap: 6px; flex: 1; min-width: 150px; font-size: 13px; }
input:not([type=checkbox]), select { padding: 9px 10px; border: 1px solid var(--vp-c-divider); border-radius: 6px; background: var(--vp-c-bg); color: var(--vp-c-text-1); }
button { padding: 9px 14px; border: 0; border-radius: 6px; background: var(--vp-c-brand-1); color: white; cursor: pointer; }
button:disabled { opacity: .5; cursor: wait; }
.secondary { background: var(--vp-c-bg-soft); color: var(--vp-c-text-1); }
.rules { padding: 0; margin: 18px 0 0; list-style: none; }
.rules li { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 12px 0; border-top: 1px solid var(--vp-c-divider); }
.rules li div { display: grid; gap: 3px; }
.rules li span, .empty { color: var(--vp-c-text-2); font-size: 13px; }
.empty { margin: 18px 0 0; }
</style>
