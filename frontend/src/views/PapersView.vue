<template>
  <AppLayout>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Papers</h1>
      <button @click="showModal = true" class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 flex items-center gap-2 text-sm font-medium">
        <Plus class="w-4 h-4"/> New Paper
      </button>
    </div>

    <div v-if="papersStore.loading" class="text-gray-500">Loading papers...</div>
    <div v-else-if="!papersStore.papers.length" class="text-center py-10 bg-white rounded-xl border border-gray-100">
      <p class="text-gray-500">No papers yet.</p>
    </div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <router-link v-for="paper in papersStore.papers" :key="paper.id" :to="`/projects/${projectId}/papers/${paper.id}`" class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 hover:shadow-md transition">
        <div class="flex justify-between items-start mb-3">
          <h3 class="font-bold text-lg text-gray-900">{{ paper.title }}</h3>
          <span class="px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">{{ paper.status }}</span>
        </div>
        <p class="text-gray-600 text-sm mb-4 line-clamp-3">{{ paper.abstract }}</p>
        <div class="text-xs text-gray-400">Last updated: {{ new Date(paper.updated_at).toLocaleDateString() }}</div>
      </router-link>
    </div>

    <BaseModal :show="showModal" title="Create Paper" @close="showModal = false">
      <form @submit.prevent="handleCreate">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input v-model="form.title" required class="w-full px-3 py-2 border border-gray-300 rounded-md" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Abstract</label>
            <textarea v-model="form.abstract" rows="4" class="w-full px-3 py-2 border border-gray-300 rounded-md"></textarea>
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button type="button" @click="showModal = false" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md">Cancel</button>
          <button type="submit" :disabled="creating" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md">Create</button>
        </div>
      </form>
    </BaseModal>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { usePapersStore } from '@/stores/papers'
import { papersAPI } from '@/api'
import { useToast } from '@/composables/useToast'
import AppLayout from '@/components/layout/AppLayout.vue'
import BaseModal from '@/components/common/BaseModal.vue'
import { Plus } from 'lucide-vue-next'

const route = useRoute()
const papersStore = usePapersStore()
const { showToast } = useToast()

const projectId = computed(() => route.params.id)
const showModal = ref(false)
const creating = ref(false)
const form = ref({ title: '', abstract: '' })

onMounted(async () => {
  await papersStore.fetchPapers(projectId.value)
})

const handleCreate = async () => {
  creating.value = true
  try {
    const res = await papersAPI.create(projectId.value, form.value)
    papersStore.papers.unshift(res.data.data)
    showModal.value = false
    showToast('Paper created successfully', 'success')
    form.value = { title: '', abstract: '' }
  } catch (e) {
    showToast(e.response?.data?.error || 'Error creating paper', 'error')
  } finally {
    creating.value = false
  }
}
</script>
