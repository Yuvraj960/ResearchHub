<template>
  <div id="app-root">
    <router-view />
    <ToastNotification />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import ToastNotification from '@/components/common/ToastNotification.vue'

const authStore = useAuthStore()
const notificationsStore = useNotificationsStore()

onMounted(async () => {
  // Only restore session if a token exists in localStorage
  // and we haven't already loaded the user into state (e.g. fresh page load)
  if (authStore.token && !authStore.user) {
    try {
      await authStore.fetchMe()
      // Only fetch notifications after we've confirmed the user is valid
      await notificationsStore.fetchUnreadCount()
      notificationsStore.initSocketListeners()
    } catch (e) {
      // fetchMe already clears token on 401 — nothing more to do
    }
  } else if (authStore.token && authStore.user) {
    // User already in state (e.g. after login/register in same session)
    notificationsStore.initSocketListeners()
  }
})
</script>
