<template>
  <AppLayout>
    <!-- Loading -->
    <div v-if="loading" class="space-y-4">
      <div class="bg-white rounded-xl border border-gray-100 p-6 animate-pulse h-28"/>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div v-for="i in 4" :key="i" class="bg-white rounded-xl border border-gray-100 p-5 animate-pulse h-24"/>
      </div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 rounded-xl p-6 text-sm">
      {{ error }}
    </div>

    <!-- Project content -->
    <div v-else-if="project" class="space-y-6">
      <!-- Header -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex justify-between items-start">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2 flex-wrap">
              <h1 class="text-2xl font-bold text-gray-900">{{ project.title }}</h1>
              <span :class="statusClass(project.status)" class="text-xs px-2.5 py-1 rounded-full font-medium">
                {{ project.status }}
              </span>
            </div>
            <p class="text-gray-600 max-w-3xl">{{ project.description || 'No description.' }}</p>
            <p v-if="project.field" class="text-sm text-gray-400 mt-1">Field: {{ project.field }}</p>
          </div>
        </div>

        <!-- Stats bar -->
        <div v-if="project.stats" class="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-100">
          <div class="text-center">
            <p class="text-2xl font-bold text-gray-900">{{ project.stats.task_count || 0 }}</p>
            <p class="text-xs text-gray-500">Tasks</p>
          </div>
          <div class="text-center">
            <p class="text-2xl font-bold text-gray-900">{{ project.stats.paper_count || 0 }}</p>
            <p class="text-xs text-gray-500">Papers</p>
          </div>
          <div class="text-center">
            <p class="text-2xl font-bold text-gray-900">{{ project.stats.member_count || 0 }}</p>
            <p class="text-xs text-gray-500">Members</p>
          </div>
        </div>
      </div>

      <!-- Navigation cards -->
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <router-link
          v-for="item in navCards"
          :key="item.label"
          :to="`/projects/${project.id}/${item.path}`"
          class="bg-white p-5 rounded-xl shadow-sm border border-gray-100 hover:shadow-md hover:border-indigo-200 transition flex flex-col items-center gap-3 text-center"
        >
          <div :class="`${item.color} p-3 rounded-xl`">
            <component :is="item.icon" class="w-5 h-5"/>
          </div>
          <div>
            <p class="font-semibold text-gray-800 text-sm">{{ item.label }}</p>
            <p class="text-xs text-gray-400 mt-0.5">{{ item.desc }}</p>
          </div>
        </router-link>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'
import AppLayout from '@/components/layout/AppLayout.vue'
import { CheckSquare, FileText, Users, Flag, BookOpen } from 'lucide-vue-next'

const route = useRoute()
const projectsStore = useProjectsStore()

const loading = ref(true)
const error = ref('')
const project = computed(() => projectsStore.currentProject)

const navCards = [
  { path: 'tasks',      label: 'Tasks',       desc: 'Manage work items',     icon: CheckSquare, color: 'bg-blue-100 text-blue-600' },
  { path: 'papers',     label: 'Papers',      desc: 'Drafts & submissions',  icon: FileText,    color: 'bg-purple-100 text-purple-600' },
  { path: 'members',    label: 'Members',     desc: 'Team collaborators',    icon: Users,       color: 'bg-green-100 text-green-600' },
  { path: 'milestones', label: 'Milestones',  desc: 'Goals & deadlines',     icon: Flag,        color: 'bg-yellow-100 text-yellow-600' },
  { path: 'references', label: 'References',  desc: 'Bibliography',          icon: BookOpen,    color: 'bg-red-100 text-red-600' },
]

const statusClass = (status) => ({
  'ACTIVE':    'bg-green-100 text-green-700',
  'COMPLETED': 'bg-blue-100 text-blue-700',
  'ARCHIVED':  'bg-gray-100 text-gray-500',
}[status] || 'bg-green-100 text-green-700')

onMounted(async () => {
  try {
    await projectsStore.fetchProject(route.params.id)
  } catch (e) {
    error.value = e.response?.data?.error || 'Failed to load project.'
  } finally {
    loading.value = false
  }
})
</script>
