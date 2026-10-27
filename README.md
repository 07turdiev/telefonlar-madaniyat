# Telefon ma'lumotnomasi — Madaniyat vazirligi

Ilgari qog'ozda tarqatilgan hodimlar telefon ro'yxatining ichki tarmoqdagi sayt ko'rinishi.

- **Hodimlar** saytni parolsiz ochadi (faqat ichki tarmoqdan). Ism, lavozim, xona yoki raqam bo'yicha qidiradi,
  bo'lim bo'yicha saralaydi, kerak bo'lsa chop etadi. Qidiruv lotin va kirill yozuvida bir xil ishlaydi.
- **Kadrlar bo'limi** `/admin` orqali login bilan kiradi: bo'limlar va hodimlarni qo'shadi, tahrirlaydi,
  tartibini o'zgartiradi, Excel'ga yuklab oladi. Har bir o'zgarish jurnalga yoziladi (kim, qachon, nima).

Hodim ma'lumotlari: F.I.Sh., lavozim, bo'lim, xona, ichki telefon, shahar telefoni, mobil telefon, e-mail.
Bo'limlar ikki darajali: yuqori bo'lim (masalan, boshqarma) va uning ichidagi bo'limlar.

## Tuzilma

```
backend/    FastAPI + SQLite. JSON API: /api/directory (ochiq), /api/auth/*, /api/admin/*
frontend/   Vue 3 + TypeScript + Vite + Tailwind (ochiq sahifa va kadrlar paneli)
deploy/     Linux server uchun nginx va systemd fayllari
```

Ma'lumotlar bitta faylda: `backend/data/telefonlar.db`. Alohida baza serveri kerak emas.

## Kompyuterda ishga tushirish

Talablar: Python 3.11+, Node.js 20+.

```powershell
# Backend
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt
copy .env.example .env
.venv\Scripts\python -m app.auth create-user kadrlar --admin --name "Kadrlar bo'limi"
.venv\Scripts\python -m uvicorn --factory app.main:create_app --port 8000 --reload

# Frontend (boshqa oynada)
cd frontend
npm install
npm run dev          # http://localhost:5173, /api so'rovlari 8000-portga uzatiladi
```

Namuna ma'lumot bilan ko'rish uchun (faqat bo'sh bazaga yozadi): `.venv\Scripts\python -m scripts.demo_data`

> **npm sekin ishlasa yoki `UNABLE_TO_VERIFY_LEAF_SIGNATURE` xatosi chiqsa:** tarmoq HTTPS'ni o'z sertifikati
> bilan qayta imzolayapti, Node.js esa unga ishonmaydi. Windows sertifikatlaridan foydalanishni yoqing:
> `$env:NODE_OPTIONS='--use-system-ca'` (PowerShell), keyin `npm install`. SSL tekshiruvini o'chirmang.

## Eski Word ro'yxatni import qilish

```powershell
cd backend
.venv\Scripts\python -m scripts.import_docx "D:\eski-ma'lumotnoma.docx"          # faqat ko'rsatadi
.venv\Scripts\python -m scripts.import_docx "D:\eski-ma'lumotnoma.docx" --save   # bazaga yozadi
```

Skript jadval sarlavhasidagi so'zlardan ustunlarni topadi ("F.I.Sh.", "Lavozimi", "Xona", "Ichki", "Shahar",
"Mobil", "E-mail", kirillchasi ham). Butun qator bo'ylab birlashtirilgan qatorni bo'lim nomi deb oladi.
Avval `--save`siz ishga tushirib, natijani tekshiring. Bazada ma'lumot bo'lsa, `--save` rad etadi;
eski ma'lumotni o'chirib qayta yozish uchun `--save --replace`.

Bo'limlar import qilingandan keyin bitta darajada bo'ladi; boshqarma ichidagi bo'limlarni kadrlar paneli
orqali joylashtiring.

## Testlar

```powershell
cd backend;  .venv\Scripts\python -m pytest -q
cd frontend; npm run typecheck
```

## Serverga o'rnatish (Ubuntu/Debian)

```bash
sudo apt install python3-venv nginx
sudo useradd --system --home /opt/telefonlar --shell /usr/sbin/nologin telefonlar
sudo mkdir -p /opt/telefonlar && sudo cp -r backend deploy /opt/telefonlar/

# Frontend: istalgan kompyuterda yig'ib, tayyor papkani serverga ko'chiring
#   cd frontend && npm ci && npm run build     →   /opt/telefonlar/frontend/dist

cd /opt/telefonlar/backend
sudo python3 -m venv .venv
sudo .venv/bin/pip install -r requirements.txt
sudo cp .env.example .env            # ORG_NAME va boshqalarni tekshiring
sudo mkdir -p data && sudo chown -R telefonlar:telefonlar data
sudo -u telefonlar .venv/bin/python -m app.auth create-user kadrlar --admin --name "Kadrlar bo'limi"

sudo cp /opt/telefonlar/deploy/telefonlar.service /etc/systemd/system/
sudo systemctl enable --now telefonlar

sudo cp /opt/telefonlar/deploy/nginx.conf /etc/nginx/sites-available/telefonlar
sudo ln -s /etc/nginx/sites-available/telefonlar /etc/nginx/sites-enabled/
sudo nano /etc/nginx/sites-available/telefonlar   # server_name va allow qatorlari
sudo nginx -t && sudo systemctl reload nginx
```

**Muhim:** `nginx.conf` dagi `allow` qatorlarida faqat xodimlar tarmog'i (VLAN) bo'lsin. Mehmonlar Wi-Fi
tarmog'i ham ichki manzil oladi; uni qo'shib qo'ysangiz, begonalar hodimlarning mobil raqamlarini ko'radi.
Server oldida teskari proksi (HTTPS uchun) tursa, nginx hamma tashrifchini proksi manzili bilan ko'radi va
`allow` cheklovi ishlamaydi. Bunday holda saytni proksi orqali o'tmaydigan alohida portda oching va proksi
manzilini `deny` qiling.

### Yangilash

GitHub'ga yangi versiya yuklangandan keyin serverda:

```bash
cd <loyiha papkasi> && bash deploy/update.sh
```

### Zaxira nusxa

Baza bitta fayl. Kuniga bir marta nusxa olish (`sudo crontab -e`):

```
30 2 * * * sqlite3 /opt/telefonlar/backend/data/telefonlar.db ".backup /var/backups/telefonlar-$(date +\%F).db"
```

(`sudo apt install sqlite3`. Oddiy `cp` ishlayotgan bazadan buzilgan nusxa olishi mumkin, `.backup` xavfsiz.)

### Foydalanuvchilar

- Birinchi administrator buyruq qatoridan yaratiladi (yuqorida). Keyingilarini administrator panelda
  "Foydalanuvchilar" bo'limidan qo'shadi.
- **Administrator** foydalanuvchilarni qo'sha, o'chira va parolini almashtira oladi; **tahrirlovchi** faqat
  bo'lim va hodimlar bilan ishlaydi.
- Parol unutilsa: `sudo -u telefonlar .venv/bin/python -m app.auth set-password <login>`
- Bir login uchun 10 daqiqada 5 marta noto'g'ri parol kiritilsa, kirish vaqtincha bloklanadi.
