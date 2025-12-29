---
layout: page
title: AI 提示词管理
sidebar: false
---

<script setup>
const columns = [
  {
    key: 'title',
    label: '标题',
    type: 'text',
    editable: true,
    width: '200px',
    validation: { required: true }
  },
  {
    key: 'content',
    label: '内容',
    type: 'textarea',
    editable: true,
    validation: { required: true }
  },
  {
    key: 'category',
    label: '分类',
    type: 'select',
    editable: true,
    width: '120px',
    options: ['Coding', 'Image', 'Writing', 'Marketing', 'SEO', 'Productivity'],
    validation: { required: true }
  },
  { key: 'tags', label: '标签', type: 'tags', editable: true, width: '200px' },
  { key: 'version', label: '版本', type: 'text', editable: true, width: '80px' },
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
