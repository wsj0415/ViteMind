# ViteMind

[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![VitePress](https://img.shields.io/badge/VitePress-1.0.0-646cff.svg)](https://vitepress.dev/)
[![Supabase](https://img.shields.io/badge/Supabase-Database-3ecf8e.svg)](https://supabase.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776ab.svg)](https://www.python.org/)

**ViteMind** 是一个基于 **VitePress** 构建的高性能知识库与内容变现平台。我们致力于将碎片化的信息重构为有价值的资产，通过 AI 自动化、内容管理系统 (CMS) 和付费订阅机制，探索知识变现的无限可能。

---

## 📖 项目概述 (Overview)

ViteMind 不仅仅是一个文档网站，它是一个集成了现代 Web 技术与 AI 能力的全栈内容平台。

### ✨ 核心特性 (Key Features)

- **📚 高性能知识库**: 基于 VitePress，极速加载，Markdown 优先的写作体验。
- **🤖 AI 资讯自动化**: 内置 Python 自动化脚本，自动聚合 RSS 信息源，利用 LLM (大语言模型) 自动生成摘要与解读。
- **🛠 AI 工具导航**: 专门设计的 AI 工具展示画廊，支持分类与搜索。
- **🔐 管理后台 (Admin Dashboard)**: 集成 Supabase 的可视化管理后台，轻松管理新闻、工具和提示词数据。
- **💰 内容变现 (Monetization)**: 内置付费墙 (Paywall) 和会员订阅逻辑，支持高价值内容的权限控制。
- **🎨 现代化 UI**: 精心设计的 Vue 组件，包括卡片流、暗黑模式支持和响应式布局。

---

## 🛠 技术栈 (Tech Stack)

### 前端 (Frontend)
- **Framework**: [VitePress](https://vitepress.dev/) (基于 Vue 3 + Vite)
- **Language**: TypeScript / JavaScript
- **Styling**: CSS Variables + Custom Layouts
- **Icons**: SVG / FontAwesome

### 后端与数据 (Backend & Data)
- **Database**: [Supabase](https://supabase.com/) (PostgreSQL)
- **Auth**: Supabase Auth (用于管理后台登录)
- **Storage**: Supabase Storage (可选，用于图片托管)

### 自动化 (Automation)
- **Language**: Python 3.8+
- **Libraries**: `requests`, `feedparser`, `openai`, `supabase`
- **AI Model**: 支持 OpenRouter / OpenAI 兼容接口 (默认配置 Qwen/Qwen2.5-Coder)

---

## 📂 目录结构 (Directory Structure)

```bash
ViteMind/
├── docs/                   # 文档根目录
│   ├── .vitepress/         # VitePress 配置与主题
│   │   ├── config.mts      # 站点主配置
│   │   └── theme/          # 自定义主题与组件
│   │       ├── components/ # Vue 组件 (Admin, Gallery, etc.)
│   │       └── style.css   # 全局样式
│   ├── admin/              # 管理后台页面 (Markdown 容器)
│   ├── guide/              # 指南文档
│   ├── public/             # 静态资源 (图片, data/news.json)
│   └── index.md            # 首页
├── scripts/                # 自动化脚本
│   └── generate_news.py    # 新闻抓取与 AI 生成脚本
├── package.json            # Node 依赖配置
├── .env.local              # 环境变量 (需自行创建)
└── README.md               # 项目说明文档
```

---

## 🚀 环境要求与安装 (Getting Started)

### 环境要求 (Prerequisites)
- **Node.js**: v18.0.0 或更高版本
- **pnpm**: 推荐使用 pnpm 管理依赖
- **Python**: v3.8+ (用于运行自动化脚本)

### 1. 安装项目依赖

```bash
# 克隆项目
git clone https://github.com/your-username/vitemind.git
cd vitemind

# 安装前端依赖
pnpm install

# 安装 Python 依赖 (用于自动化脚本)
pip install requests feedparser python-dotenv openai supabase
```

### 2. 配置环境变量

在项目根目录创建 `.env.local` 文件，填入以下配置：

```ini
# Supabase 配置 (用于后端数据存储)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# OpenRouter / OpenAI 配置 (用于 AI 新闻摘要)
OPENROUTER_API_KEY=your-api-key
```

### 3. 启动开发服务器

```bash
pnpm docs:dev
```
访问 `http://localhost:5173/ViteMind/` 即可预览。

---

## 🤖 核心功能模块 (Core Modules)

### 1. AI 新闻自动化
运行脚本自动抓取 RSS 源并生成摘要：
```bash
python scripts/generate_news.py
```
*生成的 JSON 会保存在 `docs/public/data/news.json` 供前端直接读取，同时同步至 Supabase。*

### 2. 管理后台 (Admin Dashboard)
访问 `/admin/` 路径进入后台。后台功能包括：
- **数据管理**: 对新闻、工具、提示词进行 CRUD 操作。
- **登录验证**: 基于 Supabase 的简单认证。

### 3. 付费专栏 (Paid Content)
在 Markdown 中使用自定义组件 `<PayWall>` 来隐藏特定内容，仅展示给订阅用户（需对接具体的支付/权限逻辑）。

---

## 🚢 生产环境部署 (Deployment)

### 推荐：Vercel
VitePress 项目最适合部署在 Vercel。
1. 在 Vercel 导入你的 GitHub 仓库。
2. Build Settings 会自动识别：
   - **Build Command**: `pnpm docs:build`
   - **Output Directory**: `docs/.vitepress/dist`
3. 点击 Deploy 即可。

### GitHub Pages
1. 在 `docs/.vitepress/config.mts` 中确保 `base` 设置正确（例如 `/ViteMind/`）。
2. 使用 GitHub Actions 进行自动构建和发布。

---

## ❓ 常见问题 (FAQ)

**Q: 为什么管理后台无法登录？**
A: 请确保 `.env` 文件中正确配置了 `SUPABASE_URL` 和 `SUPABASE_KEY`，并且 Supabase 中已创建对应的 `admin` 表或开启了 Auth 服务。

**Q: AI 脚本报错 `RateLimitError`？**
A: 这是 API 调用频率限制。脚本中已内置重试机制，如果持续失败，请检查 API Key 余额或更换模型提供商。

**Q: 如何修改网站 Logo 和导航？**
A: 修改 `docs/.vitepress/config.mts` 文件中的 `themeConfig` 配置项。

---

## 🤝 贡献指南 (Contributing)

欢迎提交 Pull Request (PR) 参与贡献！

1. **Fork** 本仓库。
2. 创建新的分支: `git checkout -b feature/AmazingFeature`。
3. 提交更改: `git commit -m 'Add some AmazingFeature'`。
4. 推送分支: `git push origin feature/AmazingFeature`。
5. 提交 **Pull Request**。

---

## 📄 许可证 (License)

本项目采用 [Apache License 2.0](LICENSE) 许可证。

---

## 📧 联系方式 (Contact)

如有任何问题或建议，欢迎通过以下方式联系：

- **Issues**: [GitHub Issues](https://github.com/your-username/vitemind/issues)
- **Email**: contact@vitemind.com (示例)
