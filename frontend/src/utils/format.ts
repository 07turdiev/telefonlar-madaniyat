/** Mobil va shahar raqamlari uchun tel: havola. Qisqa ichki raqamga havola bo'lmaydi. */
export function telHref(phone: string): string | null {
  const first = phone.split(/[,;/]/)[0]
  const digits = first.replace(/\D/g, '')
  if (digits.length === 9) return `tel:+998${digits}`
  if (digits.length === 12 && digits.startsWith('998')) return `tel:+${digits}`
  return null
}

/** "2026-10-27T15:40:12" → "27.10.2026 15:40" */
export function formatDateTime(iso: string | null | undefined): string {
  if (!iso) return ''
  const [date, time = ''] = iso.split('T')
  const [y, m, d] = date.split('-')
  return `${d}.${m}.${y} ${time.slice(0, 5)}`.trim()
}
