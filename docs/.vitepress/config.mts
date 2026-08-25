import { defineConfig } from 'vitepress'
import path from 'path'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  base: "/ViteMind/",
  lang: 'zh-CN',
  title: "ViteMind",
  description: "UNCOVER THE FUTURE OF AI",
  head: [
    [
      'meta',
      {
        'http-equiv': 'Content-Security-Policy',
        content: "default-src 'none'; base-uri 'self'; form-action 'self'; font-src 'self' data:; img-src 'self' data: https://www.google.com https://www.google-analytics.com https://analytics.google.com https://api.iconify.design; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com; style-src 'self' 'unsafe-inline'; connect-src 'self' https://*.supabase.co https://www.google-analytics.com https://analytics.google.com https://stats.g.doubleclick.net https://formspree.io; upgrade-insecure-requests;"
      }
    ],
    [
      'script',
      { async: '', src: 'https://www.googletagmanager.com/gtag/js?id=G-95Q2GYDF2M' }
    ],
    [
      'script',
      {},
      `window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-95Q2GYDF2M');`
    ]
  ],
  cleanUrls: true,

  // Load .env files from project root (parent of docs folder)
  vite: {
    envDir: path.resolve(__dirname, '../../'),
    envPrefix: 'SUPABASE_'
  },

  themeConfig: {
    logo: '/logo.svg',
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: '首页', link: '/' },
      { text: 'AI 工具', link: '/ai-tools' },
      { text: 'AI 提示词', link: '/ai-prompts' },
      { text: 'AI 开发', link: '/ai-development' },
      { text: '设计资源', link: '/design-resources' },
      { text: '留言板', link: '/guestbook' },
      { text: '指南', link: '/guide/getting-started' },
      { text: '更新日志', link: '/changelog' },
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
          { text: '6. 进阶功能', link: '/guide/tutorial/6-advanced-features' },
          { text: '7. 管理后台', link: '/guide/tutorial/7-admin-dashboard' }
        ]
      },
      {
        text: '高价值内容',
        items: [
          { text: '核心架构 (付费)', link: '/paid/architecture' },
          { text: '变现逻辑 (付费)', link: '/paid/monetization' }
        ]
      },
      {
        text: 'AI 资源指南',
        items: [
          { text: 'Claude', link: '/guide/claude' },
          { text: 'Gemini', link: '/guide/gemini' },
          { text: 'OpenAI', link: '/guide/openai' },
          { text: 'AI 学习课程', link: '/guide/courses' },
          { text: '最新资讯', link: '/guide/latest_ai_news' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/wsj0415/ViteMind' }
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
