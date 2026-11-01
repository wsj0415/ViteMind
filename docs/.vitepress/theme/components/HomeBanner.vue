<script setup>
import { ref, onMounted } from 'vue'
import { withBase } from 'vitepress'

const latest = ref([])
onMounted(async () => {
  try {
    const response = await fetch(withBase('/data/news.json'))
    if (response.ok) latest.value = (await response.json()).slice(0, 3)
  } catch (error) {
    console.error('Failed to load featured news:', error)
  }
})
</script>

<template>
  <section class="hero" aria-labelledby="hero-title">
    <div class="hero-inner">
      <div class="hero-top"><span>AN INDEPENDENT GUIDE TO AI</span><span>VITEMIND / 人工智能观察</span></div>
      <div class="hero-main">
        <div class="hero-intro">
          <p class="eyebrow"><span class="dot"></span> KEEP YOUR CURIOSITY ALIVE</p>
          <h1 id="hero-title">在 AI 的浪潮中，<br><span>找到值得关注的。</span></h1>
          <p class="description">追踪新动态，发现好工具，整理有用的知识。<br>让复杂的信息，变成下一步行动的灵感。</p>
          <div class="actions"><a class="primary" href="#latest-news">浏览最新资讯 <span aria-hidden="true">↗</span></a><a :href="withBase('/ai-tools')" class="secondary">探索 AI 工具 <span aria-hidden="true">→</span></a></div>
        </div>
        <aside class="briefing" aria-label="最新资讯预览">
          <div class="briefing-heading"><div><span class="briefing-kicker">THE LATEST</span><h2>最近在发生</h2></div><span class="edition">V / M<br>精选速览</span></div>
          <a v-for="(item, index) in latest" :key="item.link" class="briefing-item" :href="item.link" target="_blank" rel="noopener noreferrer">
            <span class="item-number">0{{ index + 1 }}</span><span class="item-body"><span class="item-date">{{ item.date }}</span><span class="item-title">{{ item.title }}</span></span><span class="item-arrow" aria-hidden="true">↗</span>
          </a>
          <a class="briefing-all" href="#latest-news">查看全部资讯 <span aria-hidden="true">↘</span></a>
        </aside>
      </div>
      <div class="hero-bottom"><span>IDEAS, TOOLS & WHAT'S NEXT</span><a href="#latest-news">向下探索 <span aria-hidden="true">↓</span></a></div>
    </div>
  </section>
</template>

<style scoped>
.hero { background: var(--vp-c-bg); padding: 32px 24px 8px; }
.hero-inner { max-width: 1152px; margin: auto; color: var(--vp-c-text-1); }
.hero-top, .hero-bottom { display: flex; justify-content: space-between; color: var(--vp-c-text-2); font-size: 10px; letter-spacing: .15em; font-weight: 650; }
.hero-top { border-bottom: 1px solid var(--vp-c-divider); padding: 14px 0 18px; }
.hero-main { display: grid; grid-template-columns: 1.16fr .84fr; gap: 64px; padding: 78px 0 88px; align-items: center; }
.eyebrow, .briefing-kicker { font-size: 10px; letter-spacing: .16em; font-weight: 700; color: #9274c8; }
.dot { display: inline-block; background: #9d7bd2; width: 7px; height: 7px; border-radius: 50%; margin-right: 8px; }
h1 { margin: 28px 0 24px; font-size: clamp(38px, 4.3vw, 59px); line-height: 1.26; letter-spacing: -.055em; font-weight: 700; }
h1 span { color: var(--vp-c-text-2); font-weight: 450; }
.description { margin: 0; color: var(--vp-c-text-2); font-size: 15px; line-height: 2; }
.actions { display: flex; align-items: center; gap: 28px; margin-top: 32px; font-size: 13px; font-weight: 650; }
.actions a, .briefing a, .hero-bottom a { text-decoration: none; }
.primary { display: flex; gap: 25px; padding: 13px 17px; background: var(--vp-c-text-1); color: var(--vp-c-bg) !important; }
.secondary { color: var(--vp-c-text-1) !important; }
.secondary span { margin-left: 8px; }
.briefing { background: var(--vp-c-bg-soft); padding: 28px 30px 24px; border: 1px solid var(--vp-c-divider); }
.briefing-heading { display: flex; justify-content: space-between; align-items: flex-start; padding-bottom: 21px; }
.briefing-heading h2 { margin: 5px 0 0; border: 0; padding: 0; font-size: 22px; letter-spacing: -.04em; }
.edition { font-size: 10px; line-height: 1.6; text-align: right; color: var(--vp-c-text-3); }
.briefing-item { display: grid; grid-template-columns: 28px 1fr 20px; gap: 10px; padding: 16px 0; border-top: 1px solid var(--vp-c-divider); color: var(--vp-c-text-1) !important; }
.item-number, .item-date { color: var(--vp-c-text-3); font-size: 10px; letter-spacing: .04em; }
.item-body { display: grid; gap: 5px; }
.item-title { font-size: 14px; line-height: 1.5; font-weight: 600; }
.item-arrow { color: var(--vp-c-text-3); }
.briefing-all { display: flex; justify-content: space-between; border-top: 1px solid var(--vp-c-divider); padding-top: 18px; font-size: 12px; color: var(--vp-c-text-2) !important; }
.hero-bottom { border-top: 1px solid var(--vp-c-divider); padding: 18px 0; }
.hero-bottom a { color: var(--vp-c-text-2) !important; letter-spacing: .04em; }
@media (prefers-reduced-motion: no-preference) {
  .hero-intro { animation: appear .7s ease-out both; }
  .briefing { animation: appear .8s .12s ease-out both; }
  .briefing-item, .primary { transition: transform .25s ease, color .25s ease, background .25s ease; }
  .briefing-item:hover { transform: translateX(5px); color: var(--vp-c-brand-1) !important; }
  .primary:hover { transform: translateY(-3px); background: #8064ad; }
  @keyframes appear { from { opacity: 0; transform: translateY(18px); } to { opacity: 1; transform: translateY(0); } }
}
@media (max-width: 768px) { .hero { padding: 12px 20px 0; } .hero-top { font-size: 9px; } .hero-top span:last-child { display: none; } .hero-main { grid-template-columns: 1fr; gap: 42px; padding: 55px 0; } h1 { font-size: clamp(34px, 9vw, 52px); } .description { font-size: 14px; } .briefing { padding: 24px; } }
</style>
