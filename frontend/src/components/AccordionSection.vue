<script setup lang="ts">
import AppIcon from './AppIcon.vue'

defineProps<{
  id: number
  title: string
  level: 0 | 1
  count: number
  open: boolean
  parentName?: string | null
}>()
const emit = defineEmits<{ toggle: [] }>()
</script>

<template>
  <!-- break-inside-avoid: chop etishda sarlavha o'z jadvalidan boshqa sahifaga ajralib qolmaydi -->
  <section class="print:break-inside-avoid" :class="level === 1 && 'ml-4 sm:ml-8 print:ml-0'">
    <h2>
      <button
        :id="`dept-btn-${id}`"
        type="button"
        class="flex w-full items-center gap-3 rounded-xl border bg-white px-4 py-3.5 text-left shadow-sm transition
          hover:border-brand-200 hover:bg-brand-50/40 focus:outline-none focus-visible:ring-2 focus-visible:ring-brand-500
          print:rounded-none print:border-0 print:bg-transparent print:px-0 print:py-0 print:shadow-none print:focus-visible:ring-0"
        :class="open ? 'border-brand-200' : 'border-slate-200'"
        :aria-expanded="open"
        :aria-controls="`dept-body-${id}`"
        @click="emit('toggle')"
      >
        <span
          class="w-1 shrink-0 self-stretch rounded-full print:rounded-none print:bg-black"
          :class="level === 0 ? 'bg-brand-600' : 'bg-brand-200'"
          aria-hidden="true"
        />
        <span class="min-w-0 flex-1">
          <span v-if="parentName" class="block text-xs text-slate-500">{{ parentName }}</span>
          <span
            class="block font-semibold text-slate-900 print:text-black"
            :class="level === 0 ? 'text-base print:text-[12pt]' : 'text-[15px] print:text-[11pt]'"
          >{{ title }}</span>
        </span>
        <span class="shrink-0 rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600 print:hidden">
          {{ count }} ta
        </span>
        <AppIcon
          name="down"
          class="h-5 w-5 shrink-0 transition-transform duration-300 motion-reduce:transition-none print:hidden"
          :class="open ? 'rotate-180 text-brand-600' : 'text-slate-400'"
        />
      </button>
    </h2>
    <!-- Balandlik 0 → to'liq: grid-template-rows animatsiyasi. Chop etishda doim ochiq. -->
    <div
      :id="`dept-body-${id}`"
      role="region"
      :aria-labelledby="`dept-btn-${id}`"
      class="grid transition-[grid-template-rows] duration-300 ease-out motion-reduce:transition-none print:grid-rows-[1fr]"
      :class="open ? 'grid-rows-[1fr]' : 'grid-rows-[0fr]'"
      :inert="!open || undefined"
    >
      <div class="min-h-0 overflow-hidden print:overflow-visible">
        <div class="pt-2 print:pt-2">
          <slot />
        </div>
      </div>
    </div>
  </section>
</template>
