<script setup lang="ts">
import type { Employee } from '@/types'
import { OPTIONAL_COLUMNS, splitValues, type ColumnKey } from '@/utils/columns'
import { telHref } from '@/utils/format'

const props = withDefaults(defineProps<{ employees: Employee[]; columns?: readonly ColumnKey[] }>(), {
  columns: () => OPTIONAL_COLUMNS,
})
defineSlots<{ actions?(props: { employee: Employee; index: number; last: boolean }): unknown }>()

const show = (key: ColumnKey) => props.columns.includes(key)
// Keng ekranda va chop etishda jadval; telefon va planshetda kartochka, bo'sh maydon unda ko'rinmaydi.
const cell = (value: string) => ['emp-cell', !value && 'hidden lg:table-cell print:table-cell']
</script>

<template>
  <div class="card overflow-hidden print:overflow-visible print:rounded-none print:border-slate-400 print:shadow-none">
    <!-- table-fixed: hamma bo'lim jadvallarida ustunlar bir xil tekislanadi -->
    <table class="block w-full text-sm lg:table lg:table-fixed print:table print:table-fixed">
      <colgroup class="hidden lg:table-column-group print:table-column-group">
        <col />
        <col v-if="show('room')" class="w-20 print:w-12" />
        <col v-if="show('internal_phone')" class="w-20 print:w-12" />
        <col v-if="show('city_phone')" class="w-40 print:w-28" />
        <col v-if="show('mobile_phone')" class="w-36 print:w-28" />
        <col v-if="show('email')" class="w-52 print:w-36" />
        <col v-if="$slots.actions" class="w-36 print:hidden" />
      </colgroup>
      <thead class="hidden bg-slate-50 text-left text-xs font-medium uppercase tracking-wide text-slate-500 lg:table-header-group print:table-header-group print:bg-white print:text-slate-700">
        <tr>
          <th class="px-4 py-2.5 font-medium print:px-2 print:py-1">F.I.Sh. va lavozimi</th>
          <th v-if="show('room')" class="px-3 py-2.5 font-medium print:px-2 print:py-1">Xona</th>
          <th v-if="show('internal_phone')" class="px-3 py-2.5 font-medium print:px-2 print:py-1">Ichki</th>
          <th v-if="show('city_phone')" class="px-3 py-2.5 font-medium print:px-2 print:py-1">Shahar tel.</th>
          <th v-if="show('mobile_phone')" class="px-3 py-2.5 font-medium print:px-2 print:py-1">Mobil</th>
          <th v-if="show('email')" class="px-3 py-2.5 font-medium print:px-2 print:py-1">E-mail</th>
          <th v-if="$slots.actions" class="print:hidden"><span class="sr-only">Amallar</span></th>
        </tr>
      </thead>
      <tbody class="block divide-y divide-slate-100 lg:table-row-group print:table-row-group print:divide-slate-300">
        <tr
          v-for="(e, i) in employees"
          :id="`emp-${e.id}`"
          :key="e.id"
          class="block break-inside-avoid px-4 py-3 transition-colors hover:bg-brand-50/50 lg:table-row lg:p-0 print:table-row"
        >
          <td class="block pb-1 lg:table-cell lg:px-4 lg:py-2.5 print:table-cell print:px-2 print:py-1">
            <div class="font-medium text-slate-900">{{ e.full_name }}</div>
            <div v-if="e.position" class="text-[13px] leading-snug text-slate-500 print:text-slate-700">{{ e.position }}</div>
          </td>
          <td v-if="show('room')" :class="cell(e.room)">
            <span class="emp-label">Xona</span>
            <span class="tabular-nums">{{ e.room }}</span>
          </td>
          <td v-if="show('internal_phone')" :class="cell(e.internal_phone)">
            <span class="emp-label">Ichki</span>
            <span class="phone text-base font-semibold text-brand-700 print:text-[10pt] print:text-black">{{ e.internal_phone }}</span>
          </td>
          <td v-if="show('city_phone')" :class="cell(e.city_phone)">
            <span class="emp-label">Shahar</span>
            <span class="flex flex-col">
              <template v-for="n in splitValues(e.city_phone)" :key="n">
                <a v-if="telHref(n)" :href="telHref(n)!" class="phone hover:text-brand-700 hover:underline">{{ n }}</a>
                <span v-else class="phone">{{ n }}</span>
              </template>
            </span>
          </td>
          <td v-if="show('mobile_phone')" :class="cell(e.mobile_phone)">
            <span class="emp-label">Mobil</span>
            <span class="flex flex-col">
              <template v-for="n in splitValues(e.mobile_phone)" :key="n">
                <a v-if="telHref(n)" :href="telHref(n)!" class="phone hover:text-brand-700 hover:underline">{{ n }}</a>
                <span v-else class="phone">{{ n }}</span>
              </template>
            </span>
          </td>
          <td v-if="show('email')" :class="cell(e.email)">
            <span class="emp-label">E-mail</span>
            <a :href="`mailto:${e.email}`" class="break-all text-brand-700 hover:underline print:text-black">{{ e.email }}</a>
          </td>
          <td v-if="$slots.actions" class="flex justify-end gap-0.5 pt-2 lg:table-cell lg:whitespace-nowrap lg:px-2 lg:py-1.5 lg:text-right print:hidden">
            <slot name="actions" :employee="e" :index="i" :last="i === employees.length - 1" />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
