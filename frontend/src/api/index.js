import api from './axios'

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
  me: () => api.get('/auth/me'),
  updateMe: (data) => api.put('/auth/me', data),
}

export const projectsAPI = {
  create: (data) => api.post('/projects/', data),
  list: () => api.get('/projects/'),
  get: (id) => api.get(`/projects/${id}`),
  update: (id, data) => api.put(`/projects/${id}`, data),
  delete: (id) => api.delete(`/projects/${id}`),
}

export const membersAPI = {
  list: (projectId) => api.get(`/projects/${projectId}/members`),
  add: (projectId, data) => api.post(`/projects/${projectId}/members`, data),
  updateRole: (projectId, userId, data) => api.put(`/projects/${projectId}/members/${userId}`, data),
  remove: (projectId, userId) => api.delete(`/projects/${projectId}/members/${userId}`),
}

export const tasksAPI = {
  // Backend routes: POST/GET /projects/<id>/tasks | GET/PUT/DELETE /tasks/<id>
  list: (projectId, params = {}) => api.get(`/projects/${projectId}/tasks`, { params }),
  create: (projectId, data) => api.post(`/projects/${projectId}/tasks`, data),
  get: (taskId) => api.get(`/tasks/${taskId}`),
  update: (taskId, data) => api.put(`/tasks/${taskId}`, data),
  delete: (taskId) => api.delete(`/tasks/${taskId}`),
  // Comments on tasks
  getComments: (taskId) => api.get(`/tasks/${taskId}/comments`),
  addComment: (taskId, data) => api.post(`/tasks/${taskId}/comments`, data),
  deleteComment: (commentId) => api.delete(`/comments/${commentId}`),
}

export const papersAPI = {
  // Backend routes: POST/GET /projects/<id>/papers | GET/PUT/DELETE /papers/<id>
  list: (projectId) => api.get(`/projects/${projectId}/papers`),
  get: (paperId) => api.get(`/papers/${paperId}`),
  create: (projectId, data) => api.post(`/projects/${projectId}/papers`, data),
  update: (paperId, data) => api.put(`/papers/${paperId}`, data),
  delete: (paperId) => api.delete(`/papers/${paperId}`),
  // Comments on papers
  getComments: (paperId) => api.get(`/papers/${paperId}/comments`),
  addComment: (paperId, data) => api.post(`/papers/${paperId}/comments`, data),
}

export const versionsAPI = {
  // Backend routes: POST/GET /papers/<id>/versions | GET /versions/<id>
  list: (paperId) => api.get(`/papers/${paperId}/versions`),
  create: (paperId, data) => api.post(`/papers/${paperId}/versions`, data),
  get: (versionId) => api.get(`/versions/${versionId}`),
}

export const milestonesAPI = {
  list: (projectId) => api.get(`/projects/${projectId}/milestones`),
  create: (projectId, data) => api.post(`/projects/${projectId}/milestones`, data),
  update: (milestoneId, data) => api.put(`/milestones/${milestoneId}`, data),
  delete: (milestoneId) => api.delete(`/milestones/${milestoneId}`),
}

export const referencesAPI = {
  list: (projectId) => api.get(`/projects/${projectId}/references`),
  create: (projectId, data) => api.post(`/projects/${projectId}/references`, data),
  update: (refId, data) => api.put(`/references/${refId}`, data),
  delete: (refId) => api.delete(`/references/${refId}`),
}

export const notificationsAPI = {
  list: (params = {}) => api.get('/notifications/', { params }),
  unreadCount: () => api.get('/notifications/unread-count'),
  markRead: (id) => api.put(`/notifications/${id}/read`),
  markAllRead: () => api.put('/notifications/read-all'),
}

export const reportsAPI = {
  generate: (projectId) => api.post(`/projects/${projectId}/report/`),
  status: (projectId, taskId) => api.get(`/projects/${projectId}/report/status/${taskId}`),
  download: (projectId, taskId) => api.get(`/projects/${projectId}/report/download/${taskId}`, { responseType: 'blob' }),
}

export const adminAPI = {
  stats: () => api.get('/admin/stats'),
  users: () => api.get('/admin/users'),
  updateUser: (id, data) => api.put(`/admin/users/${id}`, data),
  deleteUser: (id) => api.delete(`/admin/users/${id}`),
}
