"""Unit tests for the bank statement reader."""

from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from geldalyse.reader import parse_amount, read_bank_statement
from geldalyse.schema import STANDARD_COLUMNS

FIXTURES_DIR = Path(__file__).parent / "fixtures"
WRONG_COLUMNS = FIXTURES_DIR / "wrong_format.csv"
WRONG_DATE_FORMAT = FIXTURES_DIR / "wrong_date_format.csv"
EMPTY_FILE = FIXTURES_DIR / "empty.csv"
HEADER_ONLY = FIXTURES_DIR / "header_only.csv"


HEADER = (
    "Numéro de compte;Nom du compte;Compte contrepartie;Numéro de mouvement;"
    "Date comptable;Date valeur;Montant;Devise;Libellés;Détails du mouvement;Message"
)


def ing_csv(amount: str) -> StringIO:
    """Return an in-memory ING export with one transaction of the given amount."""
    row = (
        f";;;7;12/02/2026;11/02/2026;{amount};"
        "EUR;Retrait d'espèces Bancontact 11/02/26 - 14h48 - CASH 1000 - BRUXELLES;;"
    )
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


def test_non_ing_date_format_raises_value_error():
    with pytest.raises(ValueError):
        read_bank_statement(WRONG_DATE_FORMAT)


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
        read_bank_statement(ing_csv(amount))
