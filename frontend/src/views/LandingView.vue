<template>
  <div class="min-h-screen bg-white">
    <nav class="container mx-auto px-6 py-4 flex justify-between items-center">
      <div class="text-2xl font-bold text-indigo-600 flex items-center gap-2">
        <Activity class="w-6 h-6" /> ResearchHub
      </div>
      <div class="space-x-4">
        <router-link to="/login" class="text-gray-600 hover:text-indigo-600 font-medium">Sign In</router-link>
        <router-link to="/register" class="bg-indigo-600 text-white px-5 py-2 rounded-lg hover:bg-indigo-700 font-medium transition">Get Started</router-link>
      </div>
    </nav>

    <main class="container mx-auto px-6 py-20 text-center">
      <h1 class="text-5xl md:text-6xl font-extrabold text-gray-900 tracking-tight mb-8">
        Collaborative Research Platform
      </h1>
      <p class="text-xl text-gray-600 max-w-2xl mx-auto mb-10">
        Manage projects, version papers, track tasks, and collaborate in real-time with your team in one unified platform.
      </p>
      <div class="flex justify-center gap-4">
        <router-link to="/register" class="bg-indigo-600 text-white px-8 py-3 rounded-lg text-lg font-medium hover:bg-indigo-700 transition">
          Start for free
        </router-link>
      </div>

      <div class="mt-20 grid md:grid-cols-3 gap-8 text-left">
        <div class="p-6 bg-indigo-50 rounded-xl">
          <FolderKanban class="w-10 h-10 text-indigo-600 mb-4" />
          <h3 class="text-xl font-bold text-gray-900 mb-2">Project Management</h3>
          <p class="text-gray-600">Organize your research, track milestones, and manage team members efficiently.</p>
        </div>
        <div class="p-6 bg-indigo-50 rounded-xl">
          <FileText class="w-10 h-10 text-indigo-600 mb-4" />
          <h3 class="text-xl font-bold text-gray-900 mb-2">Paper Versioning</h3>
          <p class="text-gray-600">Keep track of drafts, collaborate on edits, and manage submission status easily.</p>
        </div>
        <div class="p-6 bg-indigo-50 rounded-xl">
          <Users class="w-10 h-10 text-indigo-600 mb-4" />
          <h3 class="text-xl font-bold text-gray-900 mb-2">Real-time Collaboration</h3>
          <p class="text-gray-600">Get notified instantly about updates, comments, and task assignments.</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { Activity, FolderKanban, FileText, Users } from 'lucide-vue-next'
</script>
