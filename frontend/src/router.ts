import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from './stores/auth'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    auth?: boolean
    adminOnly?: boolean
  }
}

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'directory', component: () => import('./pages/DirectoryPage.vue') },
    {
      path: '/admin/login',
      name: 'login',
      component: () => import('./pages/LoginPage.vue'),
      meta: { title: 'Kirish' },
    },
    {
      path: '/admin',
      component: () => import('./layouts/AdminLayout.vue'),
      meta: { auth: true },
      children: [
        { path: '', redirect: { name: 'employees' } },
        {
          path: 'employees',
          name: 'employees',
          component: () => import('./pages/admin/EmployeesPage.vue'),
          meta: { title: 'Hodimlar' },
        },
        {
          path: 'departments',
          name: 'departments',
          component: () => import('./pages/admin/DepartmentsPage.vue'),
          meta: { title: "Bo'limlar" },
        },
        {
          path: 'users',
          name: 'users',
          component: () => import('./pages/admin/UsersPage.vue'),
          meta: { title: 'Foydalanuvchilar', adminOnly: true },
        },
        {
          path: 'log',
          name: 'log',
          component: () => import('./pages/admin/LogPage.vue'),
          meta: { title: "O'zgarishlar jurnali" },
        },
        {
          path: 'password',
          name: 'password',
          component: () => import('./pages/admin/PasswordPage.vue'),
          meta: { title: 'Parolni almashtirish' },
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach(async (to) => {
  if (!to.matched.some((r) => r.meta.auth) && to.name !== 'login') return true
  const auth = useAuthStore()
  if (!auth.checked) await auth.fetchMe()
  if (to.name === 'login') return auth.user ? { name: 'employees' } : true
  if (!auth.user) return { name: 'login', query: { next: to.fullPath } }
  if (to.meta.adminOnly && !auth.user.is_admin) return { name: 'employees' }
  return true
})

router.afterEach((to) => {
  const base = "Telefon ma'lumotnomasi"
  document.title = to.meta.title ? `${to.meta.title} — ${base}` : base
})
