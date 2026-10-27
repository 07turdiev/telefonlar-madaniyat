import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { router } from './router'
import { api } from './api'
import { useAuthStore } from './stores/auth'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)

// Sessiya tugagan bo'lsa (8 soat), admin sahifasidan login sahifasiga qaytaramiz.
api.interceptors.response.use(undefined, (error) => {
  const url: string = error.config?.url ?? ''
  if (error.response?.status === 401 && url.startsWith('/admin')) {
    useAuthStore().user = null
    const current = router.currentRoute.value
    router.replace({ name: 'login', query: { next: current.fullPath } })
  }
  return Promise.reject(error)
})

app.mount('#app')
