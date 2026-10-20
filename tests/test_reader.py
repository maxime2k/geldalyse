"""Unit tests for the bank statement reader."""

from pathlib import Path

import pandas as pd

from spendlens.reader import read_bank_statement

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "ing_export_sample.csv"


def test_output_columns_match():
    transactions = read_bank_statement(FIXTURE_PATH)
    assert list(transactions.columns) == ["date", "label", "amount"]


def test_small_negative_amount_keeps_sign():
    transactions = read_bank_statement(FIXTURE_PATH)
    assert transactions["amount"][3] == -0.5


def test_dates_are_converted():
    transactions = read_bank_statement(FIXTURE_PATH)
    assert transactions["date"][0] == pd.Timestamp(2025, 12, 31)
