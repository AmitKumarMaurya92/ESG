import { useState, useEffect } from 'react'
import { supabaseService } from '../services/supabaseService'

export function useSupabaseStatus() {
  const [statusData, setStatusData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const checkStatus = async () => {
    setLoading(true)
    try {
      const data = await supabaseService.fetchStatus()
      setStatusData(data)
      setError(null)
    } catch (err) {
      setError(err.message || 'Failed to check status')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    checkStatus()
  }, [])

  return { statusData, loading, error, refresh: checkStatus }
}
