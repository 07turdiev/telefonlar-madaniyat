<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { errorMessage } from '@/api'
import AppIcon from '@/components/AppIcon.vue'
import FormField from '@/components/FormField.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')
const busy = ref(false)

async function submit() {
  busy.value = true
  error.value = ''
  try {
    await auth.login(username.value, password.value)
    const next = String(route.query.next ?? '')
    router.replace(next.startsWith('/admin') ? next : { name: 'employees' })
  } catch (e) {
    error.value = errorMessage(e)
    password.value = ''
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-brand-800 to-brand-900 px-4 py-10">
    <div class="w-full max-w-sm">
      <div class="mb-6 text-center text-white">
        <div class="mx-auto mb-3 grid h-14 w-14 place-items-center rounded-2xl bg-white/10">
          <AppIcon name="phone" class="h-7 w-7" />
        </div>
        <h1 class="text-xl font-semibold">Telefon ma'lumotnomasi</h1>
        <p class="text-sm text-brand-100">kirish</p>
      </div>

      <form class="card space-y-4 p-6" @submit.prevent="submit">
        <div v-if="error" class="flex items-start gap-2 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">
          <AppIcon name="alert" class="mt-0.5 h-4 w-4 shrink-0" />
          {{ error }}
        </div>
        <FormField label="Login" for="username">
          <input id="username" v-model="username" class="input" autocomplete="username" autofocus required />
        </FormField>
        <FormField label="Parol" for="password">
          <input id="password" v-model="password" type="password" class="input" autocomplete="current-password" required />
        </FormField>
        <button type="submit" class="btn-primary w-full" :disabled="busy">
          {{ busy ? 'Tekshirilmoqda…' : 'Kirish' }}
        </button>
      </form>

      <p class="mt-6 text-center text-sm">
        <RouterLink to="/" class="text-brand-100 hover:text-white hover:underline">← Ma'lumotnomaga qaytish</RouterLink>
      </p>
    </div>
  </div>
</template>
