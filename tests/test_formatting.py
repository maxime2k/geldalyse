"""Tests for the formatting of months, baselines and summaries in French."""

import pytest

from geldalyse.formatting import (
    format_month, format_baseline, format_amount, NBSP,
    format_change
)


@pytest.mark.parametrize(
    "month, expected",
    [
        ("2026-01", "janvier 2026"),
        ("2025-12", "décembre 2025"),
    ],
)
def test_format_month_writes_french_name(month, expected):
    assert format_month(month) == expected


@pytest.mark.parametrize(
    "months, expected",
    [
        (["2026-08"], "août 2026"),
        (["2026-06", "2026-07", "2026-08"], "la moyenne de juin à août 2026"),
        (["2025-11", "2025-12", "2026-01"], "la moyenne de novembre 2025 à janvier 2026"),
        (["2026-04", "2026-05", "2026-06"], "la moyenne d'avril à juin 2026"),
    ],
)
def test_format_baseline_describes_its_months(months, expected):
    assert format_baseline(months) == expected


@pytest.mark.parametrize(
    "amount, expected",
    [
        (1234.5, f"1{NBSP}234,50{NBSP}€"),
        (45.0, f"45,00{NBSP}€"),
        (0.0, f"0,00{NBSP}€"),
        (1234567.0, f"1{NBSP}234{NBSP}567,00{NBSP}€"),
    ],
)
def test_format_amount_writes_french_format(amount, expected):
    assert format_amount(amount) == expected


@pytest.mark.parametrize(
    "change, change_pct, expected",
    [
        (120.0, 0.09, f"+120,00{NBSP}€ (+9{NBSP}%)"),
        (-50.0, -0.04, f"-50,00{NBSP}€ (-4{NBSP}%)"),
        (40.0, float("nan"), f"+40,00{NBSP}€ (nouveau)"),
        (0.0, 0.0, f"0,00{NBSP}€ (0{NBSP}%)"),
    ],
)
def test_format_change_writes_amount_and_percentage(change, change_pct, expected):
    assert format_change(change, change_pct) == expected