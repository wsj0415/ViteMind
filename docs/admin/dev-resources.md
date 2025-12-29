---
layout: page
title: AI 开发资源管理
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
    key: 'url',
    label: '链接',
    type: 'link',
    editable: true,
    width: '250px',
    validation: { required: true, type: 'url' }
  },
  {
    key: 'github_url',
    label: 'GitHub',
    type: 'link',
    editable: true,
    width: '200px',
    validation: { type: 'url' }
  },
  { key: 'description', label: '描述', type: 'textarea', editable: true },
  {
    key: 'category',
    label: '分类',
    type: 'select',
    editable: true,
    width: '150px',
    options: ['Agent Frameworks', 'Skills & MCP', 'Dev Tools', 'Prompt Engineering', 'Workflow', 'Docs & Specs'],
    validation: { required: true }
  },
  { key: 'language', label: '语言', type: 'text', editable: true, width: '100px' },
  { key: 'license', label: '协议', type: 'text', editable: true, width: '100px' },
  { key: 'tags', label: '标签', type: 'tags', editable: true, width: '200px' },
  { key: 'is_featured', label: '精选', type: 'boolean', editable: true, width: '80px' },
  { key: 'created_at', label: '创建时间', type: 'date', editable: false, width: '120px' }
]
</script>

<AdminLayout title="AI 开发资源管理">
  <DataManager tableName="dev_resources" :columns="columns" />
</AdminLayout>
