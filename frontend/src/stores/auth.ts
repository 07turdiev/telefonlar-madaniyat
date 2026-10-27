import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/api'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const checked = ref(false)

  async function fetchMe() {
    try {
      user.value = (await api.get<User>('/auth/me')).data
    } catch {
      user.value = null
    }
    checked.value = true
  }

  async function login(username: string, password: string) {
    user.value = (await api.post<User>('/auth/login', { username, password })).data
    checked.value = true
  }

  async function logout() {
    await api.post('/auth/logout')
    user.value = null
  }

  return { user, checked, fetchMe, login, logout }
})
