<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { api, errorMessage, fieldErrors } from '@/api'
import FormField from '@/components/FormField.vue'
import { useToastStore } from '@/stores/toast'

const MIN_PASSWORD = 8
const toast = useToastStore()
const router = useRouter()
const form = reactive({ current: '', password: '', password2: '' })
const errors = ref<Record<string, string>>({})
const busy = ref(false)

async function save() {
  errors.value = {}
  if (form.password !== form.password2) {
    errors.value = { password2: 'Parollar mos kelmadi.' }
    return
  }
  busy.value = true
  try {
    await api.post('/auth/password', { current: form.current, password: form.password })
    toast.ok('Parolingiz almashtirildi.')
    router.push({ name: 'employees' })
  } catch (e) {
    errors.value = fieldErrors(e)
    if (!Object.keys(errors.value).length) toast.error(errorMessage(e))
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-md">
    <h1 class="mb-5 text-2xl font-semibold text-slate-900">Parolni almashtirish</h1>
    <form class="card space-y-4 p-6" @submit.prevent="save">
      <FormField label="Joriy parol" for="p-current" :error="errors.current">
        <input id="p-current" v-model="form.current" type="password" class="input" :class="{ 'input-error': errors.current }" autocomplete="current-password" required />
      </FormField>
      <FormField label="Yangi parol" for="p-new" :error="errors.password" :hint="`Kamida ${MIN_PASSWORD} belgi`">
        <input id="p-new" v-model="form.password" type="password" class="input" :class="{ 'input-error': errors.password }" autocomplete="new-password" required />
      </FormField>
      <FormField label="Yangi parolni takrorlang" for="p-new2" :error="errors.password2">
        <input id="p-new2" v-model="form.password2" type="password" class="input" :class="{ 'input-error': errors.password2 }" autocomplete="new-password" required />
      </FormField>
      <button type="submit" class="btn-primary w-full" :disabled="busy">Saqlash</button>
    </form>
  </div>
</template>
