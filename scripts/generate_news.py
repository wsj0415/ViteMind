import requests
import json
import os
from datetime import datetime
import feedparser

# 配置
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "xiaomi/mimo-v2-flash:free" 

# 数据源
RSS_FEEDS = [
    "https://hnrss.org/newest?q=AI", 
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
                        content = jina_resp.text[:2000] # 增加截取长度
                    else:
                        print(f"Jina returned {jina_resp.status_code}, falling back to summary.")
                        content = entry.get("summary", "")
                except Exception as e:
                    print(f"Jina read failed: {e}")
                    content = entry.get("summary", "")

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
        return []

    # 构建 Prompt
    news_text = "\n".join([f"- [{a['title']}]({a['link']}): {a['summary']}" for a in articles])
    prompt = f"""
    你是专业的 AI 行业分析师。请阅读以下原始新闻列表，筛选出 5-8 条最有价值的 AI 技术进展或行业动态。
    
    请输出一个纯 JSON 数组（不要包含 Markdown 代码块标记 ```json ... ```），数组中每个对象包含以下字段：
    - title: (string) 中文标题，吸引人且专业。
    - summary: (string) 一句话中文摘要（50字以内），用于卡片展示。
    - detail: (string) 详细的中文深度解读（Markdown 格式），包含背景、核心技术点、行业影响等（300字左右）。
    - tags: (array of strings) 1-2 个标签，如 ["LLM", "Agent", "Hardware"]。
    - link: (string) 原始链接。
    - date: (string) 日期，格式 YYYY-MM-DD。

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
        content = response.json()['choices'][0]['message']['content']
        
        # 清理可能存在的 Markdown 代码块标记
        content = content.replace("```json", "").replace("```", "").strip()
        
        return json.loads(content)
    except Exception as e:
        print(f"AI Generation Error: {e}")
        return []

def save_to_json(new_items):
    if not new_items:
        print("No new items to save.")
        return

    file_path = "docs/public/data/news.json"
    
    # 读取现有数据
    existing_data = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            existing_data = []
    
    # 合并数据（将新数据插到最前面）
    # 为每条数据添加 ID (简单的基于时间戳)
    for item in new_items:
        item['id'] = str(int(datetime.now().timestamp() * 1000)) + str(new_items.index(item))
        # 确保日期字段存在
        if 'date' not in item:
            item['date'] = datetime.now().strftime("%Y-%m-%d")

    updated_data = new_items + existing_data
    
    # 限制总条数，防止文件过大（保留最近 100 条）
    updated_data = updated_data[:100]

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(new_items)} items to {file_path}")

if __name__ == "__main__":
    if not OPENROUTER_API_KEY:
        print("Error: OPENROUTER_API_KEY not found.")
        exit(1)

    print("Starting AI News Generator (JSON Mode)...")
    raw_articles = fetch_rss_data()
    print(f"Fetched {len(raw_articles)} articles.")
    
    ai_json = summarize_with_ai(raw_articles)
    save_to_json(ai_json)
    print("Done.")
