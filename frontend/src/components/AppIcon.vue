<script setup lang="ts">
import { ICONS, type IconName } from './icons'

defineProps<{ name: IconName }>()
</script>

<template>
  <svg
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <path v-for="(d, i) in ICONS[name]" :key="i" :d="d" />
  </svg>
</template>
