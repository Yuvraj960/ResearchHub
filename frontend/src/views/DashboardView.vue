<template>
  <AppLayout>
    <div class="space-y-6">
      <!-- Welcome banner -->
      <div class="bg-indigo-600 rounded-xl p-6 text-white flex justify-between items-center shadow-sm">
        <div>
          <h1 class="text-2xl font-bold mb-1">Welcome back, {{ auth.fullName || auth.user?.username }}!</h1>
          <p class="text-indigo-200">Here's what's happening with your projects today.</p>
        </div>
        <router-link
          to="/projects"
          class="bg-white text-indigo-600 px-4 py-2 rounded-lg font-medium hover:bg-indigo-50 transition text-sm"
        >
          View All Projects
        </router-link>
      </div>

      <!-- Stats row -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
          <div class="bg-blue-100 p-3 rounded-lg text-blue-600"><Folder class="w-5 h-5"/></div>
          <div>
            <p class="text-xs text-gray-500 font-medium">Projects</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.projects }}</p>
          </div>
        </div>
        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
          <div class="bg-green-100 p-3 rounded-lg text-green-600"><CheckSquare class="w-5 h-5"/></div>
          <div>
            <p class="text-xs text-gray-500 font-medium">My Tasks</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.tasks }}</p>
          </div>
        </div>
        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
          <div class="bg-purple-100 p-3 rounded-lg text-purple-600"><FileText class="w-5 h-5"/></div>
          <div>
            <p class="text-xs text-gray-500 font-medium">Papers</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.papers }}</p>
          </div>
        </div>
        <div class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
          <div class="bg-yellow-100 p-3 rounded-lg text-yellow-600"><Users class="w-5 h-5"/></div>
          <div>
            <p class="text-xs text-gray-500 font-medium">Collaborators</p>
            <p class="text-2xl font-bold text-gray-900">{{ stats.collaborators }}</p>
          </div>
        </div>
      </div>

      <!-- Main content -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- Recent Projects -->
        <div class="lg:col-span-2 space-y-3">
          <div class="flex justify-between items-center">
            <h2 class="text-lg font-bold text-gray-800">Recent Projects</h2>
            <router-link to="/projects" class="text-sm text-indigo-600 hover:underline">See all →</router-link>
          </div>

          <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div v-for="i in 4" :key="i" class="bg-white p-5 rounded-xl border border-gray-100 animate-pulse h-28"/>
          </div>

          <div v-else-if="projects.length" class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <router-link
              v-for="proj in projects"
              :key="proj.id"
              :to="`/projects/${proj.id}`"
              class="block bg-white p-5 rounded-xl shadow-sm border border-gray-100 hover:shadow-md hover:border-indigo-200 transition"
            >
              <div class="flex justify-between items-start mb-2">
                <h3 class="font-bold text-gray-900 leading-tight">{{ proj.title }}</h3>
                <span :class="statusBadge(proj.status)" class="text-xs px-2 py-0.5 rounded-full font-medium ml-2 shrink-0">
                  {{ proj.status }}
                </span>
              </div>
              <p class="text-sm text-gray-500 line-clamp-2 mb-3">{{ proj.description || 'No description.' }}</p>
              <p class="text-xs text-gray-400">{{ proj.field }} · Updated {{ relativeTime(proj.updated_at || proj.created_at) }}</p>
            </router-link>
          </div>

          <div v-else class="bg-white rounded-xl border border-dashed border-gray-300 p-10 text-center">
            <Folder class="w-10 h-10 text-gray-300 mx-auto mb-3"/>
            <p class="text-gray-500 mb-3">No projects yet.</p>
            <router-link to="/projects" class="text-indigo-600 font-medium text-sm hover:underline">
              Create your first project →
            </router-link>
          </div>
        </div>

        <!-- Upcoming deadlines / quick actions -->
        <div class="space-y-4">
          <h2 class="text-lg font-bold text-gray-800">Quick Actions</h2>
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 divide-y divide-gray-100">
            <router-link to="/projects" class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition text-sm font-medium text-gray-700">
              <Folder class="w-4 h-4 text-indigo-500"/> New Project
            </router-link>
            <router-link to="/notifications" class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition text-sm font-medium text-gray-700">
              <Bell class="w-4 h-4 text-indigo-500"/>
              Notifications
              <span v-if="unreadCount" class="ml-auto bg-red-500 text-white text-xs px-1.5 py-0.5 rounded-full">{{ unreadCount }}</span>
            </router-link>
            <router-link to="/profile" class="flex items-center gap-3 px-4 py-3 hover:bg-gray-50 transition text-sm font-medium text-gray-700">
              <User class="w-4 h-4 text-indigo-500"/> My Profile
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useProjectsStore } from '@/stores/projects'
import { useNotificationsStore } from '@/stores/notifications'
import AppLayout from '@/components/layout/AppLayout.vue'
import { Folder, CheckSquare, FileText, Users, Bell, User } from 'lucide-vue-next'

const auth = useAuthStore()
const projectsStore = useProjectsStore()
const notificationsStore = useNotificationsStore()

const loading = ref(true)
const projects = ref([])
const stats = ref({ projects: 0, tasks: 0, papers: 0, collaborators: 0 })
const unreadCount = computed(() => notificationsStore.unreadCount)

const statusBadge = (status) => ({
  'ACTIVE':    'bg-green-100 text-green-700',
  'COMPLETED': 'bg-blue-100 text-blue-700',
  'ARCHIVED':  'bg-gray-100 text-gray-600',
}[status] || 'bg-gray-100 text-gray-600')

const relativeTime = (dateStr) => {
  if (!dateStr) return ''
  const diff = Date.now() - new Date(dateStr).getTime()
  const days = Math.floor(diff / 86400000)
  if (days === 0) return 'today'
  if (days === 1) return 'yesterday'
  if (days < 30) return `${days}d ago`
  return new Date(dateStr).toLocaleDateString()
}

onMounted(async () => {
  try {
    await projectsStore.fetchProjects()
    projects.value = projectsStore.projects.slice(0, 6)
    stats.value.projects = projectsStore.projects.length
    // Sum up tasks/papers across all projects (from stats if available)
    projectsStore.projects.forEach(p => {
      stats.value.tasks += p.stats?.task_count || 0
      stats.value.papers += p.stats?.paper_count || 0
    })
  } catch (e) {
    console.error('Dashboard load error:', e)
  } finally {
    loading.value = false
  }
})
</script>
