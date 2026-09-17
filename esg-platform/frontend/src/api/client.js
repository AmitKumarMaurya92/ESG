/**
 * API client configuration.
 *
 * Axios instance pre-configured for the ESG Platform backend.
 * Auth headers and interceptors will be added in Phase 3 (Authentication).
 */
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ── Response interceptor — structured error normalisation ─────────────────────
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Normalise error messages from the backend structured format
    const message =
      error.response?.data?.error?.message ||
      error.response?.data?.detail ||
      error.message ||
      'An unexpected error occurred.'
    return Promise.reject(new Error(message))
  }
)

export default apiClient
