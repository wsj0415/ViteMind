-- Insert niche RSS feeds for Indie Dev, Automation, and AI Video
insert into public.rss_feeds (name, url, category, is_active, include_keywords)
values
  -- Indie Dev & Monetization
  -- ('Indie Hackers (Top Today)', 'https://ihrss.io/top/today', 'New', true, null), -- SSL Error
  ('Product Hunt (Daily)', 'https://www.producthunt.com/feed', 'New', true, null),
  
  -- Automation (N8N, Zapier)
  ('N8N Blog', 'https://blog.n8n.io/rss/', 'Dev', true, null),
  ('Zapier Blog', 'https://zapier.com/blog/feeds/latest/', 'Dev', true, 'AI,Automation,Workflow'),
  
  -- AI Coding
  ('Cursor Blog', 'https://www.cursor.com/rss.xml', 'Dev', true, null),
  ('LangChain Blog', 'https://blog.langchain.dev/rss/', 'Dev', true, null),
  
  -- AI Video & Creative
  ('OpenAI News', 'https://openai.com/news/rss.xml', 'News', true, 'Sora,Video,DALL-E'),
  -- ('Stability AI', 'https://stability.ai/blog?format=rss', 'New', true, 'Video,Stable Diffusion'), -- 404 Error
  ('Runway Updates (Unofficial/News)', 'https://news.google.com/rss/search?q=RunwayML+AI+Video&hl=en-US&gl=US&ceid=US:en', 'News', true, null)

on conflict (url) do nothing;
