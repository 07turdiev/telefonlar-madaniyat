"""Eski Word (.docx) telefon ma'lumotnomasidan bir martalik import.

    python -m scripts.import_docx eski.docx            # faqat ko'rsatadi, bazaga yozmaydi
    python -m scripts.import_docx eski.docx --save     # bazaga yozadi (baza bo'sh bo'lishi kerak)
    python -m scripts.import_docx eski.docx --save --replace   # eski ma'lumotni o'chirib yozadi

Jadval qatorlari quyidagicha tushuniladi:
- sarlavha qatori: ustun nomlari ("F.I.Sh.", "Lavozimi", "Ichki" ...), ikki qatorli bo'lishi mumkin;
- butun qator bo'ylab birlashtirilgan (yoki bitta matnli) qator: bo'lim nomi;
- qolganlari: hodim.
"""

import argparse
import re
import sys
from pathlib import Path

from docx import Document

COLUMN_KEYWORDS = {
    "full_name": ("f.i.sh", "ф.и.ш", "fish", "фиш", "f.i.o", "ф.и.о", "фио", "familiya", "фамилия"),
    "position": ("lavozim", "лавозим", "должност"),
    "room": ("xona", "хона", "kabinet", "кабинет", "каб."),
    "internal_phone": ("ichki", "ички", "внутр"),
    "city_phone": ("shahar", "шаҳар", "шахар", "город", "ish tel", "иш тел", "рабоч"),
    "mobile_phone": ("mobil", "мобил", "uyali", "уяли", "сотов"),
    "email": ("mail", "почта", "pochta"),
}
NO_DEPARTMENT = "Bo'lim ko'rsatilmagan"
INTERNAL_PHONE_RE = re.compile(r"(?<!\d)\d{4}(?!\d)")


def _cell_text(cell, multiline_sep: str) -> str:
    lines = [" ".join(p.split()) for p in cell.text.splitlines()]
    return multiline_sep.join(line for line in lines if line)


def _match_field(header: str) -> str | None:
    header = header.lower()
    for field, keywords in COLUMN_KEYWORDS.items():
        if any(k in header for k in keywords):
            return field
    return None


def parse_docx(path: Path) -> tuple[dict[int, str], list[tuple[str, list[dict]]]]:
    """(ustunlar xaritasi, [(bo'lim nomi, [hodim, ...]), ...]) qaytaradi."""
    doc = Document(str(path))
    sections: list[tuple[str, list[dict]]] = []
    columns: dict[int, str] = {}

    for table in doc.tables:
        header_texts: dict[int, str] | None = None
        for row in table.rows:
            cells = row.cells  # birlashgan katak har ustunda takrorlanadi
            texts = [_cell_text(c, " ") for c in cells]
            distinct = {id(c._tc): t for c, t in zip(cells, texts) if t}
            fields = {f for t in distinct.values() if (f := _match_field(t))}
            spans_row = len({id(c._tc) for c in cells}) == 1

            # Sarlavha qatori (ketma-ket ikki qator bo'lsa, matnlar ustun bo'yicha qo'shiladi).
            # Butun qator bo'ylab birlashgan katak sarlavha emas, bo'lim nomi: "Ichki audit bo'limi",
            # "Devonxona" kabi nomlardagi so'zlar ustun nomiga o'xshab qolmasin.
            if not spans_row and (len(fields) >= 2 or (header_texts is not None and fields)):
                header_texts = header_texts or {}
                for i, t in enumerate(texts):
                    header_texts[i] = f"{header_texts.get(i, '')} {t}".strip()
                columns = {}
                for i, t in header_texts.items():
                    field = _match_field(t)
                    if field and field not in columns.values():
                        columns[i] = field
                continue
            header_texts = None
            if not columns:
                continue

            if not distinct:
                continue
            if len(set(distinct.values())) == 1:
                only = next(iter(distinct.values()))
                if not re.fullmatch(r"[\d.\s]+", only):
                    sections.append((only, []))
                continue

            employee = {field: "" for field in COLUMN_KEYWORDS}
            for i, field in columns.items():
                if i < len(cells):
                    sep = " " if field in ("full_name", "position") else ", "
                    employee[field] = _cell_text(cells[i], sep)
            # Ichki raqam: faqat bitta 4 xonali raqam ("1000 68-11" → "1000").
            four_digits = INTERNAL_PHONE_RE.search(employee["internal_phone"])
            employee["internal_phone"] = four_digits.group(0) if four_digits else ""
            if not employee["full_name"]:
                continue
            if not sections:
                sections.append((NO_DEPARTMENT, []))
            sections[-1][1].append(employee)

    return columns, [(name, emps) for name, emps in sections if emps]


def save(conn, sections: list[tuple[str, list[dict]]], replace: bool) -> None:
    from app.db import EMPLOYEE_FIELDS, log, now

    has_data = conn.execute("SELECT 1 FROM departments").fetchone()
    if has_data and not replace:
        raise SystemExit("Bazada ma'lumot bor. Ustidan yozish uchun --replace qo'shing.")
    if replace:
        conn.execute("DELETE FROM employees")
        conn.execute("DELETE FROM departments")
    columns = [*EMPLOYEE_FIELDS, "department_id", "sort_order", "updated_at"]
    for dept_order, (name, employees) in enumerate(sections, start=1):
        dept_id = conn.execute(
            "INSERT INTO departments (name, parent_id, sort_order) VALUES (?, NULL, ?)",
            (name[:200], dept_order),
        ).lastrowid
        for emp_order, emp in enumerate(employees, start=1):
            conn.execute(
                f"INSERT INTO employees ({', '.join(columns)}) VALUES ({', '.join('?' * len(columns))})",
                [emp[f][:200] for f in EMPLOYEE_FIELDS] + [dept_id, emp_order, now()],
            )
    total = sum(len(e) for _, e in sections)
    log(conn, "konsol", "Word'dan import", f"{len(sections)} bo'lim, {total} hodim")
    conn.commit()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m scripts.import_docx")
    parser.add_argument("file", type=Path)
    parser.add_argument("--save", action="store_true", help="bazaga yozish")
    parser.add_argument("--replace", action="store_true", help="eski bo'lim va hodimlarni o'chirish")
    args = parser.parse_args(argv)

    columns, sections = parse_docx(args.file)
    if not columns:
        print("Sarlavha qatori topilmadi (F.I.Sh., Lavozimi, Ichki ...). Faylni dasturchiga yuboring.")
        return 1
    print("Ustunlar:", ", ".join(f"{i + 1}-ustun → {f}" for i, f in sorted(columns.items())))
    for name, employees in sections:
        print(f"\n== {name} ({len(employees)})")
        for emp in employees:
            parts = [emp["full_name"], emp["position"]]
            parts += [f"{k}: {emp[k]}" for k in ("room", "internal_phone", "city_phone", "mobile_phone", "email") if emp[k]]
            print("   " + " | ".join(p for p in parts if p))
    total = sum(len(e) for _, e in sections)
    print(f"\nJami: {len(sections)} bo'lim, {total} hodim.")

    if not args.save:
        print("Bazaga yozilmadi. Hammasi to'g'ri bo'lsa, --save bilan qayta ishga tushiring.")
        return 0
    from app.config import load_settings
    from app.db import connect, init_db

    settings = load_settings()
    init_db(settings.db_path)
    conn = connect(settings.db_path)
    try:
        save(conn, sections, args.replace)
    finally:
        conn.close()
    print(f"Saqlandi: {settings.db_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
