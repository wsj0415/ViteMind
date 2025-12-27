---
layout: doc
title: 2. AI 自动化引擎
---

# 实战第二章：打造 AI 自动化引擎

本章是 ViteMind 的核心。我们将编写一个 Python 脚本，并利用 GitHub Actions 实现**全自动**的新闻抓取与更新。

## 🧠 核心逻辑

我们的自动化流程如下：
1.  **Fetch**: 抓取 RSS 源或网页数据。
2.  **Think**: 调用 LLM (如 OpenAI/DeepSeek) 进行总结与翻译。
3.  **Write**: 生成 JSON 数据与 Markdown 文件。
4.  **Deploy**: 自动提交代码并发布。

## 🐍 编写 Python 脚本

在项目根目录创建 `scripts/generate_news.py`。

> [!IMPORTANT] ⚠️ 避坑指南：API Key 安全
> **绝对不要**将你的 API Key 直接写在代码里提交到 GitHub！
> 必须使用环境变量：`api_key = os.getenv("OPENAI_API_KEY")`

```python
import os
import json
import requests
from datetime import datetime

# 模拟一个简单的新闻生成器
def generate_news():
    # 1. 获取 API Key (从环境变量)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: API Key not found!")
        return

    # 2. 这里可以调用 LLM API (省略具体实现)
    # ...
    
    # 3. 生成数据结构
    news_data = [
        {
            "title": "AI 正在改变世界",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "summary": "这是一个自动生成的新闻摘要...",
            "tags": ["AI", "Tech"]
        }
    ]

    # 4. 写入文件
    output_path = "docs/public/data/news.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    print("✅ News generated successfully!")

if __name__ == "__main__":
    generate_news()
```

## ⚙️ 配置 GitHub Actions

在 `.github/workflows/daily_news.yml` 中配置定时任务。

```yaml
name: Daily AI News

on:
  schedule:
    - cron: '0 0 * * *' # 每天 UTC 0点运行
  workflow_dispatch: # 允许手动触发

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Install Dependencies
        run: |
          pip install requests openai
          
      - name: Generate News
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }} # 🔑 关键点！
        run: python scripts/generate_news.py
        
      - name: Commit and Push
        run: |
          git config --global user.name 'GitHub Action'
          git config --global user.email 'action@github.com'
          git add .
          git commit -m "Auto-update news" || exit 0
          git push
```

> [!TIP] 💡 如何设置 Secrets?
> 进入 GitHub 仓库 -> **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**。
> 名字填 `OPENAI_API_KEY`，值填你的密钥。

---

**下一章预告**：有了数据，我们需要一个漂亮的界面来展示它。👉 [第三章：定制化开发](./3-customization.md)
