"""Saytni ko'rsatish uchun namunaviy (to'qima) ma'lumot. Faqat bo'sh bazaga yozadi.

    python -m scripts.demo_data
"""

import sys

from app.config import load_settings
from app.db import connect, init_db, log, now

# (bo'lim, yuqori bo'lim yoki None, [(F.I.Sh., lavozim, xona, ichki, shahar, mobil, e-mail), ...])
DEMO = [
    ("Vazirlik rahbariyati", None, [
        ("Abdullayev Rustam Karimovich", "Vazir", "201", "1100", "71 239-17-00", "", "vazir@example.uz"),
        ("Yusupova Malika Bahodirovna", "Vazirning birinchi o'rinbosari", "203", "1101", "71 239-17-01", "", ""),
        ("Qodirov Sherzod Anvarovich", "Vazir o'rinbosari", "205", "1102", "71 239-17-02", "", ""),
    ]),
    ("Devonxona", None, [
        ("Nazarova Dilfuza Olimovna", "Devonxona mudiri", "110", "1120", "71 239-17-20", "90 111-22-33", "devon@example.uz"),
        ("Ergashev Bobur Tohirovich", "Bosh mutaxassis", "111", "1121", "", "", ""),
    ]),
    ("Madaniyat siyosati boshqarmasi", None, [
        ("Hamidov Jasur Rahimovich", "Boshqarma boshlig'i", "301", "1200", "71 239-17-30", "", ""),
    ]),
    ("Teatr san'ati bo'limi", "Madaniyat siyosati boshqarmasi", [
        ("Saidova Nodira Ilhomovna", "Bo'lim boshlig'i", "305", "1215", "", "93 222-33-44", "teatr@example.uz"),
        ("G'aniyev Otabek Shuhratovich", "Yetakchi mutaxassis", "306", "1216", "", "", ""),
    ]),
    ("Musiqa san'ati bo'limi", "Madaniyat siyosati boshqarmasi", [
        ("Xolmatova Shahnoza Erkinovna", "Bo'lim boshlig'i", "310", "1220", "", "", "musiqa@example.uz"),
        ("To'xtayev Sardor Ravshanovich", "Bosh mutaxassis", "311", "1221", "", "", ""),
    ]),
    ("Moliya-iqtisodiyot bo'limi", None, [
        ("Rahimova Gulnora Abdullayevna", "Bosh hisobchi", "401", "1300", "71 239-17-40", "", "moliya@example.uz"),
        ("Mirzayev Azizbek Ulug'bekovich", "Iqtisodchi", "402", "1301", "", "", ""),
    ]),
    ("Kadrlar bo'limi", None, [
        ("Tursunova Feruza Hamidovna", "Bo'lim boshlig'i", "120", "1130", "71 239-17-13", "", "kadrlar@example.uz"),
    ]),
    ("Axborot-kommunikatsiya texnologiyalari bo'limi", None, [
        ("Karimov Jahongir Farhodovich", "Bo'lim boshlig'i", "501", "1400", "", "97 333-44-55", "akt@example.uz"),
        ("Ismoilov Doniyor Akmalovich", "Tizim administratori", "502", "1401", "", "", ""),
    ]),
]


def main() -> int:
    settings = load_settings()
    init_db(settings.db_path)
    conn = connect(settings.db_path)
    try:
        if conn.execute("SELECT 1 FROM departments").fetchone():
            print("Bazada ma'lumot bor, demo yozilmadi.", file=sys.stderr)
            return 1
        ids: dict[str, int] = {}
        order: dict[int | None, int] = {}
        for name, parent, employees in DEMO:
            parent_id = ids[parent] if parent else None
            order[parent_id] = order.get(parent_id, 0) + 1
            ids[name] = conn.execute(
                "INSERT INTO departments (name, parent_id, sort_order) VALUES (?, ?, ?)",
                (name, parent_id, order[parent_id]),
            ).lastrowid
            for i, emp in enumerate(employees, start=1):
                conn.execute(
                    "INSERT INTO employees (full_name, position, room, internal_phone, city_phone,"
                    " mobile_phone, email, department_id, sort_order, updated_at)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (*emp, ids[name], i, now()),
                )
        log(conn, "konsol", "demo ma'lumot", f"{len(DEMO)} bo'lim")
        conn.commit()
    finally:
        conn.close()
    print(f"Demo ma'lumot yozildi: {settings.db_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
