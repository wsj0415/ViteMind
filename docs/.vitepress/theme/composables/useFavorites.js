import { ref, onMounted } from 'vue'
import { getAnonymousSupabaseClient } from '../utils/supabase'

const favorites = ref([])
const isLoading = ref(true)
const supabase = getAnonymousSupabaseClient()
let userId = null

export function useFavorites() {

  // Get or Create User ID (Anonymous)
  const initUser = () => {
    if (typeof window === 'undefined') return
    const stored = localStorage.getItem('vitemind_user_id')
    if (stored) {
      userId = stored
    } else {
      // Simple random ID generation if crypto.randomUUID is not available in older browsers
      userId = crypto.randomUUID ? crypto.randomUUID() : 'user_' + Math.random().toString(36).substr(2, 9)
      localStorage.setItem('vitemind_user_id', userId)
    }
  }

  // Fetch Favorites
  const fetchFavorites = async () => {
    if (!supabase || !userId) {
      isLoading.value = false
      return
    }

    try {
      const { data, error } = await supabase
        .from('user_favorites')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })

      if (error) throw error

      // Map Supabase data to local format if needed, or just use as is
      // Assuming structure: { id, news_id, news_data: { ... }, created_at }
      favorites.value = data.map(item => ({
        ...item.news_data, // Spread original news data
        favoriteId: item.id, // Keep tracking ID
        addedAt: item.created_at
      }))
    } catch (e) {
      console.warn('[Favorites] Sync failed (table might be missing), falling back to local session only.', e)
      // Optional: Load from localStorage fallback if Supabase fails?
      // For now, we strictly follow the "Supabase" requirement but handle failure gracefully
      favorites.value = []
    } finally {
      isLoading.value = false
    }
  }

  // Toggle Favorite
  const toggleFavorite = async (newsItem) => {
    const isFav = favorites.value.some(f => f.id === newsItem.id)

    if (isFav) {
      await removeFavorite(newsItem.id)
    } else {
      await addFavorite(newsItem)
    }
  }

  // Add Favorite
  const addFavorite = async (newsItem) => {
    // Optimistic UI Update
    const newFav = { ...newsItem, addedAt: new Date().toISOString() }
    favorites.value.unshift(newFav)

    if (!supabase || !userId) return

    try {
      const { data, error } = await supabase
        .from('user_favorites')
        .insert([
          {
            user_id: userId,
            news_id: newsItem.id,
            news_data: newsItem
          }
        ])
        .select()

      if (error) throw error

      // Update with real ID from DB
      if (data && data[0]) {
        favorites.value[0].favoriteId = data[0].id
        favorites.value[0].addedAt = data[0].created_at
      }
    } catch (e) {
      console.error('[Favorites] Add failed:', e)
      // Rollback optimistic update
      favorites.value = favorites.value.filter(f => f.id !== newsItem.id)
    }
  }

  // Remove Favorite
  const removeFavorite = async (newsId) => {
    // Optimistic UI Update
    const prev = [...favorites.value]
    favorites.value = favorites.value.filter(f => f.id !== newsId)

    if (!supabase || !userId) return

    try {
      // Sentinel Security Fix: Use RPC to safely delete favorite, preventing table-wiping attacks
      const { error } = await supabase.rpc('remove_user_favorite', {
        p_user_id: userId,
        p_news_id: newsId
      })

      if (error) throw error
    } catch (e) {
      console.error('[Favorites] Remove failed:', e)
      // Rollback
      favorites.value = prev
    }
  }

  const isFavorite = (newsId) => {
    return favorites.value.some(f => f.id === newsId)
  }

  // Initialize on mount
  onMounted(() => {
    initUser()
    fetchFavorites()
  })

  return {
    favorites,
    isLoading,
    toggleFavorite,
    removeFavorite,
    isFavorite
  }
}
