import { defineStore } from 'pinia'
import { projectsAPI } from '@/api'

export const useProjectsStore = defineStore('projects', {
  state: () => ({
    projects: [],
    currentProject: null,
    loading: false,
    error: null,
  }),

  actions: {
    async fetchProjects() {
      this.loading = true
      this.error = null
      try {
        // Backend returns { message, data: [...] }
        const res = await projectsAPI.list()
        this.projects = res.data.data || []
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to load projects'
      } finally {
        this.loading = false
      }
    },

    async fetchProject(id) {
      this.loading = true
      this.error = null
      try {
        const res = await projectsAPI.get(id)
        this.currentProject = res.data.data
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to load project'
      } finally {
        this.loading = false
      }
    },

    async createProject(payload) {
      const res = await projectsAPI.create(payload)
      const project = res.data.data
      this.projects.push(project)
      return project
    },

    async updateProject(id, payload) {
      const res = await projectsAPI.update(id, payload)
      const updated = res.data.data
      const idx = this.projects.findIndex(p => p.id === updated.id)
      if (idx !== -1) this.projects[idx] = updated
      if (this.currentProject?.id === updated.id) this.currentProject = updated
      return updated
    },

    async deleteProject(id) {
      await projectsAPI.delete(id)
      this.projects = this.projects.filter(p => p.id !== id)
      if (this.currentProject?.id === id) this.currentProject = null
    },
  },
})
