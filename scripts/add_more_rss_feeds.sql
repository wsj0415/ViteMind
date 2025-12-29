-- Insert additional high-quality AI RSS feeds
insert into public.rss_feeds (name, url, category, is_active)
values
  ('Microsoft AI Blog', 'https://news.microsoft.com/source/topic/ai/feed/', 'News', true),
  ('Meta AI Research', 'https://research.facebook.com/feed', 'Dev', true),
  ('Hugging Face Blog', 'https://hf.co/blog/feed.xml', 'Dev', true),
  ('MIT News - Machine Learning', 'https://news.mit.edu/rss/topic/machine-learning', 'News', true),
  ('Berkeley AI Research (BAIR)', 'https://bair.berkeley.edu/blog/feed.xml', 'Dev', true),
  ('LangChain Blog', 'https://blog.langchain.dev/rss/', 'Dev', true),
  ('Stability AI', 'https://stability.ai/blog?format=rss', 'New', true)
on conflict (url) do nothing;
