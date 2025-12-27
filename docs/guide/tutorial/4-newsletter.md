---
layout: doc
title: 4. 私域流量 (Newsletter)
---

# 实战第四章：构建私域流量池

在 Web 2.0 时代，**Email Newsletter** 依然是触达用户最可靠的方式。本章我们将介绍如何在没有后端服务器的情况下，使用 **Formspree** 实现邮件订阅功能。

## 📧 为什么选择 Formspree?

对于静态网站（如 VitePress），我们没有后端来处理表单提交。Formspree 提供了一个完美的解决方案：
*   **无后端**：直接 POST 数据到他们的 API。
*   **免费额度**：每月 50 次提交（足够初期使用）。
*   **即时通知**：有人订阅时，你会收到邮件提醒。

## 🛠️ 集成步骤

### 1. 获取 Form ID

1.  访问 [Formspree.io](https://formspree.io/) 并注册。
2.  创建一个新表单 (New Form)，命名为 "ViteMind Newsletter"。
3.  复制你的 **Form Endpoint** (例如 `https://formspree.io/f/xvbdmqlo`)。

### 2. 编写 Vue 组件

创建 `docs/.vitepress/theme/components/NewsletterForm.vue`。

```vue
<script setup>
import { ref } from 'vue'

const email = ref('')
const status = ref('idle') // idle, loading, success, error

// 🔴 替换为你自己的 Form ID
const FORMSPREE_ENDPOINT = 'https://formspree.io/f/YOUR_FORM_ID'

const subscribe = async () => {
  if (!email.value || !email.value.includes('@')) {
    status.value = 'error'
    return
  }
  
  status.value = 'loading'
  
  try {
    const response = await fetch(FORMSPREE_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: email.value })
    })

    if (response.ok) {
      status.value = 'success'
      email.value = ''
    } else {
      status.value = 'error'
    }
  } catch (e) {
    status.value = 'error'
  }
}
</script>

<template>
  <!-- 简化的模板结构 -->
  <div class="form-container">
    <input v-model="email" placeholder="Enter your email" :disabled="status === 'success'" />
    <button @click="subscribe">
      {{ status === 'success' ? 'Subscribed!' : 'Subscribe' }}
    </button>
  </div>
</template>

<style scoped>
/* 添加你的瑞士风格样式 */
</style>
```

### 3. 创建落地页

创建 `docs/newsletter.md`：

```markdown
---
layout: page
title: Subscribe
sidebar: false
---

<NewsletterForm />
```

## 💡 进阶技巧

*   **防垃圾邮件**：Formspree 自带 Honeypot 字段，也可以在前端添加简单的正则校验。
*   **自定义感谢页**：Formspree 允许配置提交成功后的跳转页面，或者像我们一样在当前页面显示成功状态。

---

**下一章预告**：我们将列出构建 ViteMind 所参考的核心资源。👉 [第五章：巨人肩膀](./5-resources.md)
