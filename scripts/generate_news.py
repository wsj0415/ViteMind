import requests
import json
import os
from datetime import datetime
import feedparser

# 配置
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "xiaomi/mimo-v2-flash:free" # 用户指定免费模型

# 数据源
RSS_FEEDS = [
    "https://hnrss.org/newest?q=AI", # 简化查询参数
]

def fetch_rss_data():
    articles = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for feed_url in RSS_FEEDS:
        print(f"Fetching {feed_url}...")
        try:
            response = requests.get(feed_url, headers=headers, timeout=30)
            if response.status_code != 200:
                print(f"Failed to fetch {feed_url}, status code: {response.status_code}")
                continue
                
            feed = feedparser.parse(response.content)
            
            print(f"Found {len(feed.entries)} entries in {feed_url}")
            for entry in feed.entries[:5]: # 每个源只取前5条
                # 使用 Jina Reader 读取全文
                jina_url = f"https://r.jina.ai/{entry.link}"
                print(f"Reading with Jina: {jina_url}")
                try:
                    # Jina 可能会对某些 User-Agent 敏感，尝试不带特殊 UA 或使用默认
                    jina_resp = requests.get(jina_url, timeout=30) 
                    
                    if jina_resp.status_code == 200 and "403 Forbidden" not in jina_resp.text:
                        content = jina_resp.text[:2000] # 增加截取长度，获取更多信息
                    else:
                        print(f"Jina returned {jina_resp.status_code}, falling back to summary.")
                        content = entry.get("summary", "")
                except Exception as e:
                    print(f"Jina read failed: {e}")
                    content = entry.get("summary", "")

                # 如果内容太短（可能是空或错误），也回退到摘要
                if len(content) < 50:
                     content = entry.get("summary", "")

                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": content 
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
    index_file = "docs/news/index.md"
    
    new_entry = f"""
## {today} AI 日报

{content}

---
"""
    
    try:
        with open(index_file, "r", encoding="utf-8") as f:
            existing_content = f.read()
    except FileNotFoundError:
        existing_content = "# 🤖 AI 情报局\n\n这里汇集了由 AI 自动整理的每日行业动态。\n\n---\n"

    # 找到插入点（在 --- 之后）
    split_marker = "---\n"
    parts = existing_content.split(split_marker, 1)
    
    if len(parts) == 2:
        header, body = parts
        updated_content = f"{header}{split_marker}\n{new_entry}\n{body}"
    else:
        updated_content = existing_content + "\n" + new_entry

    with open(index_file, "w", encoding="utf-8") as f:
        f.write(updated_content)
    print(f"Updated {index_file}")

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
