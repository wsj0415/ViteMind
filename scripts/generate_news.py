import requests
import json
import os
import argparse
from pathlib import Path
from urllib.parse import urlsplit
from datetime import datetime, timezone, timedelta
from sentinel_safe_requests import safe_get
import feedparser
try:
    from dotenv import load_dotenv
    loaded = load_dotenv('.env.local')
    if loaded:
        print("Loaded .env.local")
    else:
        print("Warning: .env.local not found or empty.")
except ImportError:
    pass

# 配置
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://api-inference.modelscope.cn/v1/chat/completions"
MODEL_NAME = os.environ.get("NEWS_MODEL", "Qwen/Qwen3.5-397B-A17B")
DATA_FILE_PATH = "docs/public/data/news.json"

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

def load_knowledge_base():
    """Load existing news to build a set of known URLs."""
    known_links = set()
    if os.path.exists(DATA_FILE_PATH):
        try:
            with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    if "link" in item:
                        known_links.add(item["link"])
        except json.JSONDecodeError:
            pass
    return known_links

def fetch_rss_data(known_links):
    """Fetch all feeds, filter out known items, and return a globally sorted list of candidates."""
    candidates = []
    successful_feeds = 0
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    # Supabase feeds fetching logic remains (omitted for brevity if not strictly needed, but good to keep)
    feeds = []
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
        if url and key:
            supabase = create_client(url, key)
            response = supabase.table("rss_feeds").select("*").eq("is_active", True).execute()
            feeds = response.data
    except Exception as e:
        print(f"Supabase feeds fetch error: {e}")

    if not feeds:
        feeds = [{"url": url, "name": "Unknown", "include_keywords": None, "exclude_keywords": None} for url in RSS_FEEDS]

    now = datetime.now(timezone.utc)
    
    for feed_config in feeds:
        feed_url = feed_config.get("url")
        feed_name = feed_config.get("name", "Unknown")
        include_kws = [k.strip().lower() for k in (feed_config.get("include_keywords") or "").split(",") if k.strip()]
        exclude_kws = [k.strip().lower() for k in (feed_config.get("exclude_keywords") or "").split(",") if k.strip()]

        print(f"Fetching {feed_name} ({feed_url})...")
        try:
            # Sentinel: Use safe_get to prevent SSRF
            response = safe_get(feed_url, headers=headers, timeout=30)
            if response.status_code != 200:
                print(f"Failed to fetch {feed_url}, status: {response.status_code}")
                continue
                
            feed = feedparser.parse(response.content)
            if feed.bozo and not feed.entries:
                print(f"Failed to parse {feed_url}")
                continue
            successful_feeds += 1

            for entry in feed.entries:
                link = entry.link
                
                # 1. Global De-duplication (Early Exit)
                if link in known_links:
                    continue

                # 2. Keyword Filtering
                title_summary = (entry.title + " " + entry.get("summary", "")).lower()
                if any(kw in title_summary for kw in exclude_kws):
                    continue
                if include_kws and not any(kw in title_summary for kw in include_kws):
                    continue

                # 3. Time Filtering (24h window)
                published_time = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_time = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    published_time = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
                
                if not published_time:
                    continue

                # Clamp future dates to now
                if published_time > now:
                    published_time = now

                time_diff = now - published_time
                if time_diff.total_seconds() > 86400: # 24 hours
                    continue

                # 4. Content Extraction (Jina) - Only for candidates we might actually use
                # To save time, we will fetch content later ONLY for the top candidates

                candidates.append({
                    "title": entry.title,
                    "link": link,
                    "summary_raw": entry.get("summary", ""),
                    "date_obj": published_time,
                    "date": published_time.strftime("%Y-%m-%d"),
                    "source_name": feed_name
                })

        except Exception as e:
            print(f"Error fetching {feed_url}: {e}")

    if not successful_feeds:
        raise RuntimeError("All RSS feeds failed; cannot determine whether there is new content.")

    # Prioritize developer-relevant topics, with at most two items per source.
    keywords = ("agent", "open source", "open-source", "developer", "coding", "model", "llm", "api", "github", "模型", "开源")
    for item in candidates:
        text = (item["title"] + " " + item["summary_raw"]).lower()
        item["relevance_score"] = sum(1 for keyword in keywords if keyword in text)
    candidates.sort(key=lambda x: (x["relevance_score"], x["date_obj"]), reverse=True)
    diversified, seen, counts = [], set(), {}
    for item in candidates:
        host = urlsplit(item["link"]).hostname or "unknown"
        if item["link"] in seen or counts.get(host, 0) >= 2:
            continue
        seen.add(item["link"])
        counts[host] = counts.get(host, 0) + 1
        diversified.append(item)
    return diversified

