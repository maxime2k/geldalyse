"""Tests for the formatting of months, baselines and summaries in French."""

import pytest

from geldalyse.formatting import format_month


@pytest.mark.parametrize(
    "month, expected",
    [
        ("2026-01", "janvier 2026"),
        ("2025-12", "décembre 2025"),
    ],
)
def test_format_month_writes_french_name(month, expected):
    assert format_month(month) == expected