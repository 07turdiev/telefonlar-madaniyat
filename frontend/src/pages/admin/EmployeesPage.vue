<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { api, errorMessage } from '@/api'
import AppIcon from '@/components/AppIcon.vue'
import EmployeeTable from '@/components/EmployeeTable.vue'
import SearchInput from '@/components/SearchInput.vue'
import SectionHeading from '@/components/SectionHeading.vue'
import { useDirectoryFilter } from '@/composables/useDirectoryFilter'
import { useToastStore } from '@/stores/toast'
import type { Employee, Section } from '@/types'
import EmployeeDialog from './EmployeeDialog.vue'

const toast = useToastStore()
const sections = ref<Section[]>([])
const loading = ref(true)
const query = ref('')
const departmentId = ref<number | null>(null)
const { filtered, count, total, active, parentNameFor } = useDirectoryFilter(sections, query, departmentId, true)

// Dialog: undefined — yopiq, null — yangi hodim, Employee — tahrirlash.
const editing = ref<Employee | null | undefined>(undefined)
const presetDepartment = ref<number | null>(null)
const searching = computed(() => query.value.trim() !== '')

async function load() {
  try {
    sections.value = (await api.get<{ sections: Section[] }>('/admin/directory')).data.sections
  } catch (e) {
    toast.error(errorMessage(e))
  } finally {
    loading.value = false
  }
}

function openNew(deptId: number | null = departmentId.value) {
  presetDepartment.value = deptId
  editing.value = null
}

async function moveEmployee(employee: Employee, direction: 'up' | 'down') {
  try {
    await api.post(`/admin/employees/${employee.id}/move`, { direction })
    await load()
  } catch (e) {
    toast.error(errorMessage(e))
  }
}

async function remove(employee: Employee) {
  if (!confirm(`${employee.full_name} ro'yxatdan o'chirilsinmi?`)) return
  try {
    await api.delete(`/admin/employees/${employee.id}`)
    toast.ok(`${employee.full_name} o'chirildi.`)
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
        <h1 class="text-2xl font-semibold text-slate-900">Hodimlar</h1>
        <p class="text-sm text-slate-500">
          {{ active ? `Topildi: ${count} / ${total}` : `Jami ${total} ta hodim, ${sections.length} ta bo'lim` }}
        </p>
      </div>
      <a href="/api/admin/export.xlsx" class="btn-secondary" download>
        <AppIcon name="download" class="h-4 w-4" /> Excel
      </a>
      <button class="btn-primary" :disabled="!sections.length" @click="openNew()">
        <AppIcon name="plus" class="h-4 w-4" /> Hodim qo'shish
      </button>
    </div>

    <div class="mb-6 flex flex-col gap-2 sm:flex-row">
      <SearchInput v-model="query" class="flex-1" placeholder="Ism, lavozim, xona yoki raqam" />
      <select v-model="departmentId" class="input h-11 sm:w-80" aria-label="Bo'lim">
        <option :value="null">Barcha bo'limlar</option>
        <option v-for="s in sections" :key="s.id" :value="s.id">
          {{ s.level ? '    ' : '' }}{{ s.name }}
        </option>
      </select>
    </div>

    <div v-if="loading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="h-24 animate-pulse rounded-xl bg-slate-200/70" />
    </div>

    <div v-else-if="!sections.length" class="card mx-auto max-w-lg p-8 text-center">
      <AppIcon name="building" class="mx-auto mb-3 h-10 w-10 text-slate-300" />
      <p class="mb-1 font-medium text-slate-800">Hali bo'limlar yo'q</p>
      <p class="mb-5 text-sm text-slate-500">
        Avval vazirlik tuzilmasini kiriting: rahbariyat, boshqarmalar, bo'limlar. Keyin ularga hodimlarni qo'shasiz.
      </p>
      <RouterLink :to="{ name: 'departments' }" class="btn-primary">Bo'limlarni kiritish</RouterLink>
    </div>

    <p v-else-if="!filtered.length" class="card p-8 text-center text-slate-500">Hech kim topilmadi.</p>

    <template v-else>
      <p v-if="searching" class="mb-4 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800">
        Qidiruv paytida tartibni o'zgartirish o'chirilgan. Tartibni o'zgartirish uchun qidiruvni tozalang.
      </p>
      <section v-for="s in filtered" :key="s.id" :class="s.level === 0 ? 'pt-6 first:pt-0' : 'pt-3'">
        <SectionHeading :section="s" :parent-name="parentNameFor(s)" :count="s.employees.length">
          <button class="btn-secondary shrink-0 px-2.5 py-1.5 text-xs" @click="openNew(s.id)">
            <AppIcon name="plus" class="h-3.5 w-3.5" /> Qo'shish
          </button>
        </SectionHeading>
        <EmployeeTable v-if="s.employees.length" :employees="s.employees">
          <template #actions="{ employee, index, last }">
            <button class="icon-btn" title="Yuqoriga" :disabled="searching || index === 0" @click="moveEmployee(employee, 'up')">
              <AppIcon name="up" class="h-4 w-4" />
            </button>
            <button class="icon-btn" title="Pastga" :disabled="searching || last" @click="moveEmployee(employee, 'down')">
              <AppIcon name="down" class="h-4 w-4" />
            </button>
            <button class="icon-btn hover:text-brand-700" title="Tahrirlash" @click="editing = employee">
              <AppIcon name="edit" class="h-4 w-4" />
            </button>
            <button class="icon-btn hover:bg-red-50 hover:text-red-600" title="O'chirish" @click="remove(employee)">
              <AppIcon name="trash" class="h-4 w-4" />
            </button>
          </template>
        </EmployeeTable>
        <p v-else-if="s.level === 1 || !sections.some((c) => c.parent_id === s.id)" class="rounded-xl border border-dashed border-slate-300 px-4 py-3 text-sm text-slate-400">
          Bu bo'limda hali hodim yo'q.
        </p>
      </section>
    </template>

    <EmployeeDialog
      v-if="editing !== undefined"
      :employee="editing"
      :departments="sections"
      :department-id="presetDepartment"
      @saved="load"
      @close="editing = undefined"
    />
  </div>
</template>
