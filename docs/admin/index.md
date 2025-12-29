```
---
layout: page
title: 仪表盘
sidebar: false
---

<AdminLayout title="仪表盘">
  <div class="dashboard-cards">
    <div class="stat-card">
      <h3>AI 提示词</h3>
      <p>管理提示词库</p>
      <a :href="withBase('/admin/prompts')">去管理 →</a>
    </div>
    <div class="stat-card">
      <h3>AI 开发</h3>
      <p>管理开发资源</p>
      <a :href="withBase('/admin/dev-resources')">去管理 →</a>
    </div>
  </div>
</AdminLayout>
```
