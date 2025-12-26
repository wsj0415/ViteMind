# 核心架构设计

本文将深入探讨 ViteMind 的底层架构与设计哲学。

## 1. 为什么选择 VitePress？

VitePress 是基于 Vue 3 和 Vite 的静态站点生成器...（此处为免费预览内容）

<PayWall id="arch_001" price="19.9">
  <template #preview>
    <p>🔒 <strong>付费内容预览：</strong></p>
    <ul>
      <li>SSR 与 CSR 的深度融合策略</li>
      <li>如何利用 Service Worker 实现离线访问</li>
      <li>自定义主题的高级配置技巧</li>
    </ul>
  </template>

  ## 2. 深度架构解析 (付费解锁)

  恭喜你解锁了核心内容！🎉

  ### 2.1 双端渲染机制
  VitePress 在构建时会进行服务端渲染（SSR），生成静态 HTML，保证 SEO 和首屏速度。而在客户端，它会“水合”（Hydrate）为单页应用（SPA），提供无缝的路由体验。

  ### 2.2 性能优化
  我们使用了以下策略来保证极致性能：
  - **预加载 (Preload)**: 自动预加载可视区域内的链接资源。
  - **代码分割 (Code Splitting)**: 基于路由的自动代码分割。

  ### 2.3 部署架构
  ```mermaid
  graph LR
  A[Push Code] --> B[GitHub Actions]
  B --> C[Build]
  C --> D[Deploy to Pages]
  ```

  感谢您的支持！
</PayWall>
