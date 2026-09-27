<template>
  <div class="flex h-screen bg-gray-50 overflow-hidden">
    <AppSidebar />
    <div class="flex-1 flex flex-col overflow-hidden">
      <AppNavbar />
      <main class="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-6">
        <!-- SLOT — renders whatever the parent view puts inside <AppLayout> -->
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup>
import AppSidebar from './AppSidebar.vue'
import AppNavbar from './AppNavbar.vue'
</script>
