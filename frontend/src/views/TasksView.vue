<template>
  <AppLayout>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900">Tasks</h1>
      <button @click="showModal = true" class="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 flex items-center gap-2 text-sm font-medium">
        <Plus class="w-4 h-4"/> Add Task
      </button>
    </div>

    <div v-if="loading" class="text-gray-500">Loading tasks...</div>

    <div v-else class="flex gap-6 overflow-x-auto pb-4 h-full">
      <div v-for="col in columns" :key="col.key" class="min-w-[280px] w-1/4 bg-gray-100 rounded-xl p-4 flex flex-col max-h-[calc(100vh-200px)]">
        <h3 class="font-bold text-gray-700 mb-3 flex justify-between items-center">
          <span :class="['w-2 h-2 rounded-full mr-2 inline-block', col.dot]"></span>
          {{ col.label }}
          <span class="bg-gray-200 text-gray-600 px-2 py-0.5 rounded text-xs">{{ tasksByStatus(col.key).length }}</span>
        </h3>

        <div
          class="flex-1 overflow-y-auto space-y-3 p-1 min-h-[100px]"
          @dragover.prevent
          @drop="onDrop($event, col.key)"
        >
          <div
            v-for="task in tasksByStatus(col.key)"
            :key="task.id"
            draggable="true"
            @dragstart="onDragStart($event, task)"
            @click="openEdit(task)"
            class="bg-white p-3 rounded-lg shadow-sm border border-gray-200 cursor-grab active:cursor-grabbing hover:border-indigo-300 transition"
          >
            <div class="flex justify-between items-start mb-2">
              <span :class="['text-xs font-semibold px-2 py-0.5 rounded', priorityClass(task.priority)]">
                {{ task.priority }}
              </span>
              <button @click.stop="deleteTask(task.id)" class="text-gray-400 hover:text-red-500">
                <X class="w-3 h-3"/>
              </button>
            </div>
            <h4 class="text-sm font-medium text-gray-900 mb-1">{{ task.title }}</h4>
            <p v-if="task.description" class="text-xs text-gray-500 truncate">{{ task.description }}</p>
            <div class="flex justify-between items-center mt-3 text-xs text-gray-500">
              <span v-if="task.deadline" class="flex items-center gap-1">
                <Calendar class="w-3 h-3"/>
                {{ new Date(task.deadline).toLocaleDateString() }}
              </span>
              <span v-else>No deadline</span>
            </div>
          </div>

          <div v-if="tasksByStatus(col.key).length === 0" class="text-center text-gray-400 text-sm py-8">
            Drop tasks here
          </div>
        </div>
      </div>
    </div>

    <!-- Task Modal -->
    <BaseModal :show="showModal" :title="editingTask ? 'Edit Task' : 'Add Task'" @close="closeModal">
      <form @submit.prevent="handleSubmit">
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Title *</label>
            <input v-model="form.title" required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea v-model="form.description" rows="2" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500"></textarea>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <select v-model="form.priority" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500">
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
                <option value="CRITICAL">Critical</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select v-model="form.status" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500">
                <option v-for="col in columns" :key="col.key" :value="col.key">{{ col.label }}</option>
              </select>
            </div>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Deadline</label>
            <input type="date" v-model="form.deadline" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-1 focus:ring-indigo-500" />
          </div>
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button type="button" @click="closeModal" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">Cancel</button>
          <button type="submit" :disabled="saving" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:opacity-50">
            {{ editingTask ? 'Save Changes' : 'Create Task' }}
          </button>
        </div>
      </form>
    </BaseModal>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useTasksStore } from '@/stores/tasks'
import { useToast } from '@/composables/useToast'
import AppLayout from '@/components/layout/AppLayout.vue'
import BaseModal from '@/components/common/BaseModal.vue'
import { Plus, Calendar, X } from 'lucide-vue-next'

const route = useRoute()
const tasksStore = useTasksStore()
const { showToast } = useToast()

const projectId = route.params.id
const loading = ref(true)
const showModal = ref(false)
const saving = ref(false)
const editingTask = ref(null)

// Backend enum values
const columns = [
  { key: 'TODO', label: 'To Do', dot: 'bg-gray-400' },
  { key: 'IN_PROGRESS', label: 'In Progress', dot: 'bg-blue-500' },
  { key: 'REVIEW', label: 'Review', dot: 'bg-yellow-500' },
  { key: 'COMPLETED', label: 'Completed', dot: 'bg-green-500' },
]

const emptyForm = () => ({ title: '', description: '', priority: 'MEDIUM', status: 'TODO', deadline: '' })
const form = ref(emptyForm())

onMounted(async () => {
  await tasksStore.fetchTasks(projectId)
  loading.value = false
})

const tasksByStatus = (status) => tasksStore.tasks.filter(t => t.status === status)

const priorityClass = (prio) => {
  if (prio === 'CRITICAL') return 'bg-purple-100 text-purple-800'
  if (prio === 'HIGH') return 'bg-red-100 text-red-800'
  if (prio === 'MEDIUM') return 'bg-yellow-100 text-yellow-800'
  return 'bg-green-100 text-green-800'
}

const openEdit = (task) => {
  editingTask.value = task
  form.value = {
    title: task.title,
    description: task.description || '',
    priority: task.priority,
    status: task.status,
    deadline: task.deadline ? task.deadline.slice(0, 10) : '',
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingTask.value = null
  form.value = emptyForm()
}

const handleSubmit = async () => {
  saving.value = true
  try {
    const payload = { ...form.value }
    if (!payload.deadline) delete payload.deadline

    if (editingTask.value) {
      await tasksStore.updateTask(editingTask.value.id, payload)
      showToast('Task updated', 'success')
    } else {
      await tasksStore.createTask(projectId, payload)
      showToast('Task created', 'success')
    }
    closeModal()
  } catch (e) {
    showToast(e.response?.data?.error || 'Failed to save task', 'error')
  } finally {
    saving.value = false
  }
}

const deleteTask = async (taskId) => {
  if (!confirm('Delete this task?')) return
  try {
    await tasksStore.deleteTask(taskId)
    showToast('Task deleted', 'success')
  } catch (e) {
    showToast('Failed to delete task', 'error')
  }
}

const onDragStart = (e, task) => {
  e.dataTransfer.setData('taskId', String(task.id))
}

const onDrop = async (e, newStatus) => {
  const taskId = e.dataTransfer.getData('taskId')
  const task = tasksStore.tasks.find(t => t.id === +taskId)
  if (task && task.status !== newStatus) {
    const oldStatus = task.status
    task.status = newStatus // optimistic update
    try {
      await tasksStore.updateTask(taskId, { status: newStatus })
    } catch (err) {
      task.status = oldStatus
      showToast('Failed to update task status', 'error')
    }
  }
}
</script>
