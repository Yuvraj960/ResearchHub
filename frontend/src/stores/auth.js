import { defineStore } from 'pinia'
import { authAPI } from '@/api'
import { connectSocket, disconnectSocket } from '@/socket'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('rh_token') || null,
    loading: false,
    error: null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.user?.roles?.includes('admin'),
    fullName: (state) => {
      if (!state.user) return ''
      const name = `${state.user.first_name || ''} ${state.user.last_name || ''}`.trim()
      return name || state.user.username || ''
    },
  },

  actions: {
    _saveToken(token, user) {
      this.token = token
      this.user = user
      localStorage.setItem('rh_token', token)
    },

    async login(credentials) {
      this.loading = true
      this.error = null
      try {
        const res = await authAPI.login(credentials)
        const { user, token } = res.data.data
        this._saveToken(token, user)
        connectSocket(user.id)
        // Navigate after store is fully updated
        const { default: router } = await import('@/router')
        router.push('/dashboard')
      } catch (err) {
        this.error = err.response?.data?.error || 'Login failed'
        throw err
      } finally {
        this.loading = false
      }
    },

    async register(payload) {
      this.loading = true
      this.error = null
      try {
        await authAPI.register(payload)
        // Don't auto-login — send to login page so they sign in manually
        const { default: router } = await import('@/router')
        router.push({ path: '/login', query: { registered: '1' } })
      } catch (err) {
        this.error = err.response?.data?.error || 'Registration failed'
        throw err
      } finally {
        this.loading = false
      }
    },

    async logout() {
      try { await authAPI.logout() } catch (_) {}
      this.user = null
      this.token = null
      localStorage.removeItem('rh_token')
      disconnectSocket()
      const { default: router } = await import('@/router')
      router.push('/login')
    },

    async fetchMe() {
      if (!this.token) return
      this.loading = true
      try {
        const res = await authAPI.me()
        this.user = res.data.data
        connectSocket(this.user.id)
      } catch (err) {
        if (err.response?.status === 401) {
          // Token is invalid/expired — clear everything
          this.token = null
          this.user = null
          localStorage.removeItem('rh_token')
        }
        throw err
      } finally {
        this.loading = false
      }
    },

    async updateProfile(payload) {
      this.loading = true
      try {
        const res = await authAPI.updateMe(payload)
        this.user = res.data.data
        return res.data.data
      } finally {
        this.loading = false
      }
    },
  },
})
