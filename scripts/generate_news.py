import requests
import json
import os
from datetime import datetime
import feedparser

# 配置
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "google/gemini-2.0-flash-exp:free" # 使用免费模型

# 数据源
RSS_FEEDS = [
    "https://export.arxiv.org/rss/cs.AI", # Official Arxiv RSS
    "https://hnrss.org/newest?q=AI+LLM+GPT", # Hacker News AI related
]

def fetch_rss_data():
    articles = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for feed_url in RSS_FEEDS:
        print(f"Fetching {feed_url}...")
        try:
            # Use requests to fetch with headers to avoid 403 Forbidden
            response = requests.get(feed_url, headers=headers, timeout=30)
            if response.status_code != 200:
                print(f"Failed to fetch {feed_url}, status code: {response.status_code}")
                continue
                
            feed = feedparser.parse(response.content)
            
            if not feed.entries:
                print(f"No entries found in {feed_url}")
                continue
                
            print(f"Found {len(feed.entries)} entries in {feed_url}")
            for entry in feed.entries[:5]: # 每个源只取前5条
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.get("summary", "")[:200] # 截取摘要
                })
        except Exception as e:
            print(f"Error fetching {feed_url}: {e}")
    return articles

def summarize_with_ai(articles):
    if not articles:
        return "今日无重大 AI 新闻。"

    # 构建 Prompt
    news_text = "\n".join([f"- [{a['title']}]({a['link']}): {a['summary']}" for a in articles])
    prompt = f"""
    你是专业的 AI 行业分析师。请阅读以下原始新闻列表，筛选出 5-8 条最有价值的 AI 技术进展或行业动态。
    
    要求：
    1. 使用中文输出。
    2. 格式为 Markdown 列表。
    3. 每条新闻包含一个 Emoji 图标，标题（带原文链接），以及一句话的深度点评。
    4. 风格专业、简洁、有洞见。
    5. 最后加一段“今日总结”。

    原始新闻：
    {news_text}
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://vitemind.com", 
    }
    
    data = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"AI Generation Error: {e}")
        return f"AI 生成失败，请检查日志。\n\n原始数据：\n{news_text}"

def save_to_markdown(content):
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"docs/news/{today}.md"
    
    md_content = f"""---
title: AI 情报局 - {today}
---

# 🤖 AI 情报局 ({today})

> 本日报由 GitHub Actions 自动抓取，Gemini AI 整理生成。

{content}

---
*[ViteMind](/) - 构建你的数字资产金库*
"""
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Saved to {filename}")

if __name__ == "__main__":
    if not OPENROUTER_API_KEY:
        print("Error: OPENROUTER_API_KEY not found.")
        # For local testing without key, maybe generate dummy data or exit
        exit(1)

    print("Starting AI News Generator...")
    raw_articles = fetch_rss_data()
    print(f"Fetched {len(raw_articles)} articles.")
    
    ai_summary = summarize_with_ai(raw_articles)
    save_to_markdown(ai_summary)
    print("Done.")
