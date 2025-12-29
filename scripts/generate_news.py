import requests
import json
import os
from datetime import datetime, timezone
import feedparser
try:
    from dotenv import load_dotenv
    loaded = load_dotenv('.env.local')
    if loaded:
        print("Loaded .env.local")
    else:
        print("Warning: .env.local not found or empty.")
except ImportError:
    print("Warning: python-dotenv not installed. Install it with `pip install python-dotenv` to load .env.local")

# 配置
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://api-inference.modelscope.cn/v1/chat/completions"
MODEL_NAME = "Qwen/Qwen2.5-Coder-32B-Instruct"

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
    
    # Fetch feeds from Supabase
    feeds = []
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL")
        # Prefer Service Role Key for backend scripts to bypass RLS
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
        if url and key:
            supabase = create_client(url, key)
            response = supabase.table("rss_feeds").select("*").eq("is_active", True).execute()
            feeds = response.data
        else:
            print("Supabase credentials missing, falling back to hardcoded feeds.")
            # Fallback structure
            feeds = [{"url": url, "name": "Unknown", "include_keywords": None, "exclude_keywords": None} for url in RSS_FEEDS]
    except Exception as e:
        print(f"Error fetching feeds from Supabase: {e}")
        feeds = [{"url": url, "name": "Unknown", "include_keywords": None, "exclude_keywords": None} for url in RSS_FEEDS]

    if not feeds:
        print("No active feeds found.")
        return []

    # Current time in UTC
    now = datetime.now(timezone.utc)
    
    for feed_config in feeds:
        feed_url = feed_config.get("url")
        feed_name = feed_config.get("name", "Unknown")
        include_kws = [k.strip().lower() for k in (feed_config.get("include_keywords") or "").split(",") if k.strip()]
        exclude_kws = [k.strip().lower() for k in (feed_config.get("exclude_keywords") or "").split(",") if k.strip()]

        print(f"Fetching {feed_name} ({feed_url})...")
        try:
            response = requests.get(feed_url, headers=headers, timeout=30)
            if response.status_code != 200:
                print(f"Failed to fetch {feed_url}, status code: {response.status_code}")
                # Update error status in DB
                if 'id' in feed_config:
                    try:
                        supabase.table("rss_feeds").update({
                            "error_message": f"HTTP {response.status_code}"
                        }).eq("id", feed_config['id']).execute()
                    except: pass
                continue
                
            feed = feedparser.parse(response.content)
            print(f"Found {len(feed.entries)} entries in {feed_name}")
            
            # Update success status in DB
            if 'id' in feed_config:
                try:
                    supabase.table("rss_feeds").update({
                        "last_success_at": datetime.now().isoformat(),
                        "error_message": None
                    }).eq("id", feed_config['id']).execute()
                except: pass

            for entry in feed.entries:
                # 1. Keyword Filtering
                title_summary = (entry.title + " " + entry.get("summary", "")).lower()
                
                # Exclude
                if any(kw in title_summary for kw in exclude_kws):
                    # print(f"Skipping (Exclude Keyword): {entry.title}")
                    continue
                
                # Include (only if defined)
                if include_kws and not any(kw in title_summary for kw in include_kws):
                    # print(f"Skipping (Missing Keyword): {entry.title}")
                    continue

                # 2. Time Filtering
                published_time = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_time = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                
                if published_time:
                    time_diff = now - published_time
                    if time_diff.total_seconds() > 86400: # 24 hours
                        continue
                else:
                    continue

                # 3. Content Extraction (Jina)
                jina_url = f"https://r.jina.ai/{entry.link}"
                # print(f"Reading with Jina: {jina_url}")
                try:
                    jina_resp = requests.get(jina_url, timeout=30) 
                    if jina_resp.status_code == 200 and "403 Forbidden" not in jina_resp.text:
                        content = jina_resp.text[:2000]
                    else:
                        content = entry.get("summary", "")
                except Exception as e:
                    content = entry.get("summary", "")

                if len(content) < 50:
                     content = entry.get("summary", "")

                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": content,
                    "date": published_time.strftime("%Y-%m-%d") if published_time else datetime.now().strftime("%Y-%m-%d"),
                    "source_name": feed_name # Pass source name for context
                })
        except Exception as e:
            print(f"Error fetching {feed_url}: {e}")
            if 'id' in feed_config:
                try:
                    supabase.table("rss_feeds").update({
                        "error_message": str(e)[:200]
                    }).eq("id", feed_config['id']).execute()
                except: pass
                
    return articles

