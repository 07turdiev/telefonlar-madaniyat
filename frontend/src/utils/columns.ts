import type { Section } from '@/types'

export const OPTIONAL_COLUMNS = ['room', 'internal_phone', 'city_phone', 'mobile_phone', 'email'] as const
export type ColumnKey = (typeof OPTIONAL_COLUMNS)[number]

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