def enrich_candidates(candidates):
    """Fetch content for the selected top candidates."""
    enriched = []
    print(f"Enriching top {len(candidates)} candidates...")

    for item in candidates:
        jina_url = f"https://r.jina.ai/{item['link']}"
        content = item['summary_raw']
        try:
            # Sentinel: Use safe_get to prevent SSRF
            jina_resp = safe_get(jina_url, timeout=15) # Shorter timeout
            if jina_resp.status_code == 200 and "403 Forbidden" not in jina_resp.text:
                content = jina_resp.text[:2000]
        except Exception:
            pass # Fallback to raw summary

        if len(content) < 50:
             content = item['summary_raw']

        item['source_quality'] = "full_text_excerpt" if content != item['summary_raw'] else "rss_summary"
        item['summary'] = content
        enriched.append(item)

    return enriched

def distill_wisdom(articles):
    """Summarize with AI."""
    if not articles:
        return []

    print(f"Distilling wisdom from {len(articles)} articles...")

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
    - detail: (string) 根据来源撰写简短 Markdown 正文，只写有依据的事实；材料不足时不推测背景、数字和影响。
    - tags: (array of strings) 必须包含一个类别标签 ["News", "Deal", "Dev", "New"]，以及 1-2 个内容标签 (如 "LLM", "Python")。
    - link: (string) 原始链接。
    - date: (string) 日期，格式 YYYY-MM-DD (直接使用原始新闻的日期)。

    无法确认的信息请省略。不要把传闻描述为事实，不能为凑字数而推断。
    原始新闻：
    {news_text}
    """

    from openai import OpenAI, AuthenticationError, PermissionDeniedError
    import time

    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://api-inference.modelscope.cn/v1/",
        timeout=60.0,
        max_retries=0,
    )

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except (AuthenticationError, PermissionDeniedError) as e:
            raise RuntimeError(
                f"ModelScope authentication/permission failure (HTTP {e.status_code}). "
                "Check the API key and complete account email verification at "
                "https://modelscope.cn/my/settings/account. News was not updated."
            ) from None
        except Exception as e:
            print(f"AI Generation Error (Attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
    
    raise RuntimeError("AI generation failed after 3 attempts. News was not updated.")

def archive_history(new_items):
    """Merge new items with history and save."""
    if not new_items:
        print("No new items to archive.")
        return

    # Assign IDs
    for item in new_items:
        item['id'] = str(int(datetime.now().timestamp() * 1000)) + str(new_items.index(item))
        if 'date' not in item:
            item['date'] = datetime.now().strftime("%Y-%m-%d")

    existing_data = []
    if os.path.exists(DATA_FILE_PATH):
        try:
            with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except json.JSONDecodeError:
            pass

    # Merge: Newest items at the top
    combined = new_items + existing_data

    # Final De-duplication (Safety Net)
    unique_data = []
    seen = set()
    for item in combined:
        if item['link'] not in seen:
            unique_data.append(item)
            seen.add(item['link'])

    # Sort by Date Descending
    unique_data.sort(key=lambda x: x['date'], reverse=True)

    # Keep last 100
    final_data = unique_data[:100]

    os.makedirs(os.path.dirname(DATA_FILE_PATH), exist_ok=True)
    with open(DATA_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    print(f"Archived {len(new_items)} new items. Total history: {len(final_data)}")

    # Upload to Supabase
    save_to_supabase(new_items)

def save_to_supabase(new_items):
    try:
        from supabase import create_client
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY")
        if url and key:
            supabase = create_client(url, key)
            data_to_upsert = [{
                "id": item.get("id"),
                "title": item.get("title"),
                "summary": item.get("summary"),
                "detail": item.get("detail"),
                "link": item.get("link"),
                "tags": item.get("tags"),
                "date": item.get("date")
            } for item in new_items]
            
            supabase.table("news").upsert(data_to_upsert, on_conflict="link").execute()
            print(f"Synced {len(data_to_upsert)} items to Supabase.")
    except Exception as e:
        print(f"Supabase sync error: {e}")

def validate_insights(insights, candidates):
    """Accept only known candidate URLs, and derive dates from the source."""
    if not isinstance(insights, list):
        raise ValueError("Model output must be a JSON array")
    originals = {item["link"]: item for item in candidates}
    validated, seen = [], set()
    for item in insights:
        if not isinstance(item, dict):
            raise ValueError("Each generated item must be an object")
        link = item.get("link")
        if not isinstance(link, str) or link not in originals or link in seen:
            raise ValueError("Generated link is unknown or duplicated")
        for field in ("title", "summary", "detail"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"Invalid {field}")
        if not isinstance(item.get("tags"), list) or not item["tags"] or not all(isinstance(t, str) and t.strip() for t in item["tags"]):
            raise ValueError("Invalid tags")
        source = originals[link]
        item = {k: item[k] for k in ("title", "summary", "detail", "tags", "link")}
        item["date"] = source["date"]
        item["review_status"] = "pending"
        item["source_name"] = source.get("source_name", "Unknown")
        item["source_quality"] = source.get("source_quality", "unknown")
        item["source_excerpt"] = source.get("summary", "")
        validated.append(item)
        seen.add(link)
    return validated


def write_draft(path, items):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(f"Review file already exists: {path}")
    path.write_text(json.dumps({"version": 1, "model": MODEL_NAME, "items": items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(items)} pending items to {path}")


def publish_approved(path):
    draft = json.loads(Path(path).read_text(encoding="utf-8"))
    if draft.get("version") != 1 or not isinstance(draft.get("items"), list):
        raise ValueError("Invalid review file")
    items = draft["items"]
    if any(i.get("review_status") not in ("pending", "approved", "rejected") for i in items):
        raise ValueError("Invalid review status")
    approved = [i for i in items if i["review_status"] == "approved"]
    if not approved:
        print("No approved items to publish.")
        return
    checked = validate_insights(approved, approved)
    clean = [{k: item[k] for k in ("title", "summary", "detail", "tags", "link", "date")} for item in checked]
    archive_history(clean)


def publish_auto(insights):
    """Publish a validated model selection in automatic mode.

    The existing workflow uses a static JSON file for GitHub Pages, so this
    function is deliberately small and validates the same provenance fields
    before changing that file. It never treats an empty selection as an error.
    """
    if not insights:
        print("No new items to auto-publish.")
        return
    if not isinstance(insights, list) or len(insights) > 5:
        raise ValueError("Automatic publication accepts one to five items")
    links = set()
    required = ("title", "summary", "detail", "tags", "link", "date")
    for item in insights:
        if not isinstance(item, dict) or any(not item.get(field) for field in required):
            raise ValueError("Automatic publication item is incomplete")
        if not isinstance(item["tags"], list) or not all(isinstance(tag, str) and tag.strip() for tag in item["tags"]):
            raise ValueError("Automatic publication tags are invalid")
        link = item["link"]
        if link in links:
            raise ValueError("Automatic publication contains duplicate links")
        links.add(link)
    archive_history([dict(item) for item in insights])


def main():
    parser = argparse.ArgumentParser(description="Generate a review draft or publish approved news")
    parser.add_argument("--publish", metavar="DRAFT", help="Publish approved items from a reviewed JSON file")
    parser.add_argument("--auto-publish", action="store_true", help="Publish the validated selection immediately")
    parser.add_argument("--draft", default="output/news-review/draft.json", help="Path for pending draft")
    parser.add_argument("--candidates-output", help="Save enriched candidates for model comparison")
    args = parser.parse_args()
    if args.publish and args.auto_publish:
        parser.error("--publish and --auto-publish cannot be combined")
    if args.publish:
        publish_approved(args.publish)
        return
    if not OPENROUTER_API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY not found")
    known_links = load_knowledge_base()
    candidates = fetch_rss_data(known_links)
    print(f"Gathered {len(candidates)} new candidates.")
    if not candidates:
        write_draft(args.draft, [])
        return
    enriched = enrich_candidates(candidates[:15])
    if args.candidates_output:
        path = Path(args.candidates_output)
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            raise FileExistsError(path)
        serializable = [{k: v for k, v in item.items() if k != "date_obj"} for item in enriched]
        path.write_text(json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8")
    insights = distill_wisdom(enriched)
    validated = validate_insights(insights, enriched)
    write_draft(args.draft, validated)
    if args.auto_publish:
        publish_auto(validated)


if __name__ == "__main__":
    main()
