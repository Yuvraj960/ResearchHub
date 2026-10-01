<template>
  <AppLayout>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Members</h1>
      <button @click="showModal = true" class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 flex items-center gap-2 text-sm font-medium">
        <UserPlus class="w-4 h-4"/> Add Member
      </button>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div v-if="loading" class="p-6 text-gray-500">Loading members...</div>
      <table v-else class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-gray-50 border-b border-gray-100">
            <th class="py-3 px-4 font-semibold text-gray-600">User</th>
            <th class="py-3 px-4 font-semibold text-gray-600">Role</th>
            <th class="py-3 px-4 font-semibold text-gray-600">Joined</th>
            <th class="py-3 px-4 font-semibold text-gray-600 text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="member in members" :key="member.id" class="border-b border-gray-50 hover:bg-gray-50/50">
            <td class="py-3 px-4">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">
                  {{ memberInitials(member) }}
                </div>
                <div>
                  <p class="font-medium text-gray-900">{{ memberDisplayName(member) }}</p>
                  <p class="text-xs text-gray-500">{{ member.user?.email }}</p>
                </div>
              </div>
            </td>
            <td class="py-3 px-4">
              <span class="px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-700">{{ member.role }}</span>
            </td>
            <td class="py-3 px-4 text-sm text-gray-500">
              {{ new Date(member.created_at).toLocaleDateString() }}
            </td>
            <td class="py-3 px-4 text-right">
              <button @click="handleRemove(member.user_id)" class="text-red-500 hover:text-red-700 p-1" title="Remove Member">
                <Trash2 class="w-4 h-4"/>
              </button>
            </td>
          </tr>
          <tr v-if="!members.length">
            <td colspan="4" class="py-6 text-center text-gray-500">No members found.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <BaseModal :show="showModal" title="Add Member" @close="showModal = false">
      <form @submit.prevent="handleAdd">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Member Email</label>
            <input v-model="form.user_email" type="email" required placeholder="colleague@university.edu" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Role</label>
            <select v-model="form.role" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <option value="RESEARCHER">Researcher</option>
              <option value="OWNER">Owner</option>
            </select>
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button type="button" @click="showModal = false" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50">Cancel</button>
          <button type="submit" :disabled="submitting" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50">Add Member</button>
        </div>
      </form>
    </BaseModal>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { membersAPI } from '@/api'
import { useToast } from '@/composables/useToast'
import AppLayout from '@/components/layout/AppLayout.vue'
import BaseModal from '@/components/common/BaseModal.vue'
import { UserPlus, Trash2 } from 'lucide-vue-next'

const route = useRoute()
const { showToast } = useToast()
const projectId = computed(() => route.params.id)

const loading = ref(true)
const members = ref([])
const showModal = ref(false)
const submitting = ref(false)
const form = ref({ user_email: '', role: 'RESEARCHER' })

const memberInitials = (m) => {
  const u = m.user
  if (!u) return 'U'
  if (u.first_name && u.last_name) return (u.first_name[0] + u.last_name[0]).toUpperCase()
  if (u.username) return u.username.substring(0, 2).toUpperCase()
  return 'U'
}
const memberDisplayName = (m) => {
  const u = m.user
  if (!u) return 'Unknown'
  const full = `${u.first_name || ''} ${u.last_name || ''}`.trim()
  return full || u.username || u.email
}

const fetchMembers = async () => {
  loading.value = true
  try {
    const res = await membersAPI.list(projectId.value)
    members.value = res.data.data || []
  } catch (e) {
    showToast('Failed to load members', 'error')
  } finally {
    loading.value = false
  }
}

onMounted(fetchMembers)

const handleAdd = async () => {
  submitting.value = true
  try {
    await membersAPI.add(projectId.value, { user_email: form.value.user_email, role: form.value.role })
    showToast('Member added', 'success')
    showModal.value = false
    form.value = { user_email: '', role: 'RESEARCHER' }
    fetchMembers()
  } catch (e) {
    showToast(e.response?.data?.error || 'Failed to add member', 'error')
  } finally {
    submitting.value = false
  }
}

const handleRemove = async (userId) => {
  if (!confirm('Remove this member?')) return
  try {
    await membersAPI.remove(projectId.value, userId)
    showToast('Member removed', 'success')
    fetchMembers()
  } catch (e) {
    showToast('Failed to remove member', 'error')
  }
}
</script>
