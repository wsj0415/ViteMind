---
layout: doc
title: 3. 定制化开发
---

# 实战第三章：瑞士军刀般的定制化

VitePress 不仅仅是文档工具，它本质上是一个 **Vue 应用**。这意味着我们可以使用 Vue 组件来实现任何复杂的交互。

## 🎨 瑞士风格设计 (Swiss Style)

我们的设计哲学是：**内容至上，网格约束，高对比度**。

### 1. 创建 Vue 组件

在 `docs/.vitepress/theme/components/` 下创建 `NewsGallery.vue`。

```vue
<script setup>
import { ref, onMounted } from 'vue'

const news = ref([])

// 动态加载数据
onMounted(async () => {
  const res = await fetch('/data/news.json')
  news.value = await res.json()
})
</script>

<template>
  <div class="grid-container">
    <div v-for="item in news" :key="item.id" class="card">
      <h3>{{ item.title }}</h3>
      <p>{{ item.summary }}</p>
    </div>
  </div>
</template>

<style scoped>
/* 瑞士风格网格 */
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 0; /* 无间隙 */
  border: 1px solid #eee;
}

.card {
  padding: 20px;
  border-right: 1px solid #eee;
  border-bottom: 1px solid #eee;
}
</style>
```

### 2. 注册组件

在 `docs/.vitepress/theme/index.ts` 中注册，这样才能在 Markdown 中使用。

```typescript
import DefaultTheme from 'vitepress/theme'
import NewsGallery from './components/NewsGallery.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    // 注册全局组件
    app.component('NewsGallery', NewsGallery)
  }
}
```

> [!WARNING] ⚠️ 避坑指南：SSR 报错
> VitePress 在构建时是在 Node 环境下运行的（服务端渲染）。
> 如果你的组件里用到了 `window` 或 `document`，必须放在 `onMounted` 生命周期里，或者用 `<ClientOnly>` 包裹，否则构建会失败。

## 🧩 在 Markdown 中使用

现在，你可以在任何 `.md` 文件中直接插入组件了：

```markdown
# AI 情报局

<NewsGallery />
```

---

## 🎉 结语

恭喜！你已经掌握了构建 ViteMind 的核心技术：
1.  **VitePress** 搭建骨架。
2.  **Python + GitHub Actions** 注入灵魂（数据）。
3.  **Vue 组件** 赋予颜值（交互）。

现在，去创造属于你自己的“第二大脑”吧！🚀
