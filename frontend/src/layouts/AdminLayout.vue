<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { errorMessage } from '@/api'
import AppIcon from '@/components/AppIcon.vue'
import type { IconName } from '@/components/icons'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'

const auth = useAuthStore()
const toast = useToastStore()
const router = useRouter()

const links = computed(() => {
  const items: { name: string; label: string; icon: IconName }[] = [
    { name: 'employees', label: 'Hodimlar', icon: 'users' },
    { name: 'departments', label: "Bo'limlar", icon: 'building' },
    { name: 'log', label: 'Jurnal', icon: 'list' },
  ]
  if (auth.user?.is_admin) items.push({ name: 'users', label: 'Foydalanuvchilar', icon: 'shield' })
  return items
})

async function logout() {
  try {
    await auth.logout()
    router.replace('/')
  } catch (e) {
    toast.error(errorMessage(e))
  }
}
</script>

<template>
  <div class="min-h-screen">
    <header class="bg-brand-800 text-white">
      <div class="mx-auto flex h-14 max-w-6xl items-center gap-3 px-4">
        <RouterLink :to="{ name: 'employees' }" class="flex items-center gap-2 font-semibold">
          <span class="grid h-8 w-8 place-items-center rounded-lg bg-white/10"><AppIcon name="phone" class="h-4 w-4" /></span>
          <span class="hidden sm:inline">Telefon ma'lumotnomasi</span>
          <span class="rounded bg-white/15 px-1.5 py-0.5 text-[11px] font-medium uppercase tracking-wide">Kadrlar</span>
        </RouterLink>
        <div class="ml-auto flex items-center gap-1 text-sm">
          <span class="mr-2 hidden text-brand-100 md:inline">{{ auth.user?.full_name || auth.user?.username }}</span>
          <a href="/" target="_blank" class="flex items-center gap-1.5 rounded-md px-2 py-1.5 text-brand-100 hover:bg-white/10 hover:text-white" title="Saytni ochish">
            <AppIcon name="external" class="h-4 w-4" /><span class="hidden lg:inline">Sayt</span>
          </a>
          <RouterLink :to="{ name: 'password' }" class="flex items-center gap-1.5 rounded-md px-2 py-1.5 text-brand-100 hover:bg-white/10 hover:text-white" title="Parolni almashtirish">
            <AppIcon name="key" class="h-4 w-4" /><span class="hidden lg:inline">Parol</span>
          </RouterLink>
          <button class="flex items-center gap-1.5 rounded-md px-2 py-1.5 text-brand-100 hover:bg-white/10 hover:text-white" title="Chiqish" @click="logout">
            <AppIcon name="logout" class="h-4 w-4" /><span class="hidden lg:inline">Chiqish</span>
          </button>
        </div>
      </div>
      <nav class="mx-auto flex max-w-6xl gap-1 overflow-x-auto px-4">
        <RouterLink
          v-for="link in links"
          :key="link.name"
          :to="{ name: link.name }"
          class="flex shrink-0 items-center gap-2 rounded-t-lg px-4 py-2.5 text-sm font-medium text-brand-100 transition hover:bg-white/10 hover:text-white"
          active-class="!bg-slate-50 !text-brand-800"
        >
          <AppIcon :name="link.icon" class="h-4 w-4" />{{ link.label }}
        </RouterLink>
      </nav>
    </header>
    <main class="mx-auto max-w-6xl px-4 py-6">
      <RouterView />
    </main>
  </div>
</template>
