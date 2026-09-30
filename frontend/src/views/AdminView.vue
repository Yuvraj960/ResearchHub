<template>
  <AppLayout>
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500 font-medium">Total Users</p>
        <p class="text-2xl font-bold text-gray-900">{{ stats.users }}</p>
      </div>
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500 font-medium">Total Projects</p>
        <p class="text-2xl font-bold text-gray-900">{{ stats.projects }}</p>
      </div>
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500 font-medium">Total Tasks</p>
        <p class="text-2xl font-bold text-gray-900">{{ stats.tasks }}</p>
      </div>
      <div class="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
        <p class="text-sm text-gray-500 font-medium">Total Papers</p>
        <p class="text-2xl font-bold text-gray-900">{{ stats.papers }}</p>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-100 bg-gray-50">
        <h2 class="font-bold text-gray-800">User Management</h2>
      </div>
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-white border-b border-gray-100">
            <th class="py-3 px-6 font-semibold text-gray-600 text-sm">User</th>
            <th class="py-3 px-6 font-semibold text-gray-600 text-sm">Roles</th>
            <th class="py-3 px-6 font-semibold text-gray-600 text-sm">Status</th>
            <th class="py-3 px-6 font-semibold text-gray-600 text-sm text-right">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id" class="border-b border-gray-50 hover:bg-gray-50/50">
            <td class="py-3 px-6">
              <p class="font-medium text-gray-900">{{ user.name }}</p>
              <p class="text-xs text-gray-500">{{ user.email }}</p>
            </td>
            <td class="py-3 px-6 text-sm">
              <span class="px-2 py-1 bg-indigo-100 text-indigo-700 rounded text-xs font-medium">{{ user.roles }}</span>
            </td>
            <td class="py-3 px-6">
              <span :class="['px-2 py-1 rounded text-xs font-medium', user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700']">
                {{ user.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td class="py-3 px-6 text-right">
              <button @click="toggleActive(user)" class="text-sm font-medium px-3 py-1 border rounded" :class="user.is_active ? 'border-red-200 text-red-600 hover:bg-red-50' : 'border-green-200 text-green-600 hover:bg-green-50'">
                {{ user.is_active ? 'Deactivate' : 'Activate' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/api'
import { useToast } from '@/composables/useToast'
import AppLayout from '@/components/layout/AppLayout.vue'

const { showToast } = useToast()
const stats = ref({ users: 0, projects: 0, tasks: 0, papers: 0 })
const users = ref([])

const loadData = async () => {
  try {
    const [st, us] = await Promise.all([adminAPI.stats(), adminAPI.users()])
    stats.value = st.data
    users.value = us.data
  } catch (e) {
    showToast('Failed to load admin data', 'error')
  }
}

onMounted(loadData)

const toggleActive = async (user) => {
  try {
    await adminAPI.updateUser(user.id, { is_active: !user.is_active })
    user.is_active = !user.is_active
    showToast(`User ${user.is_active ? 'activated' : 'deactivated'}`, 'success')
  } catch (e) {
    showToast('Update failed', 'error')
  }
}
</script>
