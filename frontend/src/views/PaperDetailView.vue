<template>
  <AppLayout>
    <div v-if="loading" class="text-gray-500">Loading paper...</div>
    <div v-else-if="paper" class="max-w-4xl mx-auto space-y-6">
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex justify-between items-start mb-4">
          <h1 class="text-2xl font-bold text-gray-900">{{ paper.title }}</h1>
          <span class="px-3 py-1 text-sm font-semibold rounded-full bg-blue-100 text-blue-800">{{ paper.status }}</span>
        </div>
        <h3 class="text-sm font-medium text-gray-700 mb-2">Abstract</h3>
        <p class="text-gray-600 mb-4 whitespace-pre-wrap">{{ paper.abstract }}</p>
      </div>

      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-lg font-bold text-gray-900">Version History</h2>
          <button @click="showModal = true" class="bg-indigo-50 text-indigo-700 px-4 py-2 rounded-lg hover:bg-indigo-100 flex items-center gap-2 text-sm font-medium">
            <Plus class="w-4 h-4"/> Add Version
          </button>
        </div>

        <div v-if="versions.length === 0" class="text-gray-500 text-sm">No versions yet.</div>
        <div class="space-y-6">
          <div v-for="ver in versions" :key="ver.id" class="border-l-2 border-indigo-200 pl-4 py-1 relative">
            <div class="absolute w-3 h-3 bg-indigo-600 rounded-full -left-[7px] top-2"></div>
            <div class="flex justify-between items-start">
              <div>
                <h4 class="font-bold text-gray-900">Version {{ ver.version_number }}</h4>
                <p class="text-sm text-gray-500 mb-2">{{ ver.change_summary }}</p>
                <div class="bg-gray-50 p-3 rounded text-sm text-gray-700 font-mono whitespace-pre-wrap">{{ decodeBase64(ver.content) }}</div>
              </div>
              <span class="text-xs text-gray-400">{{ new Date(ver.created_at).toLocaleString() }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <BaseModal :show="showModal" title="Add New Version" @close="showModal = false">
      <form @submit.prevent="handleAddVersion">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Change Summary</label>
            <input v-model="form.change_summary" required class="w-full px-3 py-2 border border-gray-300 rounded-md" placeholder="Brief description of changes" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Content</label>
            <textarea v-model="form.content" required rows="6" class="w-full px-3 py-2 border border-gray-300 rounded-md font-mono" placeholder="Draft text..."></textarea>
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button type="button" @click="showModal = false" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md">Cancel</button>
          <button type="submit" :disabled="submitting" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md">Save Version</button>
        </div>
      </form>
    </BaseModal>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { papersAPI, versionsAPI } from '@/api'
import { useToast } from '@/composables/useToast'
import AppLayout from '@/components/layout/AppLayout.vue'
import BaseModal from '@/components/common/BaseModal.vue'
import { Plus } from 'lucide-vue-next'

const route = useRoute()
const { showToast } = useToast()

const projectId = computed(() => route.params.id)
const paperId = computed(() => route.params.paperId)

const loading = ref(true)
const paper = ref(null)
const versions = ref([])
const showModal = ref(false)
const submitting = ref(false)
const form = ref({ change_summary: '', content: '' })

onMounted(async () => {
  try {
    const [pRes, vRes] = await Promise.all([
      papersAPI.get(projectId.value, paperId.value),
      versionsAPI.list(projectId.value, paperId.value)
    ])
    paper.value = pRes.data
    versions.value = vRes.data
  } catch (e) {
    showToast('Failed to load paper details', 'error')
  } finally {
    loading.value = false
  }
})

const decodeBase64 = (str) => {
  try {
    return atob(str)
  } catch (e) {
    return str
  }
}

const handleAddVersion = async () => {
  submitting.value = true
  try {
    const payload = {
      change_summary: form.value.change_summary,
      content: btoa(form.value.content) // encode to base64
    }
    const { data } = await versionsAPI.create(projectId.value, paperId.value, payload)
    versions.value.unshift(data)
    showModal.value = false
    form.value = { change_summary: '', content: '' }
    showToast('Version added', 'success')
  } catch (e) {
    showToast('Failed to add version', 'error')
  } finally {
    submitting.value = false
  }
}
</script>
