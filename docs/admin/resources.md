---
layout: page
title: 设计资源管理
sidebar: false
---

<script setup>
const columns = [
  { key: 'title', label: '标题', type: 'text', editable: true, width: '200px' },
  { key: 'url', label: '链接', type: 'link', editable: true, width: '250px' },
  { key: 'description', label: '描述', type: 'textarea', editable: true },
  { key: 'category', label: '分类', type: 'text', editable: true, width: '120px' },
  { key: 'is_featured', label: '精选', type: 'boolean', editable: true, width: '100px' },
  { key: 'created_at', label: '创建时间', type: 'date', editable: false, width: '120px' }
]
</script>

<AdminLayout title="设计资源管理">
  <DataManager 
    tableName="design_resources" 
    :columns="columns" 
    defaultSort="created_at"
  />
</AdminLayout>
