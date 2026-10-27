import { computed, type Ref } from 'vue'
import type { Section } from '@/types'
import { buildIndex, matches, queryTokens, type SearchIndex } from '@/utils/search'

/**
 * Bo'limlar ro'yxatini qidiruv so'zi va tanlangan bo'lim bo'yicha filtrlaydi.
 * Yuqori bo'lim tanlansa, uning ichki bo'limlari ham ko'rinadi.
 * keepEmpty: qidiruv bo'lmaganda hodimsiz bo'limlarni ham qoldirish (admin uchun).
 */
export function useDirectoryFilter(
  sections: Ref<Section[]>,
  query: Ref<string>,
  departmentId: Ref<number | null>,
  keepEmpty = false,
) {
  const indexes = computed(() => {
    const names = new Map(sections.value.map((s) => [s.id, s.name]))
    const map = new Map<number, SearchIndex>()
    for (const s of sections.value) {
      const parentName = s.parent_id ? (names.get(s.parent_id) ?? '') : ''
      for (const e of s.employees) {
        map.set(
          e.id,
          buildIndex(
            [e.full_name, e.position, e.room, e.email, s.name, parentName],
            [e.internal_phone, e.city_phone, e.mobile_phone],
          ),
        )
      }
    }
    return map
  })

  const tokens = computed(() => queryTokens(query.value))
  const active = computed(() => tokens.value.length > 0 || departmentId.value !== null)

  const filtered = computed<Section[]>(() => {
    const dept = departmentId.value
    const result = sections.value
      .filter((s) => dept === null || s.id === dept || s.parent_id === dept)
      .map((s) => ({
        ...s,
        employees: tokens.value.length
          ? s.employees.filter((e) => matches(indexes.value.get(e.id)!, tokens.value))
          : s.employees,
      }))
    const keep = new Set(
      result.filter((s) => s.employees.length > 0 || (keepEmpty && !tokens.value.length)).map((s) => s.id),
    )
    // Ichki bo'limi ko'rinsa, yuqori bo'lim sarlavhasi ham ko'rinadi.
    for (const s of result) if (keep.has(s.id) && s.parent_id) keep.add(s.parent_id)
    return result.filter((s) => keep.has(s.id))
  })

  const count = computed(() => filtered.value.reduce((n, s) => n + s.employees.length, 0))
  const total = computed(() => sections.value.reduce((n, s) => n + s.employees.length, 0))

  /** Sarlavhada yuqori bo'lim nomini ko'rsatish kerakmi (u ro'yxatda ko'rinmayotgan bo'lsa). */
  function parentNameFor(section: Section): string | null {
    if (!section.parent_id || filtered.value.some((s) => s.id === section.parent_id)) return null
    return sections.value.find((s) => s.id === section.parent_id)?.name ?? null
  }

  return { filtered, count, total, active, parentNameFor }
}
