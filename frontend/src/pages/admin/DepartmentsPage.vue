<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api, errorMessage } from '@/api'
import AppIcon from '@/components/AppIcon.vue'
import { useToastStore } from '@/stores/toast'
import type { DepartmentWithCount } from '@/types'
import DepartmentDialog from './DepartmentDialog.vue'

const toast = useToastStore()
const departments = ref<DepartmentWithCount[]>([])
const loading = ref(true)
// undefined — yopiq, null — yangi bo'lim, obyekt — tahrirlash.
const editing = ref<DepartmentWithCount | null | undefined>(undefined)
const presetParent = ref<number | null>(null)

async function load() {
  try {
    departments.value = (await api.get<DepartmentWithCount[]>('/admin/departments')).data
  } catch (e) {
    toast.error(errorMessage(e))
  } finally {
    loading.value = false
  }
}

function siblings(d: DepartmentWithCount) {
  return departments.value.filter((x) => x.parent_id === d.parent_id)
}

function openNew(parentId: number | null = null) {
  presetParent.value = parentId
  editing.value = null
}

async function moveDepartment(d: DepartmentWithCount, direction: 'up' | 'down') {
  try {
    await api.post(`/admin/departments/${d.id}/move`, { direction })
    await load()
  } catch (e) {
    toast.error(errorMessage(e))
  }
}

async function remove(d: DepartmentWithCount) {
  if (!confirm(`«${d.name}» o'chirilsinmi?`)) return
  try {
    await api.delete(`/admin/departments/${d.id}`)
    toast.ok(`«${d.name}» o'chirildi.`)
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
        <h1 class="text-2xl font-semibold text-slate-900">Bo'limlar</h1>
        <p class="text-sm text-slate-500">
          Ma'lumotnomada bo'limlar shu tartibda chiqadi. Ichida hodimi yo'q bo'lim saytda ko'rinmaydi.
        </p>
      </div>
      <button class="btn-primary" @click="openNew()">
        <AppIcon name="plus" class="h-4 w-4" /> Bo'lim qo'shish
      </button>
    </div>

    <div v-if="loading" class="h-40 animate-pulse rounded-xl bg-slate-200/70" />

    <div v-else-if="!departments.length" class="card mx-auto max-w-lg p-8 text-center">
      <AppIcon name="building" class="mx-auto mb-3 h-10 w-10 text-slate-300" />
      <p class="mb-1 font-medium text-slate-800">Hali bo'lim yo'q</p>
      <p class="mb-5 text-sm text-slate-500">
        Birinchi bo'lib, masalan, «Vazirlik rahbariyati»ni qo'shing. Bo'limlarni keyin tepaga yoki pastga surish mumkin.
      </p>
      <button class="btn-primary" @click="openNew()">Bo'lim qo'shish</button>
    </div>

    <ul v-else class="card divide-y divide-slate-100">
      <li
        v-for="d in departments"
        :id="`dept-${d.id}`"
        :key="d.id"
        class="flex flex-wrap items-center gap-x-3 gap-y-1 px-4 py-2.5 hover:bg-slate-50"
        :class="d.level === 1 ? 'pl-10 sm:pl-12' : ''"
      >
        <span v-if="d.level === 1" class="-ml-5 text-slate-300">└</span>
        <span class="min-w-0 flex-1" :class="d.level === 0 ? 'font-semibold text-slate-900' : 'text-slate-700'">
          {{ d.name }}
        </span>
        <span class="rounded-full px-2 py-0.5 text-xs" :class="d.count ? 'bg-brand-50 text-brand-700' : 'bg-slate-100 text-slate-400'">
          {{ d.count }} hodim
        </span>
        <div class="flex items-center gap-0.5">
          <button v-if="d.level === 0" class="icon-btn" title="Ichki bo'lim qo'shish" @click="openNew(d.id)">
            <AppIcon name="plus" class="h-4 w-4" />
          </button>
          <span v-else class="h-8 w-8" aria-hidden="true" />
          <button class="icon-btn" title="Yuqoriga" :disabled="siblings(d)[0]?.id === d.id" @click="moveDepartment(d, 'up')">
            <AppIcon name="up" class="h-4 w-4" />
          </button>
          <button class="icon-btn" title="Pastga" :disabled="siblings(d).at(-1)?.id === d.id" @click="moveDepartment(d, 'down')">
            <AppIcon name="down" class="h-4 w-4" />
          </button>
          <button class="icon-btn hover:text-brand-700" title="Tahrirlash" @click="editing = d">
            <AppIcon name="edit" class="h-4 w-4" />
          </button>
          <button class="icon-btn hover:bg-red-50 hover:text-red-600" title="O'chirish" @click="remove(d)">
            <AppIcon name="trash" class="h-4 w-4" />
          </button>
        </div>
      </li>
    </ul>

    <DepartmentDialog
      v-if="editing !== undefined"
      :department="editing"
      :departments="departments"
      :parent-id="presetParent"
      @saved="load"
      @close="editing = undefined"
    />
  </div>
</template>
