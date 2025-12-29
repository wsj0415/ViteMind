---
layout: page
title: AI 工具管理
sidebar: false
---

<script setup>
const columns = [
  {
    key: 'name',
    label: '名称',
    type: 'text',
    editable: true,
    width: '200px',
    validation: { required: true }
  },
  {
    key: 'link',
    label: '链接',
    type: 'link',
    editable: true,
    width: '250px',
    validation: { required: true, type: 'url' }
  },
  { key: 'description', label: '描述', type: 'textarea', editable: true },
  {
    key: 'category',
    label: '分类',
    type: 'select',
    editable: true,
    width: '120px',
    options: ['Coding', 'Image', 'Video', 'Writing', 'Audio', 'Productivity'],
    validation: { required: true }
  },
  { key: 'tags', label: '标签', type: 'tags', editable: true, width: '200px' },
  { key: 'approved', label: '审核', type: 'boolean', editable: true, width: '100px' },
  { key: 'submitted_at', label: '提交时间', type: 'date', editable: false, width: '120px' }
]
</script>

<AdminLayout title="AI 工具管理">
  <DataManager 
    tableName="ai_tools" 
    :columns="columns" 
    defaultSort="submitted_at"
  />
</AdminLayout>
