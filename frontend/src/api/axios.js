import axios from 'axios'

// In development: Vite proxies /api → http://localhost:5000 (no CORS)
// In production: set VITE_API_URL=https://your-backend.com/api
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
  withCredentials: false,
})

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('rh_token')
  if (token) {
    config.headers['Authorization'] = token
  }
  return config
})

// Global response error handler
// Note: we use lazy router import to avoid circular dependency
// (router → stores → api → router)
api.interceptors.response.use(
  (res) => res,
  async (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('rh_token')
      // Lazy import avoids circular dep at module init time
      const { default: router } = await import('@/router')
      if (router.currentRoute.value.name !== 'Login') {
        router.push('/login')
      }
    }
    return Promise.reject(err)
  }
)

export default api
