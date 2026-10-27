<script setup lang="ts">
import type { Section } from '@/types'

defineProps<{ section: Section; parentName?: string | null; count?: number }>()
</script>

<template>
  <div class="mb-2 flex items-end justify-between gap-3">
    <div class="min-w-0">
      <p v-if="parentName" class="text-xs text-slate-500">{{ parentName }}</p>
      <h2
        v-if="section.level === 0"
        class="border-l-4 border-brand-600 pl-3 text-lg font-semibold text-slate-900 print:border-black print:text-[12pt]"
      >
        {{ section.name }}
        <span v-if="count !== undefined" class="ml-1 text-sm font-normal text-slate-400 print:hidden">{{ count }}</span>
      </h2>
      <h3 v-else class="pl-4 text-base font-semibold text-slate-700 print:text-[11pt]">
        {{ section.name }}
        <span v-if="count !== undefined" class="ml-1 text-sm font-normal text-slate-400 print:hidden">{{ count }}</span>
      </h3>
    </div>
    <slot />
  </div>
</template>
