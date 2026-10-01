import { defineStore } from 'pinia'
import { tasksAPI } from '@/api'

export const useTasksStore = defineStore('tasks', {
  state: () => ({
    tasks: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetchTasks(projectId, params = {}) {
      this.loading = true
      this.error = null
      try {
        // Backend returns { message, data: [...] }
        const res = await tasksAPI.list(projectId, params)
        this.tasks = res.data.data || []
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to load tasks'
      } finally {
        this.loading = false
      }
    },

    async createTask(projectId, payload) {
      const res = await tasksAPI.create(projectId, payload)
      const task = res.data.data
      this.tasks.push(task)
      return task
    },

    async updateTask(taskId, payload) {
      // Backend: PUT /tasks/<id> (not nested under project)
      const res = await tasksAPI.update(taskId, payload)
      const updated = res.data.data
      const idx = this.tasks.findIndex(t => t.id === +taskId)
      if (idx !== -1) this.tasks[idx] = updated
      return updated
    },

    async deleteTask(taskId) {
      await tasksAPI.delete(taskId)
      this.tasks = this.tasks.filter(t => t.id !== +taskId)
    },
  },
})
