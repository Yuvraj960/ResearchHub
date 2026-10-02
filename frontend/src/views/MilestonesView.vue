<template>
  <AppLayout>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Milestones</h1>
      <button @click="showModal = true" class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 flex items-center gap-2 text-sm font-medium">
        <Plus class="w-4 h-4"/> Add Milestone
      </button>
    </div>

    <div v-if="loading" class="text-gray-500">Loading milestones...</div>
    <div v-else-if="!milestones.length" class="text-center py-10 bg-white rounded-xl border border-gray-100">
      <p class="text-gray-500">No milestones yet.</p>
    </div>
    
    <div v-else class="space-y-4">
      <div v-for="ms in milestones" :key="ms.id" class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 flex items-center justify-between">
        <div class="flex items-center gap-4">
          <button @click="toggleStatus(ms)" :class="['w-6 h-6 rounded-full border-2 flex items-center justify-center transition', ms.status === 'ACHIEVED' ? 'bg-green-500 border-green-500 text-white' : 'border-gray-300']">
            <Check class="w-4 h-4" v-if="ms.status === 'ACHIEVED'"/>
          </button>
          <div>
            <h3 class="font-bold text-gray-900" :class="{'line-through text-gray-400': ms.status === 'ACHIEVED'}">{{ ms.title }}</h3>
            <p class="text-sm text-gray-500">{{ ms.description }}</p>
          </div>
        </div>
        <div class="flex items-center gap-4">
          <span class="text-sm text-gray-500 flex items-center gap-1"><Calendar class="w-4 h-4"/> {{ new Date(ms.deadline).toLocaleDateString() }}</span>
          <button @click="handleDelete(ms.id)" class="text-red-500 hover:text-red-700 p-1"><Trash2 class="w-4 h-4"/></button>
        </div>
      </div>
    </div>

    <BaseModal :show="showModal" title="Add Milestone" @close="showModal = false">
      <form @submit.prevent="handleCreate">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Title</label>
            <input v-model="form.title" required class="w-full px-3 py-2 border border-gray-300 rounded-md" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="form.description" rows="3" class="w-full px-3 py-2 border border-gray-300 rounded-md"></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Deadline</label>
            <input v-model="form.deadline" type="date" required class="w-full px-3 py-2 border border-gray-300 rounded-md" />
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button type="button" @click="showModal = false" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md">Cancel</button>
          <button type="submit" :disabled="submitting" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md">Create</button>
        </div>
      </form>
    </BaseModal>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { milestonesAPI } from '@/api'
import { useToast } from '@/composables/useToast'
import AppLayout from '@/components/layout/AppLayout.vue'
import BaseModal from '@/components/common/BaseModal.vue'
import { Plus, Check, Calendar, Trash2 } from 'lucide-vue-next'

const route = useRoute()
const { showToast } = useToast()
const projectId = computed(() => route.params.id)

const loading = ref(true)
const milestones = ref([])
const showModal = ref(false)
const submitting = ref(false)
const form = ref({ title: '', description: '', deadline: '' })

const fetchMilestones = async () => {
  loading.value = true
  try {
    const res = await milestonesAPI.list(projectId.value)
    milestones.value = res.data.data || []
  } catch (e) {
    showToast('Failed to load milestones', 'error')
  } finally {
    loading.value = false
  }
}

onMounted(fetchMilestones)

const handleCreate = async () => {
  submitting.value = true
  try {
    const payload = { ...form.value, deadline: new Date(form.value.deadline).toISOString() }
    await milestonesAPI.create(projectId.value, payload)
    showToast('Milestone created', 'success')
    showModal.value = false
    form.value = { title: '', description: '', deadline: '' }
    fetchMilestones()
  } catch (e) {
    showToast('Failed to create milestone', 'error')
  } finally {
    submitting.value = false
  }
}

const toggleStatus = async (ms) => {
  const newStatus = ms.status === 'ACHIEVED' ? 'PENDING' : 'ACHIEVED'
  try {
    await milestonesAPI.update(ms.id, { status: newStatus })
    ms.status = newStatus
  } catch (e) {
    showToast('Failed to update status', 'error')
  }
}

const handleDelete = async (id) => {
  if (!confirm('Delete this milestone?')) return
  try {
    await milestonesAPI.delete(id)
    milestones.value = milestones.value.filter(m => m.id !== id)
    showToast('Milestone deleted', 'success')
  } catch (e) {
    showToast('Failed to delete', 'error')
  }
}
</script>
