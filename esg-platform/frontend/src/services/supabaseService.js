import { supabase } from '../lib/supabase'

/**
 * Service helpers for Supabase Auth, Storage, and Database interactions.
 */
export const supabaseService = {
  /**
   * Returns current active auth session.
   */
  async getSession() {
    const { data, error } = await supabase.auth.getSession()
    if (error) throw error
    return data.session
  },

  /**
   * Listen for Auth state changes (sign in, sign out, token refresh).
   */
  onAuthStateChange(callback) {
    return supabase.auth.onAuthStateChange(callback)
  },

  /**
   * Fetch backend Supabase integration health status.
   */
  async fetchStatus() {
    try {
      const response = await fetch('/api/v1/supabase/status')
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      return await response.json()
    } catch (err) {
      console.error('Failed to fetch Supabase status from backend:', err)
      return {
        status: 'disconnected',
        error: err.message,
      }
    }
  },

  /**
   * Upload document to Supabase Storage bucket.
   */
  async uploadDocument(bucketName, filePath, file) {
    const { data, error } = await supabase.storage.from(bucketName).upload(filePath, file, {
      upsert: true,
    })
    if (error) throw error
    return data
  },

  /**
   * Get public or signed URL for document.
   */
  getPublicUrl(bucketName, filePath) {
    const { data } = supabase.storage.from(bucketName).getPublicUrl(filePath)
    return data.publicUrl
  },
}
