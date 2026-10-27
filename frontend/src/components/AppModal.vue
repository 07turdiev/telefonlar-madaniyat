<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import AppIcon from './AppIcon.vue'

defineProps<{ title: string; wide?: boolean }>()
const emit = defineEmits<{ close: [] }>()
const panel = ref<HTMLElement>()

function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}

onMounted(async () => {
  document.addEventListener('keydown', onKey)
  document.body.style.overflow = 'hidden'
  await nextTick()
  panel.value?.querySelector<HTMLElement>('input:not([type=hidden]), select, textarea')?.focus()
})
onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKey)
  document.body.style.overflow = ''
})
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-40 flex items-end justify-center bg-slate-900/40 p-0 sm:items-center sm:p-4" @mousedown.self="emit('close')">
      <div
        ref="panel"
        role="dialog"
        aria-modal="true"
        :aria-label="title"
        class="flex max-h-[92vh] w-full flex-col rounded-t-2xl bg-white shadow-xl sm:rounded-2xl"
        :class="wide ? 'sm:max-w-2xl' : 'sm:max-w-md'"
      >
        <div class="flex items-center justify-between border-b border-slate-200 px-5 py-4">
          <h2 class="text-base font-semibold text-slate-900">{{ title }}</h2>
          <button class="icon-btn -mr-2" aria-label="Yopish" @click="emit('close')">
            <AppIcon name="x" class="h-5 w-5" />
          </button>
        </div>
        <div class="overflow-y-auto px-5 py-4">
          <slot />
        </div>
        <div v-if="$slots.footer" class="flex justify-end gap-2 border-t border-slate-200 bg-slate-50 px-5 py-3 sm:rounded-b-2xl">
          <slot name="footer" />
        </div>
      </div>
    </div>
  </Teleport>
</template>
