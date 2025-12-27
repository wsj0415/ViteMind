# 第六章：进阶功能开发 (Timeline & Supabase)

随着 ViteMind 的内容库日益丰富，我们面临着两个新的挑战：
1.  **展示形式单一**：仅有的网格视图难以体现 AI 发展的“时间脉络”。
2.  **数据存储风险**：仅依赖 JSON 文件虽然快，但不利于长期归档和复杂查询。

本章将带你实战两个进阶功能：复刻 TAAFT 的**时间轴视图**，以及构建 **JSON + Supabase** 的混合数据架构。

## 1. UI 进化：打造时间轴视图 (Timeline View)

我们希望用户能像坐“时光机”一样回顾 AI 的发展历程。

### 1.1 设计思路
在 `NewsGallery.vue` 中，我们需要引入**视图状态管理**。用户可以在 "GRID" (网格) 和 "TIMELINE" (时间轴) 之间自由切换。

### 1.2 核心代码实现

首先，我们需要一个能够将扁平的数组按月份分组的计算属性：

```javascript
// NewsGallery.vue

// 状态定义
const viewMode = ref('grid') // 'grid' | 'timeline'

// 核心算法：按月份分组
const groupedNews = computed(() => {
  const groups = {}
  filteredNews.value.forEach(item => {
    const date = new Date(item.date)
    // 生成 Key: e.g., "DEC 2025"
    const monthKey = date.toLocaleString('en-US', { month: 'short', year: 'numeric' }).toUpperCase()
    
    if (!groups[monthKey]) {
      groups[monthKey] = []
    }
    groups[monthKey].push(item)
  })
  return groups
})
```

### 1.3 瑞士风格 CSS
为了保持设计的一致性，时间轴采用极简的垂直线条设计，而非复杂的图标堆砌。

```css
.timeline-month {
  font-family: monospace;
  border-bottom: 2px solid var(--vp-c-text-1); /* 强烈的分割线 */
  letter-spacing: 0.1em;
}

.timeline-item:hover {
  transform: translateX(10px); /* 细微的交互反馈 */
}
```

---

## 2. 后端进化：混合数据架构 (Hybrid Architecture)

这是本项目的架构亮点。我们没有选择“完全迁移到数据库”，而是采用了 **Hybrid Mode**。

### 2.1 为什么选择混合架构？

| 方案 | 优点 | 缺点 |
| :--- | :--- | :--- |
| **纯 JSON (现状)** | **极速 (0ms Latency)**，免费，易于部署 | 数据量大时文件臃肿，无法查询 |
| **纯 Database** | 数据管理强大，支持动态查询 | 需要后端 API，**增加延迟**，有成本 |
| **Hybrid (混合)** | **兼具速度与深度** | 写入逻辑稍显复杂 |

**我们的策略**：
-   **读 (Read)**：前端依然读取 `news.json`，确保用户打开网站是秒开的。
-   **写 (Write)**：脚本同时写入 `news.json` (用于展示) 和 `Supabase` (用于归档)。

### 2.2 Supabase 集成步骤

#### 第一步：创建表结构 (SQL)
在 Supabase SQL Editor 中运行：

```sql
create table public.news (
  id text primary key,
  title text not null,
  summary text,
  detail text,
  link text unique,
  tags text[],
  date date,
  created_at timestamp with time zone default timezone('utc'::text, now())
);
```

#### 第二步：Python 脚本改造
在 `generate_news.py` 中引入 `supabase` 客户端：

```python
def save_to_supabase(new_items):
    # 初始化客户端
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    
    # 准备数据并执行 Upsert (插入或更新)
    data = [...] 
    supabase.table("news").upsert(data).execute()
```

#### 第三步：GitHub Actions 配置
为了安全，我们绝不能将密钥硬编码在代码里。需要在 GitHub 仓库的 **Settings -> Secrets** 中配置：
-   `SUPABASE_URL`
-   `SUPABASE_KEY` (使用 Service Role Key 以获得写入权限)

## 3. 总结
通过这次迭代，ViteMind 不仅在视觉上更具探索性，在底层架构上也具备了企业级的稳健性。这就是 "Build in Public" 的魅力——我们不仅是在写代码，更是在构建一个可扩展的系统。
