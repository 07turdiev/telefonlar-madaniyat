<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { api, errorMessage, fieldErrors } from '@/api'
import AppModal from '@/components/AppModal.vue'
import FormField from '@/components/FormField.vue'
import { useToastStore } from '@/stores/toast'
import type { Department, Employee, EmployeeInput } from '@/types'

const props = defineProps<{
  employee: Employee | null
  departments: Department[]
  departmentId?: number | null
}>()
const emit = defineEmits<{ close: []; saved: [] }>()
const toast = useToastStore()

const blank = (departmentId: number | null): EmployeeInput => ({
  department_id: departmentId,
  full_name: '',
  position: '',
  room: '',
  internal_phone: '',
  city_phone: '',
  mobile_phone: '',
  email: '',
})

const form = reactive<EmployeeInput>(
  props.employee ? { ...props.employee } : blank(props.departmentId ?? null),
)
const errors = ref<Record<string, string>>({})
const busy = ref(false)
const isNew = computed(() => !props.employee)
const nameInput = ref<HTMLInputElement>()

async function save(addAnother = false) {
  busy.value = true
  errors.value = {}
  try {
    if (props.employee) await api.put(`/admin/employees/${props.employee.id}`, form)
    else await api.post('/admin/employees', form)
    toast.ok(`${form.full_name} saqlandi.`)
    emit('saved')
    if (addAnother) {
      // Ko'p hodim kiritilayotganda bo'lim tanlovi saqlanadi, qolgan maydonlar tozalanadi.
      Object.assign(form, blank(form.department_id))
      nameInput.value?.focus()
    } else {
      emit('close')
    }
  } catch (e) {
    errors.value = fieldErrors(e)
    if (!Object.keys(errors.value).length) toast.error(errorMessage(e))
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <AppModal :title="isNew ? 'Yangi hodim' : 'Hodimni tahrirlash'" wide @close="emit('close')">
    <form id="employee-form" class="grid gap-4 sm:grid-cols-2" @submit.prevent="save()">
      <FormField label="Bo'lim" for="f-dept" required :error="errors.department_id" class="sm:col-span-2">
        <select id="f-dept" v-model="form.department_id" class="input" :class="{ 'input-error': errors.department_id }">
          <option :value="null" disabled>— Bo'limni tanlang —</option>
          <option v-for="d in departments" :key="d.id" :value="d.id">
            {{ d.level ? '    ' : '' }}{{ d.name }}
          </option>
        </select>
      </FormField>
      <FormField label="Familiya, ism, otasining ismi" for="f-name" required :error="errors.full_name" class="sm:col-span-2">
        <input
          id="f-name"
          ref="nameInput"
          v-model="form.full_name"
          class="input"
          :class="{ 'input-error': errors.full_name }"
          maxlength="200"
          placeholder="Karimov Anvar Aliyevich"
        />
      </FormField>
      <FormField label="Lavozimi" for="f-position" class="sm:col-span-2">
        <input id="f-position" v-model="form.position" class="input" maxlength="200" placeholder="Bo'lim boshlig'i" />
      </FormField>
      <FormField label="Ichki telefon" for="f-internal" hint="Bir nechta bo'lsa vergul bilan: 215, 216">
        <input id="f-internal" v-model="form.internal_phone" class="input" maxlength="200" inputmode="tel" />
      </FormField>
      <FormField label="Xona" for="f-room">
        <input id="f-room" v-model="form.room" class="input" maxlength="200" placeholder="305" />
      </FormField>
      <FormField label="Shahar telefoni" for="f-city">
        <input id="f-city" v-model="form.city_phone" class="input" maxlength="200" inputmode="tel" placeholder="71 239-00-00" />
      </FormField>
      <FormField label="Mobil telefon" for="f-mobile">
        <input id="f-mobile" v-model="form.mobile_phone" class="input" maxlength="200" inputmode="tel" placeholder="90 123-45-67" />
      </FormField>
      <FormField label="E-mail" for="f-email" :error="errors.email" class="sm:col-span-2">
        <input
          id="f-email"
          v-model="form.email"
          type="email"
          class="input"
          :class="{ 'input-error': errors.email }"
          maxlength="200"
          placeholder="ism@madaniyat.uz"
        />
      </FormField>
    </form>
    <template #footer>
      <button type="button" class="btn-secondary mr-auto" @click="emit('close')">Bekor qilish</button>
      <button v-if="isNew" type="button" class="btn-secondary" :disabled="busy" @click="save(true)">
        Saqlab, yana qo'shish
      </button>
      <button type="submit" form="employee-form" class="btn-primary" :disabled="busy">Saqlash</button>
    </template>
  </AppModal>
</template>
