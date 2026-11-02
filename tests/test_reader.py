"""Unit tests for the bank statement reader."""

from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from geldalyse.reader import MISSING_LABEL, parse_amount, read_bank_statement
from geldalyse.schema import STANDARD_COLUMNS

FIXTURES_DIR = Path(__file__).parent / "fixtures"
WRONG_COLUMNS = FIXTURES_DIR / "wrong_format.csv"
EMPTY_FILE = FIXTURES_DIR / "empty.csv"
HEADER_ONLY = FIXTURES_DIR / "header_only.csv"


HEADER = (
    "Numéro de compte;Nom du compte;Compte contrepartie;Numéro de mouvement;"
    "Date comptable;Date valeur;Montant;Devise;Libellés;Détails du mouvement;Message"
)


def ing_csv(
    amount: str = "-12,50",
    date: str = "03/01/2026",
    label: str = "Retrait d'espèces Bancontact 11/02/26 - 14h48 - CASH 1000 - BRUSSELS",
) -> StringIO:
    """Return an in-memory ING export with one transaction of the given amount."""
    row = f";;;7;12/02/2026;{date};{amount};EUR;{label};;"
    return StringIO(f"{HEADER}\n{row}\n")


def test_output_columns_match(ing_sample):
    transactions = read_bank_statement(ing_sample)
    assert list(transactions.columns) == STANDARD_COLUMNS


def test_small_negative_amount_keeps_sign(ing_sample):
    transactions = read_bank_statement(ing_sample)
    assert transactions["amount"][3] == -0.5


def test_dates_are_converted(ing_sample):
    transactions = read_bank_statement(ing_sample)
    assert transactions["date"][0] == pd.Timestamp(2025, 12, 31)


def test_output_has_no_missing_values(ing_sample):
    transactions = read_bank_statement(ing_sample)
    assert not transactions.isna().any().any()


def test_non_ing_file_raises_key_error():
    with pytest.raises(KeyError):
        read_bank_statement(WRONG_COLUMNS)


def test_empty_file_raises_empty_data_error():
    with pytest.raises(pd.errors.EmptyDataError):
        read_bank_statement(EMPTY_FILE)


def test_header_only_returns_empty_table():
    transactions = read_bank_statement(HEADER_ONLY)
    assert transactions.empty
    assert list(transactions) == STANDARD_COLUMNS


@pytest.mark.parametrize(
    "amount, expected",
    [
        ("1250", 1250.0),
        ("1.350", 1350.0),
        ("-2200", -2200.0),
        ("1 350 480", 1350480.0),
        ("2.480.255", 2480255.0),
        ("12,5", 12.5),
        ("1.235,50", 1235.50),
        ("-1.235,50", -1235.50),
    ],
)
def test_parse_amount_reads_valid_amounts(amount, expected):
    assert parse_amount(amount) == expected


@pytest.mark.parametrize(
    "amount",
    [
        ("abc"),
        ("12.50"),
        (" "),
        (""),
        ("1.25"),
        ("1.25,00"),
        ("1.2345,00"),
        ("12,345"),
        ("12,"),
        ("1,2,3"),
        ("--5"),
    ],
)
def test_parse_amount_rejects_invalid_amounts(amount):
    with pytest.raises(ValueError):
        parse_amount(amount)


@pytest.mark.parametrize("amount", ["abc", "", "12.50"])
def test_read_bank_statement_rejects_invalid_amount(amount):
    with pytest.raises(ValueError, match="Ligne 2"):
        read_bank_statement(ing_csv(amount=amount))


@pytest.mark.parametrize(
    "date",
    ["", "any text", "30/02/2015", "25/01/203", "2026/02/15", "2026-01-03"],
)
def test_read_bank_statement_rejects_invalid_date(date):
    with pytest.raises(ValueError, match="Ligne 2"):
        read_bank_statement(ing_csv(date=date))


def test_read_bank_statement_reads_day_first():
    transactions = read_bank_statement(ing_csv(date="05/01/2021"))
    assert transactions["date"].iloc[0] == pd.Timestamp(2021, 1, 5)


@pytest.mark.parametrize("label", ["", "   "])
def test_read_bank_statement_replaces_missing_label(label):
    transactions = read_bank_statement(ing_csv(label=label))
    assert transactions["label"].iloc[0] == MISSING_LABEL
