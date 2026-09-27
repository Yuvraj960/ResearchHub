<template>
  <nav class="bg-indigo-600 w-64 min-h-screen flex flex-col text-white">
    <div class="p-4 text-2xl font-bold border-b border-indigo-500 flex items-center gap-2">
      <Home class="w-6 h-6" /> ResearchHub
    </div>
    
    <div class="flex-1 py-4 overflow-y-auto flex flex-col gap-1 px-2">
      <router-link to="/dashboard" class="nav-link" active-class="active-link">
        <LayoutDashboard class="w-5 h-5"/> Dashboard
      </router-link>
      <router-link to="/projects" class="nav-link" active-class="active-link">
        <Folder class="w-5 h-5"/> My Projects
      </router-link>
      <router-link to="/notifications" class="nav-link" active-class="active-link">
        <Bell class="w-5 h-5"/> Notifications
        <span v-if="unreadCount" class="ml-auto bg-red-500 text-xs px-2 py-0.5 rounded-full">{{ unreadCount }}</span>
      </router-link>
      <router-link to="/profile" class="nav-link" active-class="active-link">
        <User class="w-5 h-5"/> Profile
      </router-link>
      <router-link v-if="isAdmin" to="/admin" class="nav-link" active-class="active-link">
        <Settings class="w-5 h-5"/> Admin
      </router-link>
      
      <!-- Project Context Navigation -->
      <div v-if="projectId" class="mt-6">
        <div class="px-4 text-xs font-semibold text-indigo-200 uppercase tracking-wider mb-2">Project</div>
        <router-link :to="`/projects/${projectId}`" class="nav-link text-sm" active-class="active-link">Overview</router-link>
        <router-link :to="`/projects/${projectId}/tasks`" class="nav-link text-sm" active-class="active-link">Tasks</router-link>
        <router-link :to="`/projects/${projectId}/papers`" class="nav-link text-sm" active-class="active-link">Papers</router-link>
        <router-link :to="`/projects/${projectId}/members`" class="nav-link text-sm" active-class="active-link">Members</router-link>
        <router-link :to="`/projects/${projectId}/milestones`" class="nav-link text-sm" active-class="active-link">Milestones</router-link>
        <router-link :to="`/projects/${projectId}/references`" class="nav-link text-sm" active-class="active-link">References</router-link>
      </div>
    </div>
    
    <div class="p-4 border-t border-indigo-500">
      <button @click="handleLogout" class="flex items-center gap-2 text-sm text-indigo-200 hover:text-white w-full px-2 py-2 rounded transition">
        <LogOut class="w-5 h-5"/> Logout
      </button>
    </div>
  </nav>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import { Home, LayoutDashboard, Folder, Bell, User, Settings, LogOut } from 'lucide-vue-next'

const route = useRoute()
const auth = useAuthStore()
const notifications = useNotificationsStore()

const projectId = computed(() => route.params.id)
const isAdmin = computed(() => auth.isAdmin)
const unreadCount = computed(() => notifications.unreadCount)

const handleLogout = () => {
  auth.logout()
}
</script>

<style scoped>
.nav-link {
  @apply flex items-center gap-3 px-3 py-2 text-indigo-100 rounded hover:bg-indigo-500 transition-colors;
}
.active-link {
  @apply bg-indigo-700 text-white font-medium;
}
</style>
