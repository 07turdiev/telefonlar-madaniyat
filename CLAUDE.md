# telefonlar-madaniyat: loyiha bo'yicha ko'rsatmalar

Madaniyat vazirligi hodimlarining ichki telefon ma'lumotnomasi. Umumiy tavsif, ishga tushirish va o'rnatish: [README.md](README.md).

## Foydalanuvchi tasdiqlagan qarorlar

- Ko'rish parolsiz, faqat ichki tarmoqdan (cheklov nginx'da, `deploy/nginx.conf`). Login faqat kadrlar bo'limi uchun.
- Maydonlar: F.I.Sh., lavozim, bo'lim, xona, ichki tel., shahar tel., mobil, e-mail.
- Ichki raqam: faqat bitta 4 xonali raqam yoki bo'sh ("68-11" kabi qo'shimcha raqamlar kerak emas). Backend, forma va import shuni tekshiradi.
- Vakant o'rin (`employees.is_vacant`): F.I.Sh. "Vakant", lavozim majburiy, qolgan BARCHA maydonlar (ichki va shahar tel. ham) bo'sh va hamma joyda "-" ko'rsatiladi.
- Server: Linux (nginx + systemd). Frontend Vue'da (foydalanuvchi so'rovi).
- Eski ro'yxat Word (.docx) faylda, `backend/scripts/import_docx.py` orqali import. Haqiqiy fayl hali ko'rilmagan:
  u kelganda importni shu faylda tekshirish kerak.

## Texnik tuzilma

- `backend/`: Python 3.11+, FastAPI, SQLite (`sqlite3` standart moduli, ORM yo'q). Ilova `app.main:create_app` (factory).
  - `app/public.py`: `/api/directory` (ochiq) va `/api/auth/*`.
  - `app/admin.py`: `/api/admin/*`, hammasi login talab qiladi; foydalanuvchilar bo'limi faqat `is_admin`.
  - `app/db.py`: sxema, `directory()`, tartib (`move`), jurnal (`log`). Har o'zgarish `audit_log`ga yoziladi.
  - Xato formati: `{"detail": "matn"}` yoki maydonlar bo'yicha `{"detail": {"errors": {"field": "matn"}}}`.
  - CSRF: POST/PUT/DELETE `X-Requested-With: XMLHttpRequest` sarlavhasini talab qiladi (`main.py`).
- `frontend/`: Vue 3 + TS + Vite + Pinia + vue-router + axios + Tailwind 3. Tashqi CDN/shrift yo'q (ichki tarmoqda internet bo'lmasligi mumkin).
  - Qidiruv `src/utils/search.ts`: kirill→lotin, tutuq belgilari va x/h farqi e'tiborga olinmaydi.
  - `EmployeeTable.vue` ochiq sahifa va admin uchun umumiy; `lg` dan tor ekranda kartochka.
- TypeScript 6 da qoldirilgan: vue-tsc TypeScript 7 bilan ishlamaydi.
- Tarmoqda npm uchun `NODE_OPTIONS=--use-system-ca` kerak (HTTPS inspeksiya).

## Tekshirish

Har o'zgarishdan keyin: `backend` da `.venv\Scripts\python -m pytest -q`, `frontend` da `npm run typecheck` va `npm run build`.
