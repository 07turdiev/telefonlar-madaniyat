<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { api, errorMessage, fieldErrors } from '@/api'
import AppIcon from '@/components/AppIcon.vue'
import AppModal from '@/components/AppModal.vue'
import FormField from '@/components/FormField.vue'
import { useToastStore } from '@/stores/toast'
import type { Department, Employee, EmployeeInput } from '@/types'
import { VACANT_CLEARED, VACANT_NAME } from '@/utils/columns'

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
  is_vacant: false,
})

const form = reactive<EmployeeInput>(
  props.employee ? { ...props.employee } : blank(props.departmentId ?? null),
)
const errors = ref<Record<string, string>>({})
const busy = ref(false)
const isNew = computed(() => !props.employee)
const nameInput = ref<HTMLInputElement>()

// Ichki raqam: faqat raqamlar, ko'pi bilan 4 ta (harf, tire, bo'shliq yozilmaydi).
function onInternalInput(event: Event) {
  const input = event.target as HTMLInputElement
  input.value = input.value.replace(/\D/g, '').slice(0, 4)
  form.internal_phone = input.value
}

// Vakant: F.I.Sh. "Vakant", lavozimdan boshqa maydonlar "-". Qayta bosilsa, avvalgi qiymatlar qaytadi.
let beforeVacant: Pick<EmployeeInput, 'full_name' | (typeof VACANT_CLEARED)[number]> | null = null

function toggleVacant() {
  if (!form.is_vacant) {
    beforeVacant = {
      full_name: form.full_name,
      room: form.room,
      internal_phone: form.internal_phone,
      city_phone: form.city_phone,
      mobile_phone: form.mobile_phone,
      email: form.email,
    }
    for (const field of VACANT_CLEARED) form[field] = ''
    form.full_name = VACANT_NAME
    form.is_vacant = true
  } else {
    form.is_vacant = false
    form.full_name = beforeVacant && beforeVacant.full_name !== VACANT_NAME ? beforeVacant.full_name : ''
    for (const field of VACANT_CLEARED) form[field] = beforeVacant?.[field] ?? ''
    beforeVacant = null
    nameInput.value?.focus()
  }
  errors.value = {}
}

async function save(addAnother = false) {
  busy.value = true
  errors.value = {}
  try {
    if (props.employee) await api.put(`/admin/employees/${props.employee.id}`, form)
    else await api.post('/admin/employees', form)
    toast.ok(form.is_vacant ? `«${form.position}» vakant o'rin sifatida saqlandi.` : `${form.full_name} saqlandi.`)
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
      <FormField
        label="Familiya, ism, otasining ismi"
        for="f-name"
        :required="!form.is_vacant"
        :error="errors.full_name"
        :hint="form.is_vacant ? 'Lavozim bo\'sh. Odam tayinlansa, «Vakant» tugmasini qayta bosing.' : undefined"
        class="sm:col-span-2"
      >
        <div class="flex gap-2">
          <input
            id="f-name"
            ref="nameInput"
            v-model="form.full_name"
            class="input"
            :class="{ 'input-error': errors.full_name, '!font-medium !text-amber-700': form.is_vacant }"
            :disabled="form.is_vacant"
            maxlength="200"
            placeholder="Karimov Anvar Aliyevich"
          />
          <button
            type="button"
            class="btn shrink-0"
            :class="form.is_vacant
              ? 'border-amber-300 bg-amber-50 text-amber-800 hover:bg-amber-100'
              : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50'"
            :aria-pressed="form.is_vacant"
            title="Lavozim bo'sh (vakant)"
            @click="toggleVacant"
          >
            <AppIcon v-if="form.is_vacant" name="check" class="h-4 w-4" /> Vakant
          </button>
        </div>
      </FormField>
      <FormField label="Lavozimi" for="f-position" :required="form.is_vacant" :error="errors.position" class="sm:col-span-2">
        <input
          id="f-position"
          v-model="form.position"
          class="input"
          :class="{ 'input-error': errors.position }"
          maxlength="200"
          placeholder="Bo'lim boshlig'i"
        />
      </FormField>
      <FormField
        label="Ichki telefon"
        for="f-internal"
        :error="errors.internal_phone"
        :hint="form.is_vacant ? undefined : '4 xonali raqam, masalan 1290'"
      >
        <input
          id="f-internal"
          :value="form.internal_phone"
          class="input tabular-nums"
          :class="{ 'input-error': errors.internal_phone }"
          :disabled="form.is_vacant"
          maxlength="4"
          inputmode="numeric"
          :placeholder="form.is_vacant ? '-' : '1290'"
          autocomplete="off"
          @input="onInternalInput"
        />
      </FormField>
      <FormField label="Xona" for="f-room">
        <input id="f-room" v-model="form.room" class="input" :disabled="form.is_vacant" maxlength="200" :placeholder="form.is_vacant ? '-' : '305'" />
      </FormField>
      <FormField label="Shahar telefoni" for="f-city">
        <input
          id="f-city"
          v-model="form.city_phone"
          class="input"
          :disabled="form.is_vacant"
          maxlength="200"
          inputmode="tel"
          :placeholder="form.is_vacant ? '-' : '71 239-00-00'"
        />
      </FormField>
      <FormField label="Mobil telefon" for="f-mobile">
        <input
          id="f-mobile"
          v-model="form.mobile_phone"
          class="input"
          :disabled="form.is_vacant"
          maxlength="200"
          inputmode="tel"
          :placeholder="form.is_vacant ? '-' : '90 123-45-67'"
        />
      </FormField>
      <FormField label="E-mail" for="f-email" :error="errors.email" class="sm:col-span-2">
        <input
          id="f-email"
          v-model="form.email"
          type="email"
          class="input"
          :class="{ 'input-error': errors.email }"
          :disabled="form.is_vacant"
          maxlength="200"
          :placeholder="form.is_vacant ? '-' : 'ism@madaniyat.uz'"
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
