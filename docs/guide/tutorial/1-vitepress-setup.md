---
layout: doc
title: 1. 极速搭建 (Setup)
---

# 实战第一章：极速搭建 VitePress

欢迎来到 **ViteMind 构建实战**。本章我们将从零开始，搭建一个高性能的文档站点。

## 🛠️ 环境准备

在开始之前，请确保你的电脑上安装了 **Node.js**。

> [!WARNING] ⚠️ 避坑指南：Node 版本
> VitePress 要求 **Node.js 18+**。
> 如果你的版本过低，安装时会报错。请在终端输入 `node -v` 检查。

## 🚀 初始化项目

打开终端，执行以下命令：

```bash
# 1. 创建并进入项目目录
mkdir my-vitemind
cd my-vitemind

# 2. 初始化 package.json
npm init -y

# 3. 安装 VitePress
npm add -D vitepress

# 4. 启动安装向导 (推荐)
npx vitepress init
```

在安装向导中，建议如下选择：

*   **Where should VitePress initialize the config?** -> `./docs` (推荐，结构更清晰)
*   **Site title:** -> `My AI Hub`
*   **Site description:** -> `A knowledge base for AI.`
*   **Theme:** -> `Default Theme`

## 📂 目录结构解析

安装完成后，你的项目结构应该是这样的：

```
.
├─ docs/
│  ├─ .vitepress/
│  │  └─ config.mts   <-- 核心配置文件
│  ├─ api-examples.md
│  ├─ markdown-examples.md
│  └─ index.md        <-- 首页
└─ package.json
```

> [!TIP] 💡 为什么是 docs 目录？
> 将文档放在 `docs` 目录下，可以保持根目录整洁，方便后续添加脚本（如我们的 AI 爬虫脚本）或其他配置文件。

## 🏃‍♂️ 启动与预览

```bash
npm run docs:dev
```

浏览器打开 `http://localhost:5173`，恭喜你！你的网站雏形已经诞生了。

---

**下一章预告**：我们将为这个静态网站装上“大脑”，实现 AI 自动抓取新闻。👉 [第二章：AI 自动化引擎](./2-news-automation.md)
