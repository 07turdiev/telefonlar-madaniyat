<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api, errorMessage } from '@/api'
import SearchInput from '@/components/SearchInput.vue'
import { useToastStore } from '@/stores/toast'
import type { LogEntry } from '@/types'
import { formatDateTime } from '@/utils/format'
import { normalize, queryTokens } from '@/utils/search'

const toast = useToastStore()
const entries = ref<LogEntry[]>([])
const loading = ref(true)
const query = ref('')

const visible = computed(() => {
  const tokens = queryTokens(query.value)
  if (!tokens.length) return entries.value
  return entries.value.filter((e) => {
    const text = normalize(`${e.username} ${e.action} ${e.details}`)
    return tokens.every((t) => text.includes(t))
  })
})

onMounted(async () => {
  try {
    entries.value = (await api.get<LogEntry[]>('/admin/log')).data
  } catch (e) {
    toast.error(errorMessage(e))
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div class="mb-5">
      <h1 class="text-2xl font-semibold text-slate-900">O'zgarishlar jurnali</h1>
      <p class="text-sm text-slate-500">Kim, qachon va nimani o'zgartirgani. Oxirgi 500 ta yozuv.</p>
    </div>
    <SearchInput v-model="query" class="mb-4" placeholder="Foydalanuvchi, hodim yoki bo'lim nomi" />

    <div v-if="loading" class="h-40 animate-pulse rounded-xl bg-slate-200/70" />
    <p v-else-if="!visible.length" class="card p-8 text-center text-slate-500">Yozuv yo'q.</p>
    <div v-else class="card overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-slate-50 text-left text-xs uppercase tracking-wide text-slate-500">
          <tr>
            <th class="px-4 py-2.5 font-medium">Vaqt</th>
            <th class="px-4 py-2.5 font-medium">Kim</th>
            <th class="px-4 py-2.5 font-medium">Amal</th>
            <th class="px-4 py-2.5 font-medium">Tafsilot</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-100">
          <tr v-for="e in visible" :key="e.id" class="align-top">
            <td class="whitespace-nowrap px-4 py-2.5 tabular-nums text-slate-500">{{ formatDateTime(e.at) }}</td>
            <td class="whitespace-nowrap px-4 py-2.5 font-medium text-slate-800">{{ e.username }}</td>
            <td class="whitespace-nowrap px-4 py-2.5">{{ e.action }}</td>
            <td class="min-w-[16rem] px-4 py-2.5 text-slate-600">{{ e.details }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
