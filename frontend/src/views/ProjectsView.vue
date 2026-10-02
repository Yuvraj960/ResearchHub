<template>
  <AppLayout>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">My Projects</h1>
      <button
        @click="showModal = true"
        class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 flex items-center gap-2 text-sm font-medium transition"
      >
        <Plus class="w-4 h-4"/> New Project
      </button>
    </div>

    <!-- Loading skeleton -->
    <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="i in 6" :key="i" class="bg-white rounded-xl border border-gray-100 p-5 animate-pulse h-40"/>
    </div>

    <!-- Empty state -->
    <div v-else-if="!projectsStore.projects.length" class="text-center py-20 bg-white rounded-xl shadow-sm border border-gray-100">
      <Folder class="w-12 h-12 text-gray-300 mx-auto mb-4" />
      <h3 class="text-lg font-medium text-gray-900 mb-1">No projects yet</h3>
      <p class="text-gray-500 mb-4">Get started by creating your first research project.</p>
      <button @click="showModal = true" class="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-700 transition">
        Create Project
      </button>
    </div>

    <!-- Project grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <router-link
        v-for="proj in projectsStore.projects"
        :key="proj.id"
        :to="`/projects/${proj.id}`"
        class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md hover:border-indigo-200 transition flex flex-col"
      >
        <div class="flex justify-between items-start mb-2">
          <h3 class="font-bold text-gray-900 leading-tight">{{ proj.title }}</h3>
          <span :class="statusClass(proj.status)" class="text-xs px-2 py-0.5 rounded-full font-medium shrink-0 ml-2">
            {{ proj.status }}
          </span>
        </div>
        <p class="text-gray-500 text-sm mb-4 flex-1 line-clamp-3">{{ proj.description || 'No description.' }}</p>
        <div class="flex justify-between items-center text-xs text-gray-400 pt-3 border-t border-gray-100">
          <span class="font-medium text-gray-500">{{ proj.field || 'General' }}</span>
          <span>{{ new Date(proj.created_at).toLocaleDateString() }}</span>
        </div>
      </router-link>
    </div>

    <!-- Create Project Modal -->
    <BaseModal :show="showModal" title="Create New Project" @close="closeModal">
      <form @submit.prevent="handleCreate" class="space-y-4">
        <div v-if="createError" class="bg-red-50 border border-red-200 text-red-700 rounded-lg px-3 py-2 text-sm">
          {{ createError }}
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Project Title <span class="text-red-500">*</span></label>
          <input
            v-model="form.title"
            required
            placeholder="e.g. Climate Change Impact Study"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Research Field</label>
          <input
            v-model="form.field"
            placeholder="e.g. Computer Science, Biology, Physics"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
          <textarea
            v-model="form.description"
            rows="3"
            placeholder="What is this research project about?"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
          />
        </div>

        <div class="flex justify-end gap-3 pt-2">
          <button
            type="button"
            @click="closeModal"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="creating"
            class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-2"
          >
            <svg v-if="creating" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
            </svg>
            {{ creating ? 'Creating...' : 'Create Project' }}
          </button>
        </div>
      </form>
    </BaseModal>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProjectsStore } from '@/stores/projects'
import AppLayout from '@/components/layout/AppLayout.vue'
import BaseModal from '@/components/common/BaseModal.vue'
import { Plus, Folder } from 'lucide-vue-next'

const projectsStore = useProjectsStore()
const router = useRouter()

const loading = ref(true)
const showModal = ref(false)
const creating = ref(false)
const createError = ref('')
const form = ref({ title: '', field: '', description: '' })

const statusClass = (status) => ({
  'ACTIVE':    'bg-green-100 text-green-700',
  'COMPLETED': 'bg-blue-100 text-blue-700',
  'ARCHIVED':  'bg-gray-100 text-gray-500',
}[status] || 'bg-green-100 text-green-700')

const closeModal = () => {
  showModal.value = false
  createError.value = ''
  form.value = { title: '', field: '', description: '' }
}

onMounted(async () => {
  try {
    await projectsStore.fetchProjects()
  } finally {
    loading.value = false
  }
})

const handleCreate = async () => {
  createError.value = ''
  creating.value = true
  try {
    const newProject = await projectsStore.createProject({
      title: form.value.title.trim(),
      field: form.value.field.trim(),
      description: form.value.description.trim(),
    })
    closeModal()
    router.push(`/projects/${newProject.id}`)
  } catch (e) {
    createError.value = e.response?.data?.error || 'Failed to create project. Try again.'
  } finally {
    creating.value = false
  }
}
</script>
