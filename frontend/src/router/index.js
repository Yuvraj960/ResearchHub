import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', name: 'Landing', component: () => import('@/views/LandingView.vue') },
  { path: '/login', name: 'Login', component: () => import('@/views/LoginView.vue'), meta: { guest: true } },
  { path: '/register', name: 'Register', component: () => import('@/views/RegisterView.vue'), meta: { guest: true } },
  { path: '/dashboard', name: 'Dashboard', component: () => import('@/views/DashboardView.vue'), meta: { requiresAuth: true } },
  { path: '/projects', name: 'Projects', component: () => import('@/views/ProjectsView.vue'), meta: { requiresAuth: true } },
  { path: '/projects/:id', name: 'ProjectDetail', component: () => import('@/views/ProjectDetailView.vue'), meta: { requiresAuth: true } },
  { path: '/projects/:id/tasks', name: 'Tasks', component: () => import('@/views/TasksView.vue'), meta: { requiresAuth: true } },
  { path: '/projects/:id/papers', name: 'Papers', component: () => import('@/views/PapersView.vue'), meta: { requiresAuth: true } },
  { path: '/projects/:id/papers/:paperId', name: 'PaperDetail', component: () => import('@/views/PaperDetailView.vue'), meta: { requiresAuth: true } },
  { path: '/projects/:id/members', name: 'Members', component: () => import('@/views/MembersView.vue'), meta: { requiresAuth: true } },
  { path: '/projects/:id/milestones', name: 'Milestones', component: () => import('@/views/MilestonesView.vue'), meta: { requiresAuth: true } },
  { path: '/projects/:id/references', name: 'References', component: () => import('@/views/ReferencesView.vue'), meta: { requiresAuth: true } },
  { path: '/notifications', name: 'Notifications', component: () => import('@/views/NotificationsView.vue'), meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: () => import('@/views/ProfileView.vue'), meta: { requiresAuth: true } },
  { path: '/admin', name: 'Admin', component: () => import('@/views/AdminView.vue'), meta: { requiresAuth: true, adminOnly: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    next('/login')
  } else if (to.meta.guest && auth.isLoggedIn) {
    next('/dashboard')
  } else if (to.meta.adminOnly && !auth.isAdmin) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
