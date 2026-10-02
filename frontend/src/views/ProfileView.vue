<template>
  <AppLayout>
    <div class="max-w-2xl mx-auto space-y-6">
      <h1 class="text-2xl font-bold text-gray-900">My Profile</h1>

      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <!-- Avatar + info header -->
        <div class="flex items-center gap-6 mb-8">
          <div class="w-20 h-20 rounded-full bg-indigo-100 text-indigo-700 flex items-center justify-center text-3xl font-bold shrink-0">
            {{ initials }}
          </div>
          <div>
            <h2 class="text-xl font-bold text-gray-900">{{ auth.fullName || auth.user?.username }}</h2>
            <p class="text-gray-500 text-sm">{{ auth.user?.email }}</p>
            <div v-if="auth.user?.roles?.length" class="mt-2 flex gap-1 flex-wrap">
              <span
                v-for="role in auth.user.roles"
                :key="role"
                class="text-xs font-medium px-2 py-0.5 bg-indigo-100 text-indigo-700 rounded-full"
              >{{ role }}</span>
            </div>
          </div>
        </div>

        <!-- Success / Error messages -->
        <div v-if="successMsg" class="mb-4 bg-green-50 border border-green-200 text-green-700 rounded-lg px-4 py-3 text-sm">
          ✓ {{ successMsg }}
        </div>
        <div v-if="errorMsg" class="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">
          {{ errorMsg }}
        </div>

        <!-- Edit form -->
        <form @submit.prevent="handleUpdate" class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">First Name</label>
              <input
                v-model="form.first_name"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
              <input
                v-model="form.last_name"
                class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input
              v-model="form.username"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
            <input
              :value="auth.user?.email"
              disabled
              class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-50 text-gray-400 cursor-not-allowed"
            />
            <p class="text-xs text-gray-400 mt-1">Email cannot be changed.</p>
          </div>

          <div class="flex justify-end pt-2">
            <button
              type="submit"
              :disabled="saving"
              class="px-6 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 flex items-center gap-2 transition"
            >
              <svg v-if="saving" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
              </svg>
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppLayout from '@/components/layout/AppLayout.vue'

const auth = useAuthStore()

const saving = ref(false)
const successMsg = ref('')
const errorMsg = ref('')

const form = ref({ first_name: '', last_name: '', username: '' })

const initials = computed(() => {
  const u = auth.user
  if (!u) return 'U'
  if (u.first_name && u.last_name) return (u.first_name[0] + u.last_name[0]).toUpperCase()
  if (u.username) return u.username.substring(0, 2).toUpperCase()
  return 'U'
})

onMounted(() => {
  const u = auth.user
  if (u) {
    form.value.first_name = u.first_name || ''
    form.value.last_name = u.last_name || ''
    form.value.username = u.username || ''
  }
})

const handleUpdate = async () => {
  successMsg.value = ''
  errorMsg.value = ''
  saving.value = true
  try {
    await auth.updateProfile({
      first_name: form.value.first_name.trim(),
      last_name: form.value.last_name.trim(),
      username: form.value.username.trim(),
    })
    successMsg.value = 'Profile updated successfully.'
  } catch (e) {
    errorMsg.value = e.response?.data?.error || 'Failed to update profile.'
  } finally {
    saving.value = false
  }
}
</script>
