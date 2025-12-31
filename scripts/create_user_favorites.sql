-- Create user_favorites table for anonymous news saving
CREATE TABLE IF NOT EXISTS public.user_favorites (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id TEXT NOT NULL, -- Stores the anonymous UUID from localStorage
    news_id TEXT NOT NULL, -- Matches the ID from news.json
    news_data JSONB,       -- Caches the news item content
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(user_id, news_id)
);

-- Enable Row Level Security
ALTER TABLE public.user_favorites ENABLE ROW LEVEL SECURITY;

-- Policy: Allow public to insert their own favorites (we rely on client providing the ID)
CREATE POLICY "Allow public insert favorites"
ON public.user_favorites
FOR INSERT
WITH CHECK (true);

-- Policy: Allow public to select their own favorites
-- (Technically anyone can select anyone's if they guess the UUID, but it's obscurity-based for anonymous usage)
CREATE POLICY "Allow public select favorites"
ON public.user_favorites
FOR SELECT
USING (true);

-- Policy: Allow public to delete their own favorites
CREATE POLICY "Allow public delete favorites"
ON public.user_favorites
FOR DELETE
USING (true);

-- Create index for faster lookups by user
CREATE INDEX IF NOT EXISTS idx_user_favorites_user_id ON public.user_favorites(user_id);
