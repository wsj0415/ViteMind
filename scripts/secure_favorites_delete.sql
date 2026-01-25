-- Security Fix: Prevent mass deletion of favorites
-- Vulnerability: The previous RLS policy 'Allow public delete favorites' allowed 'USING (true)',
-- which meant anyone could delete ALL rows by sending a delete request without a filter.
-- Fix: We replace direct table deletes with a Security Definer RPC function that enforces
-- exact matching of user_id and news_id.

-- 1. Revoke the dangerous delete policy
DROP POLICY IF EXISTS "Allow public delete favorites" ON public.user_favorites;

-- 2. Create the secure deletion function
-- SECURITY DEFINER allows this function to bypass RLS, but we enforce logic inside.
CREATE OR REPLACE FUNCTION remove_user_favorite(p_user_id text, p_news_id text)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
  DELETE FROM public.user_favorites
  WHERE user_id = p_user_id AND news_id = p_news_id;
END;
$$;

-- 3. Grant execute permissions to anonymous and authenticated users
GRANT EXECUTE ON FUNCTION remove_user_favorite(text, text) TO anon;
GRANT EXECUTE ON FUNCTION remove_user_favorite(text, text) TO authenticated;
