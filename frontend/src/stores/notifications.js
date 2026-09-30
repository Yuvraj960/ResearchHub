import { defineStore } from 'pinia'
import { notificationsAPI } from '@/api'
import { getSocket } from '@/socket'

export const useNotificationsStore = defineStore('notifications', {
  state: () => ({
    notifications: [],
    unreadCount: 0,
    loading: false,
  }),

  actions: {
    async fetchNotifications() {
      this.loading = true
      this.error = null
      try {
        // Backend returns { message, data: { items: [...], total, pages, page } }
        const res = await notificationsAPI.list()
        const payload = res.data.data
        // Handle both flat array (legacy) and paginated response
        this.notifications = Array.isArray(payload) ? payload : (payload?.items || [])
        this.unreadCount = this.notifications.filter(n => !n.is_read).length
      } finally {
        this.loading = false
      }
    },

    async fetchUnreadCount() {
      try {
        const res = await notificationsAPI.unreadCount()
        this.unreadCount = res.data.data?.count || 0
      } catch (_) {}
    },

    async markRead(id) {
      await notificationsAPI.markRead(id)
      const n = this.notifications.find(n => n.id === id)
      if (n) {
        n.is_read = true
        this.unreadCount = Math.max(0, this.unreadCount - 1)
      }
    },

    async markAllRead() {
      await notificationsAPI.markAllRead()
      this.notifications.forEach(n => (n.is_read = true))
      this.unreadCount = 0
    },

    addNotification(notif) {
      this.notifications.unshift(notif)
      if (!notif.is_read) this.unreadCount++
    },

    initSocketListeners() {
      const socket = getSocket()
      if (socket) {
        socket.on('new_notification', (data) => {
          this.addNotification(data)
        })
      }
    },
  },
})

