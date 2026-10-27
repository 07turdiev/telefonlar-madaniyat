<script setup lang="ts">
import { useToastStore } from '@/stores/toast'
import AppIcon from './AppIcon.vue'

const toast = useToastStore()
</script>

<template>
  <div
    class="pointer-events-none fixed inset-x-4 bottom-4 z-50 flex flex-col items-center gap-2 sm:inset-x-auto sm:right-4 sm:items-end print:hidden"
    aria-live="polite"
  >
    <TransitionGroup
      enter-from-class="translate-y-2 opacity-0"
      enter-active-class="transition duration-200"
      leave-to-class="opacity-0"
      leave-active-class="transition duration-150"
    >
      <div
        v-for="t in toast.items"
        :key="t.id"
        class="pointer-events-auto flex w-full max-w-sm items-start gap-3 rounded-lg px-4 py-3 text-sm text-white shadow-lg"
        :class="t.kind === 'error' ? 'bg-red-600' : 'bg-slate-800'"
        role="status"
      >
        <AppIcon :name="t.kind === 'error' ? 'alert' : 'check'" class="mt-0.5 h-4 w-4 shrink-0" />
        <span class="flex-1">{{ t.text }}</span>
        <button class="-mr-1 opacity-70 hover:opacity-100" aria-label="Yopish" @click="toast.dismiss(t.id)">
          <AppIcon name="x" class="h-4 w-4" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>
