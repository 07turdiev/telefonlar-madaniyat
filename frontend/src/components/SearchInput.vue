<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import AppIcon from './AppIcon.vue'

defineProps<{ placeholder?: string }>()
const model = defineModel<string>({ required: true })
const input = ref<HTMLInputElement>()

// "/" tugmasi qidiruvga o'tkazadi, Esc tozalaydi.
function onKey(e: KeyboardEvent) {
  const target = e.target as HTMLElement
  const typing = ['INPUT', 'TEXTAREA', 'SELECT'].includes(target.tagName)
  if (e.key === '/' && !typing) {
    e.preventDefault()
    input.value?.focus()
  }
}
onMounted(() => document.addEventListener('keydown', onKey))
onBeforeUnmount(() => document.removeEventListener('keydown', onKey))

defineExpose({ focus: () => input.value?.focus() })
</script>

<template>
  <div class="relative">
    <AppIcon name="search" class="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-slate-400" />
    <input
      ref="input"
      v-model="model"
      type="search"
      class="input h-11 pl-10 pr-9 text-base"
      :placeholder="placeholder"
      autocomplete="off"
      spellcheck="false"
      @keydown.esc="model = ''"
    />
    <button
      v-if="model"
      type="button"
      class="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1 text-slate-400 hover:text-slate-700"
      aria-label="Qidiruvni tozalash"
      @click="model = ''; input?.focus()"
    >
      <AppIcon name="x" class="h-4 w-4" />
    </button>
  </div>
</template>
