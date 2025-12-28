---
layout: page
title: 仪表盘
sidebar: false
---

<script setup>
import { withBase } from 'vitepress'
</script>

<AdminLayout title="仪表盘">
  <div class="dashboard-welcome">
    <h2>欢迎回来，管理员 👋</h2>
    <p>请从左侧菜单选择要管理的内容。</p>
    
    <div class="quick-stats">
      <div class="stat-card">
        <h3>AI 工具</h3>
        <p>管理 AI 导航列表</p>
        <a :href="withBase('/admin/tools')">去管理 →</a>
      </div>
      <div class="stat-card">
        <h3>设计资源</h3>
        <p>管理设计资源列表</p>
        <a :href="withBase('/admin/resources')">去管理 →</a>
      </div>
      <div class="stat-card">
        <h3>AI 提示词</h3>
        <p>管理提示词库</p>
        <a :href="withBase('/admin/prompts')">去管理 →</a>
      </div>
    </div>
  </div>
</AdminLayout>

<style>
.dashboard-welcome {
  padding: 20px;
}

.quick-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 40px;
}

.stat-card {
  background: var(--vp-c-bg);
  border: 1px solid var(--vp-c-divider);
  border-radius: 12px;
  padding: 24px;
  transition: all 0.2s;
}

.stat-card:hover {
  border-color: var(--vp-c-brand);
  transform: translateY(-2px);
}

.stat-card h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
}

.stat-card p {
  color: var(--vp-c-text-2);
  margin-bottom: 16px;
}

.stat-card a {
  color: var(--vp-c-brand);
  font-weight: 600;
  text-decoration: none;
}
</style>
