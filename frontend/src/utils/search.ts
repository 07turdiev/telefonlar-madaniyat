// Qidiruv lotin va kirill yozuvida bir xil ishlaydi: "Каримов" ham, "karimov" ham "Karimov"ni topadi.
// O'zbekcha tutuq belgilari (o', g', oʻ, g‘ ...) e'tiborga olinmaydi, x va h bir harf deb qaraladi.

const CYRILLIC: Record<string, string> = {
  а: 'a', б: 'b', в: 'v', г: 'g', д: 'd', е: 'e', ё: 'yo', ж: 'j', з: 'z', и: 'i', й: 'y',
  к: 'k', л: 'l', м: 'm', н: 'n', о: 'o', п: 'p', р: 'r', с: 's', т: 't', у: 'u', ф: 'f',
  х: 'x', ц: 'ts', ч: 'ch', ш: 'sh', щ: 'sh', ъ: '', ы: 'i', ь: '', э: 'e', ю: 'yu', я: 'ya',
  ў: 'o', қ: 'q', ғ: 'g', ҳ: 'h',
}

export function normalize(text: string): string {
  let out = ''
  for (const ch of text.toLowerCase()) out += CYRILLIC[ch] ?? ch
  return out
    .replace(/[ʻʼ'‘’`´]/g, '')
    .replace(/x/g, 'h')
    .replace(/\s+/g, ' ')
    .trim()
}

const digitsOnly = (s: string) => s.replace(/\D/g, '')

export interface SearchIndex {
  text: string
  digits: string
}

export function buildIndex(texts: string[], phones: string[]): SearchIndex {
  return { text: normalize(texts.join(' ')), digits: phones.map(digitsOnly).join(' ') }
}

export function queryTokens(query: string): string[] {
  return normalize(query).split(' ').filter(Boolean)
}

/** Har bir so'z matnda yoki telefon raqamlarida (bo'shliq va tiresiz) uchrashi kerak. */
export function matches(index: SearchIndex, tokens: string[]): boolean {
  return tokens.every((token) => {
    if (index.text.includes(token)) return true
    return /^[\d\-()+.]+$/.test(token) && index.digits.includes(digitsOnly(token))
  })
}
