<script setup>
// Pricing logic can be added here if needed
</script>

<template>
  <div class="pricing-section">
    <h2>订阅方案</h2>
    <p class="subtitle">选择最适合您的成长计划</p>
    
    <div class="pricing-cards">
      <div class="card">
        <div class="card-header">
          <h3>基础版</h3>
          <div class="price">Free</div>
        </div>
        <ul class="features">
          <li>✅ 访问所有公开指南</li>
          <li>✅ 基础架构解析</li>
          <li>✅ 社区技术支持</li>
        </ul>
        <a href="/guide/getting-started" class="btn">开始阅读</a>
      </div>
      
      <div class="card popular">
        <div class="tag">最受欢迎</div>
        <div class="card-header">
          <h3>专业版</h3>
          <div class="price">¥99<span class="period">/年</span></div>
        </div>
        <ul class="features">
          <li>✅ <strong>解锁所有付费专栏</strong></li>
          <li>✅ 深度架构设计源码</li>
          <li>✅ 1对1 变现咨询</li>
          <li>✅ 专属会员群</li>
        </ul>
        <a href="/paid/index" class="btn primary">立即订阅</a>
      </div>
      
      <div class="card">
        <div class="card-header">
          <h3>终身版</h3>
          <div class="price">¥299<span class="period">/一次性</span></div>
        </div>
        <ul class="features">
          <li>✅ <strong>包含专业版所有权益</strong></li>
          <li>✅ 永久更新承诺</li>
          <li>✅ 优先功能建议权</li>
          <li>✅ 早期项目投资机会</li>
        </ul>
        <a href="/paid/index" class="btn">获取终身卡</a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pricing-section {
  margin-top: 60px;
  text-align: center;
}

.pricing-section h2 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 10px;
  border: none;
}

.subtitle {
  color: var(--vp-c-text-2);
  margin-bottom: 40px;
}

.pricing-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 20px;
}

.card {
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 2rem;
  text-align: left;
  transition: transform 0.3s, box-shadow 0.3s;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.1);
  border-color: var(--vp-c-brand);
}

.card.popular {
  border: 2px solid var(--vp-c-brand);
  background: var(--vp-c-bg-alt);
}

.tag {
  position: absolute;
  top: 12px;
  right: -30px;
  background: var(--vp-c-brand);
  color: white;
  padding: 5px 40px;
  transform: rotate(45deg);
  font-size: 0.8rem;
  font-weight: bold;
}

.card-header h3 {
  font-size: 1.5rem;
  margin: 0;
  color: var(--vp-c-text-1);
}

.price {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--vp-c-text-1);
  margin: 1rem 0;
}

.period {
  font-size: 1rem;
  color: var(--vp-c-text-2);
  font-weight: normal;
}

.features {
  list-style: none;
  padding: 0;
  margin: 2rem 0;
  flex-grow: 1;
}

.features li {
  margin-bottom: 0.8rem;
  color: var(--vp-c-text-2);
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn {
  display: block;
  text-align: center;
  padding: 12px;
  border-radius: 6px;
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  color: var(--vp-c-text-1);
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  margin-top: auto;
}

.btn.primary {
  background: var(--vp-c-brand);
  color: white;
  border-color: var(--vp-c-brand);
}

.btn:hover {
  opacity: 0.9;
  text-decoration: none;
}
</style>
