<template>
  <header class="bg-white shadow-sm h-16 flex items-center justify-between px-6 border-b shrink-0">
    <!-- Left: page title -->
    <div class="text-base font-semibold text-gray-700">
      <span v-if="projectId && currentProjectTitle">
        <router-link to="/projects" class="text-gray-400 hover:text-gray-600">Projects</router-link>
        <span class="mx-1 text-gray-300">/</span>
        <span class="text-gray-800">{{ currentProjectTitle }}</span>
      </span>
      <span v-else>{{ routeTitle }}</span>
    </div>

    <!-- Right: actions -->
    <div class="flex items-center gap-2">
      <!-- Notifications bell -->
      <router-link
        to="/notifications"
        class="relative p-2 text-gray-500 hover:text-indigo-600 hover:bg-gray-100 rounded-full transition"
        title="Notifications"
      >
        <Bell class="w-5 h-5" />
        <span
          v-if="unreadCount > 0"
          class="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center leading-none"
        >
          {{ unreadCount > 9 ? '9+' : unreadCount }}
        </span>
      </router-link>

      <!-- Profile avatar (click → /profile) -->
      <div class="relative" ref="menuRef">
        <button
          @click="menuOpen = !menuOpen"
          class="w-9 h-9 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm hover:bg-indigo-200 transition focus:outline-none focus:ring-2 focus:ring-indigo-400"
          :title="auth.fullName || auth.user?.username"
        >
          {{ userInitials }}
        </button>

        <!-- Dropdown -->
        <Transition
          enter-active-class="transition ease-out duration-100"
          enter-from-class="transform opacity-0 scale-95"
          enter-to-class="transform opacity-100 scale-100"
          leave-active-class="transition ease-in duration-75"
          leave-from-class="transform opacity-100 scale-100"
          leave-to-class="transform opacity-0 scale-95"
        >
          <div
            v-if="menuOpen"
            class="absolute right-0 mt-2 w-52 bg-white rounded-xl shadow-lg border border-gray-100 py-1 z-50"
          >
            <div class="px-4 py-2 border-b border-gray-100">
              <p class="text-sm font-semibold text-gray-800 truncate">{{ auth.fullName || auth.user?.username }}</p>
              <p class="text-xs text-gray-400 truncate">{{ auth.user?.email }}</p>
            </div>
            <router-link
              to="/profile"
              @click="menuOpen = false"
              class="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
            >
              <User class="w-4 h-4 text-gray-400" /> My Profile
            </router-link>
            <router-link
              to="/notifications"
              @click="menuOpen = false"
              class="flex items-center gap-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
            >
              <Bell class="w-4 h-4 text-gray-400" /> Notifications
              <span v-if="unreadCount" class="ml-auto bg-red-500 text-white text-xs px-1.5 rounded-full">{{ unreadCount }}</span>
            </router-link>
            <div class="border-t border-gray-100 mt-1">
              <button
                @click="handleLogout"
                class="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
              >
                <LogOut class="w-4 h-4" /> Sign out
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProjectsStore } from '@/stores/projects'
import { useNotificationsStore } from '@/stores/notifications'
import { Bell, User, LogOut } from 'lucide-vue-next'

const route = useRoute()
const auth = useAuthStore()
const projectsStore = useProjectsStore()
const notificationsStore = useNotificationsStore()

const menuOpen = ref(false)
const menuRef = ref(null)

const projectId = computed(() => route.params.id)
const currentProjectTitle = computed(() => projectsStore.currentProject?.title || '')
const unreadCount = computed(() => notificationsStore.unreadCount)

const routeTitles = {
  Dashboard: 'Dashboard',
  Projects: 'My Projects',
  Notifications: 'Notifications',
  Profile: 'My Profile',
  Admin: 'Admin',
  Tasks: 'Tasks',
  Papers: 'Papers',
  Members: 'Members',
  Milestones: 'Milestones',
  References: 'References',
}
const routeTitle = computed(() => routeTitles[route.name] || route.name || '')

const userInitials = computed(() => {
  const u = auth.user
  if (!u) return 'U'
  if (u.first_name && u.last_name) return (u.first_name[0] + u.last_name[0]).toUpperCase()
  if (u.username) return u.username.substring(0, 2).toUpperCase()
  return 'U'
})

const handleLogout = () => {
  menuOpen.value = false
  auth.logout()
}

// Close dropdown when clicking outside
const handleClickOutside = (e) => {
  if (menuRef.value && !menuRef.value.contains(e.target)) {
    menuOpen.value = false
  }
}
onMounted(() => document.addEventListener('click', handleClickOutside))
onUnmounted(() => document.removeEventListener('click', handleClickOutside))
</script>
