<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
    <div class="max-w-md w-full bg-white p-8 rounded-2xl shadow-lg space-y-6">
      <!-- Header -->
      <div class="text-center">
        <h1 class="text-3xl font-extrabold text-gray-900">Sign in</h1>
        <p class="mt-2 text-sm text-gray-600">
          No account?
          <router-link to="/register" class="text-indigo-600 hover:text-indigo-500 font-medium">Create one</router-link>
        </p>
      </div>

      <!-- Success banner after registration -->
      <div v-if="justRegistered" class="bg-green-50 border border-green-200 text-green-700 rounded-lg px-4 py-3 text-sm">
        ✓ Account created successfully! Sign in to get started.
      </div>

      <!-- Error banner -->
      <div v-if="errorMsg" class="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">
        {{ errorMsg }}
      </div>

      <form class="space-y-4" @submit.prevent="handleLogin">
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
            placeholder="Your password"
            autocomplete="current-password"
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
            Signing in...
          </span>
          <span v-else>Sign in</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const auth = useAuthStore()
const loading = ref(false)
const errorMsg = ref('')

// Show success message when redirected from /register
const justRegistered = computed(() => route.query.registered === '1')

const form = ref({ email: '', password: '' })

const handleLogin = async () => {
  errorMsg.value = ''
  loading.value = true
  try {
    await auth.login(form.value)
    // Auth store handles redirect to /dashboard on success
  } catch (err) {
    errorMsg.value = err.response?.data?.error || err.message || 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
