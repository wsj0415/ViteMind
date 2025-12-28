import requests
import json
import os
from datetime import datetime, timezone
import feedparser
try:
    from dotenv import load_dotenv
    load_dotenv('.env.local')
except ImportError:
    pass

# 配置
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://api-inference.modelscope.cn/v1/chat/completions"
MODEL_NAME = "MiniMax/MiniMax-M2.1" 

# 数据源
RSS_FEEDS = [
    "https://hnrss.org/newest?q=AI", # Hacker News AI
    "https://www.theverge.com/rss/artificial-intelligence/index.xml", # The Verge AI
    "https://techcrunch.com/category/artificial-intelligence/feed/", # TechCrunch AI
    "https://openai.com/news/rss.xml", # OpenAI News
    "https://research.google/blog/rss", # Google Research
    "https://machinelearningmastery.com/blog/feed/", # ML Mastery (Dev/Tutorial)
    "https://www.producthunt.com/feed?topic=artificial-intelligence", # Product Hunt AI (New Tools)
]

def fetch_rss_data():
    articles = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Current time in UTC
    now = datetime.now(timezone.utc)
    
    for feed_url in RSS_FEEDS:
        print(f"Fetching {feed_url}...")
        try:
            response = requests.get(feed_url, headers=headers, timeout=30)
            if response.status_code != 200:
                print(f"Failed to fetch {feed_url}, status code: {response.status_code}")
                continue
                
            feed = feedparser.parse(response.content)
            
            print(f"Found {len(feed.entries)} entries in {feed_url}")
            
            for entry in feed.entries:
                # Parse publication time
                published_time = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_time = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                
                # Filter: Only keep articles from the last 1 hour
                if published_time:
                    time_diff = now - published_time
                    if time_diff.total_seconds() > 3600: # 3600 seconds = 1 hour
                        continue
                else:
                    # If no time found, skip or keep? Let's skip to be safe for "hourly" updates
                    continue

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

    # Limit to top 5 articles to avoid token limits/timeouts
    articles = articles[:5]

    # 构建 Prompt
    news_text = "\n".join([f"- [{a['title']}]({a['link']}): {a['summary']}" for a in articles])
    prompt = f"""
    你是专业的 AI 行业分析师。请阅读以下原始新闻列表，筛选出 8-12 条最有价值的内容。
    
    **筛选标准（必须覆盖以下类别）：**
    1. 🚨 **大事件 (News)**: 24小时内的重大 AI 新闻 (OpenAI, Google 等)。
    2. 🎁 **促销 (Deals)**: AI 产品的限时优惠、Lifetime Deal (如 AppSumo 上的 AI 工具)。
    3. 🛠️ **编程 (Dev)**: AI 开发教程、Hugging Face 论文、LLM 部署指南。
    4. 🚀 **新产品 (New)**: Product Hunt 上的热门 AI 新品 (类似 TAAFT 时间轴)。

    请输出一个纯 JSON 数组（不要包含 Markdown 代码块标记 ```json ... ```），数组中每个对象包含以下字段：
    - title: (string) 中文标题，吸引人且专业。
    - summary: (string) 一句话中文摘要（50字以内），用于卡片展示。
    - detail: (string) 详细的中文深度解读（Markdown 格式），包含背景、核心技术点、行业影响等（300字左右）。
    - tags: (array of strings) 必须包含一个类别标签 ["News", "Deal", "Dev", "New"]，以及 1-2 个内容标签 (如 "LLM", "Python")。
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

    import time
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(OPENROUTER_URL, headers=headers, json=data)
            response.raise_for_status()
            content = response.json()['choices'][0]['message']['content']
            
            # 清理可能存在的 Markdown 代码块标记
            content = content.replace("```json", "").replace("```", "").strip()
            
            return json.loads(content)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print(f"Rate limit hit (429), retrying in {2 ** attempt} seconds...")
                time.sleep(2 ** attempt)
            else:
                print(f"AI Generation Error: {e}")
                return []
        except Exception as e:
            print(f"AI Generation Error: {e}")
            return []
    
    print("Max retries exceeded.")
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

    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(new_items)} items to {file_path}")

def save_to_supabase(new_items):
    try:
        from supabase import create_client, Client
    except ImportError:
        print("Supabase library not installed. Skipping Supabase upload.")
        return

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        print("Supabase credentials not found. Skipping Supabase upload.")
        return

    try:
        supabase: Client = create_client(url, key)
        
        # 准备数据，确保格式符合 Supabase 表结构
        data_to_upsert = []
        for item in new_items:
            data_to_upsert.append({
                "id": item.get("id"),
                "title": item.get("title"),
                "summary": item.get("summary"),
                "detail": item.get("detail"),
                "link": item.get("link"),
                "tags": item.get("tags"),
                "date": item.get("date")
            })
            
        if not data_to_upsert:
            return

        # 执行 Upsert
        response = supabase.table("news").upsert(data_to_upsert).execute()
        print(f"Successfully uploaded {len(data_to_upsert)} items to Supabase.")
        
    except Exception as e:
        print(f"Error uploading to Supabase: {e}")

if __name__ == "__main__":
    if not OPENROUTER_API_KEY:
        print("Error: OPENROUTER_API_KEY not found.")
        exit(1)

    print("Starting AI News Generator (JSON + Supabase)...")
    raw_articles = fetch_rss_data()
    print(f"Fetched {len(raw_articles)} articles.")
    
    ai_json = summarize_with_ai(raw_articles)
    
    # 1. 保存为本地 JSON (用于前端静态展示)
    save_to_json(ai_json)
    
    # 2. 上传到 Supabase (用于数据归档)
    save_to_supabase(ai_json)
    
    print("Done.")
