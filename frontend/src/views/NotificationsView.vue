<template>
  <AppLayout>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Notifications</h1>
      <button @click="markAllRead" class="text-indigo-600 font-medium hover:underline text-sm">
        Mark all as read
      </button>
    </div>

    <div v-if="loading" class="text-gray-500">Loading...</div>
    <div v-else-if="!notifications.length" class="text-center py-10 bg-white rounded-xl border border-gray-100">
      <p class="text-gray-500">You're all caught up!</p>
    </div>
    <div v-else class="space-y-3">
      <div 
        v-for="notif in notifications" 
        :key="notif.id" 
        @click="markRead(notif)"
        :class="['bg-white rounded-xl shadow-sm border p-4 cursor-pointer transition', notif.is_read ? 'border-gray-100' : 'border-l-4 border-l-indigo-500 border-gray-100']"
      >
        <div class="flex justify-between items-start">
          <p :class="['text-sm', notif.is_read ? 'text-gray-600' : 'text-gray-900 font-medium']">{{ notif.message }}</p>
          <span class="text-xs text-gray-400 whitespace-nowrap ml-4">{{ new Date(notif.created_at).toLocaleString() }}</span>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { onMounted, computed } from 'vue'
import { useNotificationsStore } from '@/stores/notifications'
import AppLayout from '@/components/layout/AppLayout.vue'

const store = useNotificationsStore()

const loading = computed(() => store.loading)
const notifications = computed(() => store.notifications)

onMounted(() => {
  store.fetchNotifications()
})

const markRead = (notif) => {
  if (!notif.read) {
    store.markRead(notif.id)
  }
}

const markAllRead = () => {
  store.markAllRead()
}
</script>
