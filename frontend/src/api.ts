import axios, { isAxiosError } from 'axios'

export const api = axios.create({
  baseURL: '/api',
  // Backend bu sarlavhasiz POST/PUT/DELETE so'rovlarni rad etadi (CSRF himoyasi).
  headers: { 'X-Requested-With': 'XMLHttpRequest' },
})

/** Server qaytargan umumiy xato matni. */
export function errorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (detail?.errors) return 'Formadagi xatolarni tuzating.'
    if (!error.response) return "Server bilan bog'lanib bo'lmadi."
  }
  return "Kutilmagan xatolik. Sahifani yangilab ko'ring."
}

/** Maydonlar bo'yicha xatolar: { full_name: "...", email: "..." }. */
export function fieldErrors(error: unknown): Record<string, string> {
  if (isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (detail && typeof detail === 'object' && detail.errors) return detail.errors
  }
  return {}
}
