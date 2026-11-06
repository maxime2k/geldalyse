import pandas as pd
import pytest

from geldalyse.readers import InvalidStatementError
from geldalyse.readers.base import parse_amounts, parse_dates


@pytest.mark.parametrize(
    "date",
    [
        "",
        "any text",
        "30/02/2015",
        "25/01/203",
        "2026/02/15",
        "2026-01-03",
        "29/02/2025",
    ],
)
def test_parse_dates_rejects_invalid_date(date):
    with pytest.raises(InvalidStatementError, match="Ligne 2"):
        parse_dates(pd.Series([date]))


def test_parse_dates_accepts_leap_day():
    dates = parse_dates(pd.Series(["29/02/2024"]))
    assert dates.iloc[0] == pd.Timestamp(2024, 2, 29)


def test_parse_dates_reads_day_first():
    dates = parse_dates(pd.Series(["05/01/2021"]))
    assert dates.iloc[0] == pd.Timestamp(2021, 1, 5)


def test_parse_amounts_rejects_invalid_amount():
    with pytest.raises(InvalidStatementError, match="Ligne 3"):
        parse_amounts(pd.Series(["1.5", "abc"]), float)


def test_parse_amounts_converts_each_amount():
    assert parse_amounts(pd.Series(["1.5", "2"]), float).tolist() == [1.5, 2.0]
