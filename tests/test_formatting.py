"""Tests for the formatting of months, baselines and summaries in French."""

import pytest

from geldalyse.formatting import format_month, format_baseline


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