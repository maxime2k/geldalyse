import pandas as pd
import pytest

from geldalyse.readers import InvalidStatementError
from geldalyse.readers.base import (
    check_columns,
    clean_labels,
    parse_amounts,
    parse_dates,
)
from geldalyse.schema import MISSING_LABEL


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


def test_clean_labels_replaces_missing_label():
    assert clean_labels(pd.Series(["", "   "])).tolist() == [
        MISSING_LABEL,
        MISSING_LABEL,
    ]


def test_clean_labels_strip_and_uppercases():
    assert clean_labels(pd.Series(["  ami fictif  "])).tolist() == ["AMI FICTIF"]


def test_check_columns_names_missing_columns():

    with pytest.raises(InvalidStatementError, match=r"Colonnes manquantes : Date\.$"):
        check_columns(pd.DataFrame(columns=["Montant"]), ["Montant", "Date"])


def test_check_columns_accepts_complete_columns():

    check_columns(pd.DataFrame(columns=["Montant", "Date"]), ["Montant", "Date"])
