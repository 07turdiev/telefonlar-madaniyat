<script setup lang="ts">
import type { Employee } from '@/types'
import { telHref } from '@/utils/format'

defineProps<{ employees: Employee[] }>()
defineSlots<{ actions?(props: { employee: Employee; index: number; last: boolean }): unknown }>()

// Keng ekranda va chop etishda jadval; telefon va planshetda kartochka, bo'sh maydon unda ko'rinmaydi.
const cell = (value: string) => ['emp-cell', !value && 'hidden lg:table-cell print:table-cell']
</script>

<template>
  <div class="card overflow-hidden print:overflow-visible print:rounded-none print:border-slate-400 print:shadow-none">
    <!-- table-fixed: hamma bo'lim jadvallarida ustunlar bir xil tekislanadi -->
    <table class="block w-full text-sm lg:table lg:table-fixed print:table print:table-fixed">
      <colgroup class="hidden lg:table-column-group print:table-column-group">
        <col />
        <col class="w-20 print:w-12" />
        <col class="w-24 print:w-14" />
        <col class="w-36 print:w-[6.5rem]" />
        <col class="w-36 print:w-[6.5rem]" />
        <col class="w-52 print:w-36" />
        <col v-if="$slots.actions" class="w-36 print:hidden" />
      </colgroup>
      <thead class="hidden bg-slate-50 text-left text-xs font-medium uppercase tracking-wide text-slate-500 lg:table-header-group print:table-header-group print:bg-white print:text-slate-700">
        <tr>
          <th class="px-4 py-2.5 font-medium print:px-2 print:py-1">F.I.Sh. va lavozimi</th>
          <th class="px-3 py-2.5 font-medium print:px-2 print:py-1">Xona</th>
          <th class="px-3 py-2.5 font-medium print:px-2 print:py-1">Ichki</th>
          <th class="px-3 py-2.5 font-medium print:px-2 print:py-1">Shahar tel.</th>
          <th class="px-3 py-2.5 font-medium print:px-2 print:py-1">Mobil</th>
          <th class="px-3 py-2.5 font-medium print:px-2 print:py-1">E-mail</th>
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
          <td :class="cell(e.room)">
            <span class="emp-label">Xona</span>
            <span class="tabular-nums">{{ e.room }}</span>
          </td>
          <td :class="cell(e.internal_phone)">
            <span class="emp-label">Ichki</span>
            <span class="phone text-base font-semibold text-brand-700 print:text-[10pt] print:text-black">{{ e.internal_phone }}</span>
          </td>
          <td :class="cell(e.city_phone)">
            <span class="emp-label">Shahar</span>
            <a v-if="telHref(e.city_phone)" :href="telHref(e.city_phone)!" class="phone hover:text-brand-700 hover:underline">{{ e.city_phone }}</a>
            <span v-else class="phone">{{ e.city_phone }}</span>
          </td>
          <td :class="cell(e.mobile_phone)">
            <span class="emp-label">Mobil</span>
            <a v-if="telHref(e.mobile_phone)" :href="telHref(e.mobile_phone)!" class="phone hover:text-brand-700 hover:underline">{{ e.mobile_phone }}</a>
            <span v-else class="phone">{{ e.mobile_phone }}</span>
          </td>
          <td :class="cell(e.email)">
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
