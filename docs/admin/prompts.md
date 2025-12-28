---
layout: page
title: AI 提示词管理
sidebar: false
---

<script setup>
const columns = [
  { key: 'title', label: '标题', type: 'text', editable: true, width: '200px' },
  { key: 'content', label: '内容', type: 'textarea', editable: true },
  { key: 'category', label: '分类', type: 'text', editable: true, width: '120px' },
  { key: 'approved', label: '审核', type: 'boolean', editable: true, width: '100px' },
  { key: 'created_at', label: '创建时间', type: 'date', editable: false, width: '120px' }
]
</script>

<AdminLayout title="AI 提示词管理">
  <DataManager 
    tableName="ai_prompts" 
    :columns="columns" 
    defaultSort="created_at"
  />
</AdminLayout>
