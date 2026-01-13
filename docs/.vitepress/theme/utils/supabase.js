import { createClient } from '@supabase/supabase-js'

let supabaseInstance = null

export function getAnonymousSupabaseClient() {
  if (supabaseInstance) return supabaseInstance

  const supabaseUrl = import.meta.env.SUPABASE_URL
  const supabaseKey = import.meta.env.SUPABASE_KEY

  if (supabaseUrl && supabaseKey) {
    supabaseInstance = createClient(supabaseUrl, supabaseKey, {
      auth: {
        persistSession: false,
        autoRefreshToken: false,
        detectSessionInUrl: false
      }
    })
  }

  return supabaseInstance
}
