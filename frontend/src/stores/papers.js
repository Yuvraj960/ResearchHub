import { defineStore } from 'pinia'
import { papersAPI, versionsAPI } from '@/api'

export const usePapersStore = defineStore('papers', {
  state: () => ({
    papers: [],
    currentPaper: null,
    versions: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetchPapers(projectId) {
      this.loading = true
      this.error = null
      try {
        // Backend returns { message, data: [...] }
        const res = await papersAPI.list(projectId)
        this.papers = res.data.data || []
      } catch (err) {
        this.error = err.response?.data?.error || 'Failed to load papers'
      } finally {
        this.loading = false
      }
    },

    async fetchPaper(paperId) {
      this.loading = true
      try {
        const res = await papersAPI.get(paperId)
        this.currentPaper = res.data.data
      } finally {
        this.loading = false
      }
    },

    async createPaper(projectId, payload) {
      const res = await papersAPI.create(projectId, payload)
      const paper = res.data.data
      this.papers.push(paper)
      return paper
    },

    async updatePaper(paperId, payload) {
      const res = await papersAPI.update(paperId, payload)
      const updated = res.data.data
      const idx = this.papers.findIndex(p => p.id === updated.id)
      if (idx !== -1) this.papers[idx] = updated
      if (this.currentPaper?.id === updated.id) this.currentPaper = updated
      return updated
    },

    async deletePaper(paperId) {
      await papersAPI.delete(paperId)
      this.papers = this.papers.filter(p => p.id !== paperId)
      if (this.currentPaper?.id === paperId) this.currentPaper = null
    },

    async fetchVersions(paperId) {
      const res = await versionsAPI.list(paperId)
      this.versions = res.data.data || []
    },

    async createVersion(paperId, payload) {
      const res = await versionsAPI.create(paperId, payload)
      const version = res.data.data
      this.versions.unshift(version) // newest first
      return version
    },
  },
})
