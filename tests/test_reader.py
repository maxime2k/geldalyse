"""Unit tests for the bank statement reader."""

from pathlib import Path

import pandas as pd
import pytest

from geldalyse.reader import read_bank_statement
from geldalyse.schema import STANDARD_COLUMNS

FIXTURES_DIR = Path(__file__).parent / "fixtures"
ING_SAMPLE = FIXTURES_DIR/ "ing_export_sample.csv"
WRONG_COLUMNS = FIXTURES_DIR / "wrong_format.csv"
WRONG_DATE_FORMAT = FIXTURES_DIR / "wrong_date_format.csv"
EMPTY_FILE = FIXTURES_DIR / "empty.csv"


def test_output_columns_match():
    transactions = read_bank_statement(ING_SAMPLE)
    assert list(transactions.columns) == STANDARD_COLUMNS


def test_small_negative_amount_keeps_sign():
    transactions = read_bank_statement(ING_SAMPLE)
    assert transactions["amount"][3] == -0.5


def test_dates_are_converted():
    transactions = read_bank_statement(ING_SAMPLE)
    assert transactions["date"][0] == pd.Timestamp(2025, 12, 31)


def test_output_has_no_missing_values():
    transactions = read_bank_statement(ING_SAMPLE)
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
        
