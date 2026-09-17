/**
 * Health service — calls the backend health endpoint.
 * Used by the frontend to verify API connectivity.
 */
import apiClient from '../api/client'

export async function fetchHealth() {
  const { data } = await apiClient.get('/health')
  return data
}
