---
layout: page
title: 设计资源管理
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
  { key: 'description', label: '描述', type: 'textarea', editable: true },
  {
    key: 'category',
    label: '分类',
    type: 'select',
    editable: true,
    width: '120px',
    options: ['Design Tools', 'UI Libraries', 'Icons & Fonts', 'Colors', 'Design Systems', 'Learning', 'Inspiration', 'Prototyping'],
    validation: { required: true }
  },
  { key: 'logo_url', label: 'Logo URL', type: 'text', editable: true, width: '200px' },
  { key: 'tags', label: '标签', type: 'tags', editable: true, width: '200px' },
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
