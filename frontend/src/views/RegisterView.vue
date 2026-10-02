<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
    <div class="max-w-md w-full bg-white p-8 rounded-2xl shadow-lg space-y-6">
      <!-- Header -->
      <div class="text-center">
        <h1 class="text-3xl font-extrabold text-gray-900">Create account</h1>
        <p class="mt-2 text-sm text-gray-600">
          Already have an account?
          <router-link to="/login" class="text-indigo-600 hover:text-indigo-500 font-medium">Sign in</router-link>
        </p>
      </div>

      <!-- Error banner -->
      <div v-if="errorMsg" class="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">
        {{ errorMsg }}
      </div>

      <form class="space-y-4" @submit.prevent="handleRegister">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">First Name</label>
            <input
              v-model="form.first_name"
              type="text"
              required
              placeholder="Alice"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
            <input
              v-model="form.last_name"
              type="text"
              placeholder="Smith"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Username</label>
          <input
            v-model="form.username"
            type="text"
            required
            placeholder="alice_researcher"
            autocomplete="username"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Email address</label>
          <input
            v-model="form.email"
            type="email"
            required
            placeholder="alice@university.edu"
            autocomplete="email"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Password</label>
          <input
            v-model="form.password"
            type="password"
            required
            minlength="6"
            placeholder="Min. 6 characters"
            autocomplete="new-password"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full flex justify-center py-2.5 px-4 rounded-lg text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-60 disabled:cursor-not-allowed transition"
        >
          <span v-if="loading" class="flex items-center gap-2">
            <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"/>
            </svg>
            Creating account...
          </span>
          <span v-else>Create account</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const loading = ref(false)
const errorMsg = ref('')

const form = ref({
  first_name: '',
  last_name: '',
  username: '',
  email: '',
  password: '',
})

const handleRegister = async () => {
  errorMsg.value = ''
  loading.value = true
  try {
    await auth.register({
      first_name: form.value.first_name.trim(),
      last_name: form.value.last_name.trim(),
      username: form.value.username.trim(),
      email: form.value.email.trim(),
      password: form.value.password,
    })
    // Auth store handles redirect to /dashboard on success
  } catch (err) {
    // Show the exact error message from the backend
    errorMsg.value = err.response?.data?.error || err.message || 'Registration failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
