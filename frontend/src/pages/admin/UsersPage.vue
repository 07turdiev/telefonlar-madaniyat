<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { api, errorMessage, fieldErrors } from '@/api'
import AppIcon from '@/components/AppIcon.vue'
import AppModal from '@/components/AppModal.vue'
import FormField from '@/components/FormField.vue'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import type { User } from '@/types'
import { formatDateTime } from '@/utils/format'

const MIN_PASSWORD = 8
const auth = useAuthStore()
const toast = useToastStore()
const users = ref<User[]>([])

// Yangi foydalanuvchi dialogi
const creating = ref(false)
const newUser = reactive({ username: '', full_name: '', password: '', password2: '', is_admin: false })
const createErrors = ref<Record<string, string>>({})

// Parolni tiklash dialogi
const resetting = ref<User | null>(null)
const reset = reactive({ password: '', password2: '' })
const resetError = ref('')

const busy = ref(false)

async function load() {
  try {
    users.value = (await api.get<User[]>('/admin/users')).data
  } catch (e) {
    toast.error(errorMessage(e))
  }
}

function openCreate() {
  Object.assign(newUser, { username: '', full_name: '', password: '', password2: '', is_admin: false })
  createErrors.value = {}
  creating.value = true
}

async function create() {
  createErrors.value = {}
  if (newUser.password !== newUser.password2) {
    createErrors.value = { password2: 'Parollar mos kelmadi.' }
    return
  }
  busy.value = true
  try {
    const { password2: _, ...payload } = newUser
    await api.post('/admin/users', payload)
    toast.ok(`«${newUser.username}» qo'shildi.`)
    creating.value = false
    await load()
  } catch (e) {
    createErrors.value = fieldErrors(e)
    if (!Object.keys(createErrors.value).length) toast.error(errorMessage(e))
  } finally {
    busy.value = false
  }
}

function openReset(user: User) {
  Object.assign(reset, { password: '', password2: '' })
  resetError.value = ''
  resetting.value = user
}

async function saveReset() {
  if (!resetting.value) return
  if (reset.password.length < MIN_PASSWORD) {
    resetError.value = `Parol kamida ${MIN_PASSWORD} belgidan iborat bo'lsin.`
    return
  }
  if (reset.password !== reset.password2) {
    resetError.value = 'Parollar mos kelmadi.'
    return
  }
  busy.value = true
  try {
    await api.post(`/admin/users/${resetting.value.id}/password`, { password: reset.password })
    toast.ok(`«${resetting.value.username}» paroli almashtirildi.`)
    resetting.value = null
  } catch (e) {
    resetError.value = fieldErrors(e).password ?? errorMessage(e)
  } finally {
    busy.value = false
  }
}