def summarize_with_ai(articles):
    if not articles:
        return []

    # Limit to top 5 articles to avoid token limits/timeouts
    articles = articles[:5]

    # 构建 Prompt
    news_text = "\n".join([f"- [{a['date']}] [{a['title']}]({a['link']}): {a['summary']}" for a in articles])
    prompt = f"""
    你是专业的 AI 行业分析师。请阅读以下原始新闻列表，筛选并总结其中有价值的内容。
    
    **重要原则：**
    1. **真实性**：必须基于提供的原始新闻进行总结，**严禁编造**不存在的新闻或日期。
    2. **数量**：如果提供的有效新闻较少，就只总结这些，**不要强行凑数**。
    3. **日期**：请使用原始新闻中提供的日期。

    **筛选标准（优先关注）：**
    1. 🚨 **大事件 (News)**: 重大 AI 新闻 (OpenAI, Google 等)。
    2. 🎁 **促销 (Deals)**: AI 产品的限时优惠、Lifetime Deal。
    3. 🛠️ **编程 (Dev)**: AI 开发教程、Hugging Face 论文、LLM 部署指南。
    4. 🚀 **新产品 (New)**: Product Hunt 上的热门 AI 新品。

    请输出一个纯 JSON 数组（不要包含 Markdown 代码块标记 ```json ... ```），数组中每个对象包含以下字段：
    - title: (string) 中文标题，吸引人且专业。
    - summary: (string) 一句话中文摘要（50字以内），用于卡片展示。
    - detail: (string) 详细的中文深度解读（Markdown 格式），包含背景、核心技术点、行业影响等（300字左右）。
    - tags: (array of strings) 必须包含一个类别标签 ["News", "Deal", "Dev", "New"]，以及 1-2 个内容标签 (如 "LLM", "Python")。
    - link: (string) 原始链接。
    - date: (string) 日期，格式 YYYY-MM-DD (直接使用原始新闻的日期)。

    原始新闻：
    {news_text}
    """

    from openai import OpenAI, RateLimitError
    import time

    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://api-inference.modelscope.cn/v1/"
    )

    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            
            # 清理可能存在的 Markdown 代码块标记
            content = content.replace("```json", "").replace("```", "").strip()
            
            return json.loads(content)
        except RateLimitError:
            wait_time = 5 * (2 ** attempt) # 5s, 10s, 20s, 40s, 80s
            print(f"Rate limit hit (429), retrying in {wait_time} seconds...")
            time.sleep(wait_time)
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
    
    # Process all data (New + Existing) to remove duplicates
    # Prioritize new items (they are at the start of the list if we prepend them)

    # 为每条新数据添加 ID (简单的基于时间戳)
    for item in new_items:
        item['id'] = str(int(datetime.now().timestamp() * 1000)) + str(new_items.index(item))
        # 确保日期字段存在
        if 'date' not in item:
            item['date'] = datetime.now().strftime("%Y-%m-%d")

    combined_data = new_items + existing_data

    unique_data = []
    seen_links = set()
    seen_titles = set()

    for item in combined_data:
        link = item.get("link")
        title = item.get("title")

        is_duplicate = False
        if link and link in seen_links:
            is_duplicate = True
        if title and title in seen_titles:
            is_duplicate = True

        if is_duplicate:
            # print(f"Skipping duplicate in final list: {title}")
            continue

        unique_data.append(item)
        if link:
            seen_links.add(link)
        if title:
            seen_titles.add(title)

    updated_data = unique_data[:100]

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
    # Prefer Service Role Key for backend scripts to bypass RLS
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")

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

        # 执行 Upsert (如果 link 重复则更新)
        response = supabase.table("news").upsert(
            data_to_upsert,
            on_conflict="link"  # 使用 link 作为冲突键
        ).execute()
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
