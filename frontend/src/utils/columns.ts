import type { Section } from '@/types'

export const OPTIONAL_COLUMNS = ['room', 'internal_phone', 'city_phone', 'mobile_phone', 'email'] as const
export type ColumnKey = (typeof OPTIONAL_COLUMNS)[number]

/** Vakant o'rinda shu maydonlar bo'sh bo'ladi va "-" bilan ko'rsatiladi (backend'dagi VACANT_CLEARED). */
export const VACANT_CLEARED = OPTIONAL_COLUMNS
export const VACANT_NAME = 'Vakant'

/** Kamida bitta hodimda to'ldirilgan ustunlar. Butunlay bo'sh ustun jadvalda ko'rsatilmaydi. */
export function usedColumns(sections: Section[]): ColumnKey[] {
  return OPTIONAL_COLUMNS.filter((key) => sections.some((s) => s.employees.some((e) => e[key].trim())))
}

/** "1000, 68-11" → ["1000", "68-11"]: har bir raqam alohida qatorda chiqadi. */
export function splitValues(value: string): string[] {
  return value
    .split(/[,;]/)
    .map((v) => v.trim())
    .filter(Boolean)
}
