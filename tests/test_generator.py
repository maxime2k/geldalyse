from datetime import date

from geldalyse.generator import generate_ing_export


def test_same_seed_gives_same_export():
    first = generate_ing_export(start=date(2026, 1, 1), days=90)
    second = generate_ing_export(start=date(2026, 1, 1), days=90)

    assert first == second


def test_salary_is_paid_every_month():
    export = generate_ing_export(start=date(2026, 1, 1), days=90)

    assert export.count("SOCIÉTÉ FICTIVE SA") == 3
