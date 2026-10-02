<template>
  <AppLayout>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">References</h1>
      <button @click="showModal = true" class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 flex items-center gap-2 text-sm font-medium">
        <Plus class="w-4 h-4"/> Add Reference
      </button>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div v-if="loading" class="p-6 text-gray-500">Loading references...</div>
      <table v-else class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-gray-50 border-b border-gray-100 text-sm">
            <th class="py-3 px-4 font-semibold text-gray-600">Title</th>
            <th class="py-3 px-4 font-semibold text-gray-600">Authors</th>
            <th class="py-3 px-4 font-semibold text-gray-600">Year</th>
            <th class="py-3 px-4 font-semibold text-gray-600">URL / DOI</th>
            <th class="py-3 px-4 font-semibold text-gray-600 text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ref in references" :key="ref.id" class="border-b border-gray-50 hover:bg-gray-50/50">
            <td class="py-3 px-4 font-medium text-gray-900">{{ ref.title }}</td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ ref.authors }}</td>
            <td class="py-3 px-4 text-sm text-gray-600">{{ ref.year }}</td>
            <td class="py-3 px-4 text-sm">
              <a v-if="ref.url_or_doi" :href="ref.url_or_doi" target="_blank" class="text-indigo-600 hover:underline">Link</a>
            </td>
            <td class="py-3 px-4 text-right">
              <button @click="handleDelete(ref.id)" class="text-red-500 hover:text-red-700 p-1"><Trash2 class="w-4 h-4"/></button>
            </td>
          </tr>
          <tr v-if="!references.length">
            <td colspan="5" class="py-6 text-center text-gray-500">No references added.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <BaseModal :show="showModal" title="Add Reference" @close="showModal = false">
      <form @submit.prevent="handleCreate">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input v-model="form.title" required class="w-full px-3 py-2 border border-gray-300 rounded-md" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Authors</label>
            <input v-model="form.authors" class="w-full px-3 py-2 border border-gray-300 rounded-md" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Year</label>
              <input v-model.number="form.year" type="number" class="w-full px-3 py-2 border border-gray-300 rounded-md" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">URL / DOI</label>
              <input v-model="form.url_or_doi" class="w-full px-3 py-2 border border-gray-300 rounded-md" />
            </div>
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button type="button" @click="showModal = false" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md">Cancel</button>
          <button type="submit" :disabled="submitting" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md">Add</button>
        </div>
      </form>
    </BaseModal>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { referencesAPI } from '@/api'
import { useToast } from '@/composables/useToast'
import AppLayout from '@/components/layout/AppLayout.vue'
import BaseModal from '@/components/common/BaseModal.vue'
import { Plus, Trash2 } from 'lucide-vue-next'

const route = useRoute()
const { showToast } = useToast()
const projectId = computed(() => route.params.id)

const loading = ref(true)
const references = ref([])
const showModal = ref(false)
const submitting = ref(false)
const form = ref({ title: '', authors: '', year: new Date().getFullYear(), url_or_doi: '' })

const fetchReferences = async () => {
  loading.value = true
  try {
    const res = await referencesAPI.list(projectId.value)
    references.value = res.data.data || []
  } catch (e) {
    showToast('Failed to load references', 'error')
  } finally {
    loading.value = false
  }
}

onMounted(fetchReferences)

const handleCreate = async () => {
  submitting.value = true
  try {
    await referencesAPI.create(projectId.value, form.value)
    showToast('Reference added', 'success')
    showModal.value = false
    form.value = { title: '', authors: '', year: new Date().getFullYear(), url_or_doi: '' }
    fetchReferences()
  } catch (e) {
    showToast('Failed to add reference', 'error')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (id) => {
  if (!confirm('Delete reference?')) return
  try {
    await referencesAPI.delete(id)
    references.value = references.value.filter(r => r.id !== id)
    showToast('Deleted', 'success')
  } catch (e) {
    showToast('Failed to delete', 'error')
  }
}
</script>
