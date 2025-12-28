---
layout: doc
title: 7. 构建全栈管理后台
description: 使用 Supabase Auth 和 RLS 构建安全的管理后台
---

# 7. 构建全栈管理后台 (Admin Dashboard)

随着 ViteMind 的功能日益丰富，我们需要一个便捷的方式来管理 AI 工具、设计资源和提示词，而不是每次都去操作数据库。本章将介绍如何基于 Supabase Auth 和 Vue 构建一个安全、高效的全栈管理后台。

## 核心架构

我们的管理后台采用 **SPA (单页应用)** 模式嵌入在 VitePress 中，核心技术栈如下：

*   **身份认证**: Supabase Auth (Email/Password)
*   **权限控制**: PostgreSQL RLS (Row Level Security)
*   **前端路由**: VitePress 路由 + 客户端守卫
*   **UI 组件**: 自定义 Vue 组件 (`DataManager`, `AdminLayout`)

## 1. 数据库安全策略 (RLS)

这是最关键的一步。我们需要确保只有管理员才能修改数据，而普通用户只能读取或提交。

我们为所有表（`ai_tools`, `design_resources`, `ai_prompts`, `news`）配置了如下策略：

```sql
-- 允许所有用户读取 (SELECT)
CREATE POLICY "Allow public read access" ON public.ai_tools FOR SELECT USING (true);

-- 允许所有用户提交 (INSERT)
CREATE POLICY "Allow public insert" ON public.ai_tools FOR INSERT WITH CHECK (true);

-- 仅允许认证用户修改和删除 (UPDATE, DELETE)
CREATE POLICY "Allow full access for authenticated users"
ON public.ai_tools
FOR ALL
TO authenticated
USING (true)
WITH CHECK (true);
```

这样，即使前端代码暴露了 Supabase Key，恶意用户也无法修改数据，因为他们没有 `authenticated` 角色。

## 2. 身份认证实现

我们创建了一个独立的登录页面 `AdminLogin.vue`，使用 Supabase SDK 进行登录：

```javascript
const handleLogin = async () => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email: email.value,
    password: password.value
  })
  
  if (!error) {
    // 登录成功，跳转到仪表盘
    // 使用 import.meta.env.BASE_URL 兼容子路径部署
    window.location.href = import.meta.env.BASE_URL + 'admin/index'
  }
}
```

## 3. 路由保护与布局

为了统一管理页面的外观和权限检查，我们封装了 `AdminLayout.vue` 组件。它在挂载时会检查用户的会话状态：

```javascript
onMounted(async () => {
  const { data: { session } } = await supabase.auth.getSession()
  
  if (!session) {
    // 未登录，强制跳转回登录页
    window.location.href = import.meta.env.BASE_URL + 'admin/login'
  }
})
```

## 4. 通用数据管理组件

为了避免为每个表重复写 CRUD 代码，我们开发了 `DataManager.vue` 组件。它接收 `tableName` 和 `columns` 配置，自动生成表格和操作按钮。

**使用示例 (`docs/admin/tools.md`)**:

```vue
<script setup>
const columns = [
  { key: 'name', label: '名称', type: 'text', editable: true },
  { key: 'approved', label: '审核', type: 'boolean', editable: true }
]
</script>

<AdminLayout title="AI 工具管理">
  <DataManager tableName="ai_tools" :columns="columns" />
</AdminLayout>
```

## 5. 部署与使用

由于我们使用的是自建后台，没有开放注册入口，管理员账号需要手动创建：

1.  在 Supabase Dashboard -> Authentication -> Providers 中启用 **Email**。
2.  在 Authentication -> Users 中手动 **Add User**。
3.  运行我们提供的 SQL 脚本 `scripts/update_rls_for_admin.sql` 更新权限策略。

---

通过这种方式，我们不仅拥有了一个功能完备的 CMS，还保持了 "Serverless" 的架构优势，无需维护后端服务器。
