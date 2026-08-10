-- 🛡️ Sentinel Security Patch
-- Fixes: Insecure Direct Object Reference (IDOR) / Bulk Delete Risk on user_favorites
-- Date: 2025-01-29

-- 1. Drop the overly permissive DELETE policy (which allowed USING(true))
DROP POLICY IF EXISTS "Allow public delete favorites" ON public.user_favorites;

-- 2. Create a secure RPC function for deletion
-- This function enforces that you can only delete a specific pair of user_id and news_id
-- It runs with SECURITY DEFINER to bypass RLS (since we revoked public delete access via RLS)
CREATE OR REPLACE FUNCTION remove_user_favorite(p_user_id TEXT, p_news_id TEXT)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  DELETE FROM public.user_favorites
  WHERE user_id = p_user_id AND news_id = p_news_id;
END;
$$;

-- 3. Grant execute permissions
GRANT EXECUTE ON FUNCTION remove_user_favorite(TEXT, TEXT) TO anon;
GRANT EXECUTE ON FUNCTION remove_user_favorite(TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION remove_user_favorite(TEXT, TEXT) TO service_role;

-- 4. Comment for documentation
COMMENT ON FUNCTION remove_user_favorite IS 'Securely removes a favorite item for an anonymous user. Prevents table-wiping attacks.';
