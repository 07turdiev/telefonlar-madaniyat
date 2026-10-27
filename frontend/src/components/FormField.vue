<script setup lang="ts">
defineProps<{ label: string; error?: string; required?: boolean; hint?: string; for?: string }>()
</script>

<template>
  <div>
    <label :for="$props.for" class="mb-1 block text-sm font-medium text-slate-700">
      {{ label }}<span v-if="required" class="text-red-500"> *</span>
    </label>
    <slot />
    <p v-if="error" class="mt-1 text-xs text-red-600">{{ error }}</p>
    <p v-else-if="hint" class="mt-1 text-xs text-slate-500">{{ hint }}</p>
  </div>
</template>
