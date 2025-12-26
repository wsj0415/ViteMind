import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "ViteMind",
  description: "极速构建你的第二大脑",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: '首页', link: '/' },
      { text: '指南', link: '/guide/getting-started' },
      { text: '付费专栏', link: '/paid/index' }
    ],

    sidebar: [
      {
        text: '开始使用',
        items: [
          { text: '简介', link: '/guide/getting-started' },
          { text: '快速上手', link: '/guide/quick-start' }
        ]
      },
      {
        text: '高价值内容',
        items: [
          { text: '核心架构 (付费)', link: '/paid/architecture' },
          { text: '变现逻辑 (付费)', link: '/paid/monetization' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/vuejs/vitepress' }
    ],

    footer: {
      message: '基于 VitePress 构建 | ViteMind 知识库',
      copyright: 'Copyright © 2025 ViteMind'
    }
  }
})
