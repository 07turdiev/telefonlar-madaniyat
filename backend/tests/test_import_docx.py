from docx import Document

from scripts.import_docx import parse_docx, save


def make_docx(path):
    """Qog'oz ma'lumotnomaga o'xshash jadval: ikki qatorli sarlavha, birlashgan bo'lim qatorlari."""
    doc = Document()
    doc.add_paragraph("TELEFON MA'LUMOTNOMASI")
    table = doc.add_table(rows=0, cols=6)

    def row(*values):
        cells = table.add_row().cells
        for cell, value in zip(cells, values):
            cell.text = value
        return cells

    head = row("№", "Ф.И.Ш.", "Лавозими", "Хона", "Телефон", "")
    head[4].merge(head[5])
    head[4].text = "Телефон"
    row("", "", "", "", "Ички", "Мобил")
    dept = row("Rahbariyat", "", "", "", "", "")
    dept[0].merge(dept[5]).text = "Rahbariyat"
    row("1", "Karimov Anvar\nAliyevich", "Vazir", "201", "1000", "90 123 45 67")
    row("2", "Toshmatova Gulnora", "Vazir o'rinbosari", "203", "1001\n57-89", "")  # haqiqiy faylda shunday
    dept = row("", "", "", "", "", "")
    dept[0].merge(dept[5]).text = "Moliya bo'limi"
    row("3", "Rahimov Bobur", "Bosh hisobchi", "310", "1500", "")
    row("", "Vakant", "Bosh mutaxassis", "311", "1501", "90 000 00 00")
    # Nomida ustun kalit so'zi bor bo'limlar ("ichki", "xona") sarlavha deb olinmasligi kerak.
    for name, person in (("Ichki audit bo'limi", "Aliyev Ali"), ("Ijro intizomi va devonxona bo'limi", "Valiyeva Vali")):
        dept = row("", "", "", "", "", "")
        dept[0].merge(dept[5]).text = name
        row("4", person, "Bosh mutaxassis", "401", "1600", "")
    doc.save(path)


def test_parse_docx(tmp_path):
    path = tmp_path / "eski.docx"
    make_docx(path)
    columns, sections = parse_docx(path)
    assert set(columns.values()) == {"full_name", "position", "room", "internal_phone", "mobile_phone"}
    assert [(name, len(emps)) for name, emps in sections] == [
        ("Rahbariyat", 2),
        ("Moliya bo'limi", 2),
        ("Ichki audit bo'limi", 1),
        ("Ijro intizomi va devonxona bo'limi", 1),
    ]
    first, second = sections[0][1]
    assert first["full_name"] == "Karimov Anvar Aliyevich"
    assert first["mobile_phone"] == "90 123 45 67"
    assert first["internal_phone"] == "1000"
    assert second["internal_phone"] == "1001"  # tire bilan yozilgan qo'shimcha raqam olinmaydi
    assert not first["is_vacant"]
    vacant = sections[1][1][1]
    assert (vacant["is_vacant"], vacant["full_name"], vacant["position"]) == (True, "Vakant", "Bosh mutaxassis")
    assert [vacant[f] for f in ("room", "internal_phone", "mobile_phone")] == ["", "", ""]
    audit = sections[2][1][0]
    assert (audit["full_name"], audit["room"], audit["internal_phone"]) == ("Aliyev Ali", "401", "1600")
    devon = sections[3][1][0]
    assert (devon["full_name"], devon["position"], devon["internal_phone"]) == ("Valiyeva Vali", "Bosh mutaxassis", "1600")


def test_save_refuses_to_overwrite(tmp_path, db):
    path = tmp_path / "eski.docx"
    make_docx(path)
    _, sections = parse_docx(path)
    save(db, sections, replace=False)
    assert db.execute("SELECT COUNT(*), SUM(is_vacant) FROM employees").fetchone()[:] == (6, 1)
    try:
        save(db, sections, replace=False)
    except SystemExit:
        pass
    else:
        raise AssertionError("ikkinchi import rad etilishi kerak edi")
    save(db, sections, replace=True)
    assert db.execute("SELECT COUNT(*) FROM employees").fetchone()[0] == 6
