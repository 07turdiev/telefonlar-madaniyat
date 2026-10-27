<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { api, errorMessage, fieldErrors } from '@/api'
import AppModal from '@/components/AppModal.vue'
import FormField from '@/components/FormField.vue'
import { useToastStore } from '@/stores/toast'
import type { DepartmentWithCount } from '@/types'

const props = defineProps<{
  department: DepartmentWithCount | null
  departments: DepartmentWithCount[]
  parentId?: number | null
}>()
const emit = defineEmits<{ close: []; saved: [] }>()
const toast = useToastStore()

const form = reactive({
  name: props.department?.name ?? '',
  parent_id: props.department ? props.department.parent_id : (props.parentId ?? null),
})
const errors = ref<Record<string, string>>({})
const busy = ref(false)

// Faqat ikki daraja: yuqori bo'lim (boshqarma) va uning ichidagi bo'lim.
const parents = computed(() => props.departments.filter((d) => d.level === 0 && d.id !== props.department?.id))
const hasChildren = computed(
  () => !!props.department && props.departments.some((d) => d.parent_id === props.department!.id),
)

async function save() {
  busy.value = true
  errors.value = {}
  try {
    if (props.department) await api.put(`/admin/departments/${props.department.id}`, form)
    else await api.post('/admin/departments', form)
    toast.ok(`«${form.name}» saqlandi.`)
    emit('saved')
    emit('close')
  } catch (e) {
    errors.value = fieldErrors(e)
    if (!Object.keys(errors.value).length) toast.error(errorMessage(e))
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <AppModal :title="department ? 'Bo\'limni tahrirlash' : 'Yangi bo\'lim'" @close="emit('close')">
    <form id="department-form" class="space-y-4" @submit.prevent="save">
      <FormField label="Nomi" for="d-name" required :error="errors.name">
        <input
          id="d-name"
          v-model="form.name"
          class="input"
          :class="{ 'input-error': errors.name }"
          maxlength="200"
          placeholder="Moliya-iqtisodiyot bo'limi"
        />
      </FormField>
      <FormField
        label="Qaysi bo'lim ichida"
        for="d-parent"
        :error="errors.parent_id"
        :hint="hasChildren ? 'Ichida bo\'limlari bor, shuning uchun yuqori darajada qoladi.' : 'Masalan, bo\'lim boshqarma tarkibida bo\'lsa.'"
      >
        <select id="d-parent" v-model="form.parent_id" class="input" :disabled="hasChildren">
          <option :value="null">— Yuqori daraja —</option>
          <option v-for="p in parents" :key="p.id" :value="p.id">{{ p.name }}</option>
        </select>
      </FormField>
    </form>
    <template #footer>
      <button type="button" class="btn-secondary" @click="emit('close')">Bekor qilish</button>
      <button type="submit" form="department-form" class="btn-primary" :disabled="busy">Saqlash</button>
    </template>
  </AppModal>
</template>
