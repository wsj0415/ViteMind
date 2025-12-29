-- Create rss_feeds table
create table if not exists public.rss_feeds (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  url text not null unique,
  category text default 'News',
  is_active boolean default true,
  include_keywords text, -- Comma separated keywords
  exclude_keywords text, -- Comma separated keywords
  last_success_at timestamptz,
  error_message text,
  created_at timestamptz default now()
);

-- Enable RLS
alter table public.rss_feeds enable row level security;

-- Policies
create policy "Allow public read access"
  on public.rss_feeds for select
  using (true);

create policy "Allow authenticated insert"
  on public.rss_feeds for insert
  with check (auth.role() = 'authenticated');

create policy "Allow authenticated update"
  on public.rss_feeds for update
  using (auth.role() = 'authenticated');

create policy "Allow authenticated delete"
  on public.rss_feeds for delete
  using (auth.role() = 'authenticated');

-- Seed initial data (optional, migrating from python script)
insert into public.rss_feeds (name, url, category, include_keywords)
values
  ('Hacker News (AI)', 'https://hnrss.org/newest?q=AI', 'News', null),
  ('The Verge (AI)', 'https://www.theverge.com/rss/artificial-intelligence/index.xml', 'News', null),
  ('TechCrunch (AI)', 'https://techcrunch.com/category/artificial-intelligence/feed/', 'News', null),
  ('OpenAI News', 'https://openai.com/news/rss.xml', 'News', null),
  ('Google Research', 'https://research.google/blog/rss', 'Dev', null),
  ('Machine Learning Mastery', 'https://machinelearningmastery.com/blog/feed/', 'Dev', null),
  ('Product Hunt (AI)', 'https://www.producthunt.com/feed?topic=artificial-intelligence', 'New', null)
on conflict (url) do nothing;
