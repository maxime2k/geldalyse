"""Integration tests: modules must work together on generated and ING data."""

from datetime import date
from pathlib import Path

import pandas as pd

from geldalyse.categorizer import categorize, DEFAULT_CATEGORY
from geldalyse.generator import MERCHANTS, RECURRING, generate_transactions
from geldalyse.merchant import extract_merchant
from geldalyse.reader import read_bank_statement
from geldalyse.schema import STANDARD_COLUMNS

# --- Generated data ---
# les quatre tests du générateur


def test_all_merchants_are_categorized():
    for merchant, (low, high) in MERCHANTS.items():
        assert categorize(merchant, -low) != DEFAULT_CATEGORY, f"{merchant} does not have a category"


def test_all_recurring_labels_are_categorized():
    for _, label, amount in RECURRING:
        assert categorize(label, amount) != DEFAULT_CATEGORY, f"{label} does not have a category"
        

def test_output_generator_columns_match_standard_columns():
    transactions = generate_transactions(start=date(2026, 1, 1), days=10)
    assert list(transactions.columns) == STANDARD_COLUMNS


def test_generator_dates_are_datetime():
    transactions = generate_transactions(start=date(2026, 1, 1), days=10)
    assert pd.api.types.is_datetime64_any_dtype(transactions["date"])


# --- ING data ---
# les trois tests qui lisent la fixture


def test_reader_dates_are_datetime(ing_sample):
    transactions = read_bank_statement(ing_sample)
    assert pd.api.types.is_datetime64_any_dtype(transactions["date"])


def test_reader_output_can_be_categorized(ing_sample):
    transactions = read_bank_statement(ing_sample)
    categories = transactions.apply(lambda row: categorize(row["label"], row["amount"]), axis=1)
    assert categories.notna().all()


def test_reader_output_gives_non_empty_merchant(ing_sample):
    transactions = read_bank_statement(ing_sample)
    merchants = transactions["label"].apply(extract_merchant)
    assert (merchants.str.len() > 0).all()
