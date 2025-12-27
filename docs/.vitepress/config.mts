import { defineConfig } from 'vitepress'
import path from 'path'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  base: "/ViteMind/",
  title: "ViteMind",
  description: "极速构建你的第二大脑",

  // Load .env files from project root (parent of docs folder)
  vite: {
    envDir: path.resolve(__dirname, '../../')
  },

  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: '首页', link: '/' },
      { text: 'AI 导航', link: '/ai-tools' },
      { text: '指南', link: '/guide/getting-started' },
      { text: '付费专栏', link: '/paid/index' },
      { text: '订阅', link: '/newsletter' }
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
        text: '实战教程 (Build in Public)',
        items: [
          { text: '1. 极速搭建', link: '/guide/tutorial/1-vitepress-setup' },
          { text: '2. AI 自动化引擎', link: '/guide/tutorial/2-news-automation' },
          { text: '3. 定制化开发', link: '/guide/tutorial/3-customization' },
          { text: '4. 私域流量', link: '/guide/tutorial/4-newsletter' },
          { text: '5. 巨人肩膀', link: '/guide/tutorial/5-resources' },
          { text: '6. 进阶功能', link: '/guide/tutorial/6-advanced-features' }
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
    },

    search: {
      provider: 'local',
      options: {
        translations: {
          button: {
            buttonText: '搜索文档',
            buttonAriaLabel: '搜索文档'
          },
          modal: {
            noResultsText: '无法找到相关结果',
            resetButtonTitle: '清除查询条件',
            footer: {
              selectText: '选择',
              navigateText: '切换'
            }
          }
        }
      }
    }
  }
})