async function remove(user: User) {
  if (!confirm(`«${user.username}» foydalanuvchisi o'chirilsinmi?`)) return
  try {
    await api.delete(`/admin/users/${user.id}`)
    toast.ok(`«${user.username}» o'chirildi.`)
    await load()
  } catch (e) {
    toast.error(errorMessage(e))
  }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="mb-5 flex flex-wrap items-center gap-3">
      <div class="mr-auto">
        <h1 class="text-2xl font-semibold text-slate-900">Foydalanuvchilar</h1>
        <p class="text-sm text-slate-500">Ma'lumotnomani tahrirlay oladigan kadrlar bo'limi xodimlari.</p>
      </div>
      <button class="btn-primary" @click="openCreate">
        <AppIcon name="plus" class="h-4 w-4" /> Foydalanuvchi qo'shish
      </button>
    </div>

    <div class="card overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th class="px-4 py-2.5 font-medium">Login</th>
            <th class="px-4 py-2.5 font-medium">F.I.Sh.</th>
            <th class="px-4 py-2.5 font-medium">Huquq</th>
            <th class="px-4 py-2.5 font-medium">Qo'shilgan</th>
            <th class="px-4 py-2.5"><span class="sr-only">Amallar</span></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="u in users" :key="u.id">
            <td class="px-4 py-2.5 font-medium text-slate-900">
              {{ u.username }}
              <span v-if="u.id === auth.user?.id" class="ml-1 text-xs font-normal text-slate-400">(siz)</span>
            </td>
            <td class="px-4 py-2.5">{{ u.full_name }}</td>
            <td class="px-4 py-2.5">
              <span
                class="rounded-full px-2 py-0.5 text-xs"
                :class="u.is_admin ? 'bg-amber-50 text-amber-700' : 'bg-slate-100 text-slate-600'"
              >
                {{ u.is_admin ? 'Administrator' : 'Tahrirlovchi' }}
              </span>
            </td>
            <td class="whitespace-nowrap px-4 py-2.5 text-slate-500">{{ formatDateTime(u.created_at) }}</td>
            <td class="whitespace-nowrap px-2 py-1.5 text-right">
              <button class="icon-btn" title="Parolni almashtirish" @click="openReset(u)">
                <AppIcon name="key" class="h-4 w-4" />
              </button>
              <button
                class="icon-btn hover:bg-red-50 hover:text-red-600"
                title="O'chirish"
                :disabled="u.id === auth.user?.id"
                @click="remove(u)"
              >
                <AppIcon name="trash" class="h-4 w-4" />
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AppModal v-if="creating" title="Yangi foydalanuvchi" @close="creating = false">
      <form id="user-form" class="space-y-4" @submit.prevent="create">
        <FormField label="Login" for="u-login" required :error="createErrors.username" hint="Lotin harflari, raqamlar, nuqta yoki tire">
          <input id="u-login" v-model="newUser.username" class="input" :class="{ 'input-error': createErrors.username }" autocomplete="off" />
        </FormField>
        <FormField label="F.I.Sh." for="u-name">
          <input id="u-name" v-model="newUser.full_name" class="input" maxlength="200" />
        </FormField>
        <FormField label="Parol" for="u-pass" required :error="createErrors.password" :hint="`Kamida ${MIN_PASSWORD} belgi`">
          <input id="u-pass" v-model="newUser.password" type="password" class="input" :class="{ 'input-error': createErrors.password }" autocomplete="new-password" />
        </FormField>
        <FormField label="Parolni takrorlang" for="u-pass2" required :error="createErrors.password2">
          <input id="u-pass2" v-model="newUser.password2" type="password" class="input" :class="{ 'input-error': createErrors.password2 }" autocomplete="new-password" />
        </FormField>
        <label class="flex items-start gap-2 text-sm">
          <input v-model="newUser.is_admin" type="checkbox" class="mt-0.5 h-4 w-4 rounded border-slate-300 text-brand-700" />
          <span>
            <span class="font-medium text-slate-800">Administrator</span>
            <span class="block text-slate-500">Boshqa foydalanuvchilarni qo'sha va o'chira oladi.</span>
          </span>
        </label>
      </form>
      <template #footer>
        <button type="button" class="btn-secondary" @click="creating = false">Bekor qilish</button>
        <button type="submit" form="user-form" class="btn-primary" :disabled="busy">Qo'shish</button>
      </template>
    </AppModal>

    <AppModal v-if="resetting" :title="`Yangi parol: ${resetting.username}`" @close="resetting = null">
      <form id="reset-form" class="space-y-4" @submit.prevent="saveReset">
        <p v-if="resetError" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{{ resetError }}</p>
        <FormField label="Yangi parol" for="r-pass" :hint="`Kamida ${MIN_PASSWORD} belgi`">
          <input id="r-pass" v-model="reset.password" type="password" class="input" autocomplete="new-password" />
        </FormField>
        <FormField label="Parolni takrorlang" for="r-pass2">
          <input id="r-pass2" v-model="reset.password2" type="password" class="input" autocomplete="new-password" />
        </FormField>
      </form>
      <template #footer>
        <button type="button" class="btn-secondary" @click="resetting = null">Bekor qilish</button>
        <button type="submit" form="reset-form" class="btn-primary" :disabled="busy">Saqlash</button>
      </template>
    </AppModal>
  </div>
</template>
