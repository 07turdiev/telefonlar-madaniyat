import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Toast {
  id: number
  kind: 'ok' | 'error'
  text: string
}

export const useToastStore = defineStore('toast', () => {
  const items = ref<Toast[]>([])
  let nextId = 1

  function dismiss(id: number) {
    items.value = items.value.filter((t) => t.id !== id)
  }

  function show(text: string, kind: Toast['kind'] = 'ok') {
    const id = nextId++
    items.value.push({ id, kind, text })
    setTimeout(() => dismiss(id), kind === 'error' ? 7000 : 3500)
  }

  return { items, show, dismiss, ok: (t: string) => show(t), error: (t: string) => show(t, 'error') }
})
