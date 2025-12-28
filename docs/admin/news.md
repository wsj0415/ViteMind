---
layout: page
title: 每日新闻管理
sidebar: false
---

<script setup>
const columns = [
  { key: 'title', label: '标题', type: 'text', editable: true, width: '300px' },
  { key: 'link', label: '链接', type: 'link', editable: true, width: '250px' },
  { key: 'summary', label: '摘要', type: 'textarea', editable: true },
  { key: 'date', label: '日期', type: 'date', editable: true, width: '120px' }
]
</script>

<AdminLayout title="每日新闻管理">
  <DataManager 
    tableName="news" 
    :columns="columns" 
    defaultSort="date"
  />
</AdminLayout>
