<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, errorMessage } from '@/api'
import AppIcon from '@/components/AppIcon.vue'
import EmployeeTable from '@/components/EmployeeTable.vue'
import SearchInput from '@/components/SearchInput.vue'
import SectionHeading from '@/components/SectionHeading.vue'
import { useDirectoryFilter } from '@/composables/useDirectoryFilter'
import type { Directory } from '@/types'
import { usedColumns } from '@/utils/columns'
import { formatDateTime } from '@/utils/format'

const route = useRoute()
const router = useRouter()

const data = ref<Directory | null>(null)
const loading = ref(true)
const error = ref('')

// Qidiruv manzilda saqlanadi: ?q=...&b=<bo'lim id>, havolani boshqaga yuborish mumkin.
const query = ref(String(route.query.q ?? ''))
const departmentId = ref<number | null>(route.query.b ? Number(route.query.b) : null)
watch([query, departmentId], ([q, b]) => {
  router.replace({ query: { ...(q ? { q } : {}), ...(b ? { b: String(b) } : {}) } })
})

const sections = computed(() => data.value?.sections ?? [])
const { filtered, count, total, active, parentNameFor } = useDirectoryFilter(sections, query, departmentId)
const columns = computed(() => usedColumns(sections.value))

async function load() {
  loading.value = true
  error.value = ''
  try {
    data.value = (await api.get<Directory>('/directory')).data
    if (departmentId.value && !sections.value.some((s) => s.id === departmentId.value)) {
      departmentId.value = null
    }
  } catch (e) {
    error.value = errorMessage(e)
  } finally {
    loading.value = false
  }
}

function reset() {
  query.value = ''
  departmentId.value = null
}

const printPage = () => window.print()

onMounted(load)
</script>

<template>
  <div class="flex min-h-screen flex-col">
    <header class="bg-brand-800 text-white print:bg-white print:text-black">
      <div class="h-1 bg-gradient-to-r from-[#0099b5] via-white to-[#1eb53a] print:hidden" />
      <div class="mx-auto flex max-w-6xl items-center gap-4 px-4 py-5 print:px-0 print:py-0 print:pb-3">
        <div class="hidden h-12 w-12 shrink-0 place-items-center rounded-xl bg-white/10 sm:grid print:hidden">
          <AppIcon name="phone" class="h-6 w-6" />
        </div>
        <div class="min-w-0 flex-1">
          <p class="text-sm text-brand-100 print:text-[9pt] print:text-slate-600">
            {{ data?.org_name ?? "O'zbekiston Respublikasi Madaniyat vazirligi" }}
          </p>
          <h1 class="text-xl font-semibold tracking-tight sm:text-2xl print:text-[16pt]">
            {{ data?.site_title ?? "Telefon ma'lumotnomasi" }}
          </h1>
        </div>
        <button
          class="btn hidden border-white/25 bg-white/10 text-white hover:bg-white/20 sm:inline-flex print:hidden"
          :disabled="!data"
          @click="printPage"
        >
          <AppIcon name="printer" class="h-4 w-4" /> Chop etish
        </button>
        <p v-if="data?.updated" class="hidden text-[9pt] text-slate-600 print:block">
          {{ formatDateTime(data.updated).slice(0, 10) }} holatiga
        </p>
      </div>
    </header>

    <div class="sticky top-0 z-20 border-b border-slate-200 bg-white/95 shadow-sm backdrop-blur print:hidden">
      <div class="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-3 sm:flex-row sm:items-center">
        <SearchInput
          v-model="query"
          class="flex-1"
          placeholder="Ism, lavozim, bo'lim yoki raqam"
        />
        <select v-model="departmentId" class="input h-11 sm:w-80" aria-label="Bo'lim">
          <option :value="null">Barcha bo'limlar</option>
          <option v-for="s in sections" :key="s.id" :value="s.id">
            {{ s.level ? '    ' : '' }}{{ s.name }}
          </option>
        </select>
      </div>
    </div>

    <main class="mx-auto w-full max-w-6xl flex-1 px-4 py-6 print:px-0 print:py-0">
      <div v-if="loading" class="space-y-3" aria-busy="true">
        <div v-for="i in 4" :key="i" class="h-24 animate-pulse rounded-xl bg-slate-200/70" />
      </div>

      <div v-else-if="error" class="card mx-auto max-w-md p-6 text-center">
        <AppIcon name="alert" class="mx-auto mb-3 h-8 w-8 text-red-500" />
        <p class="mb-4 text-slate-700">{{ error }}</p>
        <button class="btn-secondary" @click="load">Qayta urinish</button>
      </div>

      <div v-else-if="!total" class="card mx-auto max-w-md p-8 text-center text-slate-500">
        Ma'lumotnoma hali to'ldirilmagan.
      </div>

      <template v-else>
        <p class="mb-4 text-sm text-slate-500 print:hidden">
          <template v-if="active">
            Topildi: <b class="text-slate-800">{{ count }}</b> ta hodim (jami {{ total }})
            <button v-if="count" class="ml-2 text-brand-700 hover:underline" @click="reset">Filtrni tozalash</button>
          </template>
          <template v-else>Jami {{ total }} ta hodim</template>
        </p>

        <div v-if="!count" class="card mx-auto max-w-md p-8 text-center">
          <AppIcon name="search" class="mx-auto mb-3 h-8 w-8 text-slate-300" />
          <p class="mb-1 font-medium text-slate-800">Hech kim topilmadi</p>
          <p class="mb-4 text-sm text-slate-500">So'zni boshqacha yozib yoki boshqa bo'limni tanlab ko'ring.</p>
          <button class="btn-secondary" @click="reset">Filtrni tozalash</button>
        </div>

        <section
          v-for="s in filtered"
          :key="s.id"
          :class="s.level === 0 ? 'pt-6 first:pt-0' : 'pt-3'"
          class="print:break-inside-auto"
        >
          <SectionHeading :section="s" :parent-name="parentNameFor(s)" />
          <EmployeeTable v-if="s.employees.length" :employees="s.employees" :columns="columns" />
        </section>
      </template>
    </main>

    <footer class="border-t border-slate-200 bg-white print:hidden">
      <div class="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-2 px-4 py-4 text-sm text-slate-500">
        <span v-if="data?.updated">Oxirgi yangilanish: {{ formatDateTime(data.updated) }}</span>
        <span v-else />
        <RouterLink to="/admin" class="hover:text-brand-700 hover:underline">Kirish</RouterLink>
      </div>
    </footer>
  </div>
</template>
