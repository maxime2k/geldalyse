"""Integration tests: modules must work together on generated and ING data."""

from datetime import date
from pathlib import Path

import pandas as pd

from geldalyse.categorizer import categorize, DEFAULT_CATEGORY
from geldalyse.generator import MERCHANTS, RECURRING, generate_transactions
from geldalyse.merchant import extract_merchant
from geldalyse.reader import read_bank_statement
from geldalyse.schema import STANDARD_COLUMNS

FIXTURES_DIR = Path(__file__).parent / "fixtures"
ING_SAMPLE = FIXTURES_DIR / "ing_export_sample.csv"

# --- Generated data ---
# les quatre tests du générateur


def test_all_merchants_are_categorized():
    for merchant in MERCHANTS:
        assert categorize(merchant) != DEFAULT_CATEGORY, f"{merchant} does not have a category"


def test_all_recurring_labels_are_categorized():
    for _, label, _ in RECURRING:
        assert categorize(label) != DEFAULT_CATEGORY, f"{label} does not have a category"
        

def test_output_generator_columns_match_standard_columns():
    transactions = generate_transactions(start=date(2026, 1, 1), days=10)
    assert list(transactions.columns) == STANDARD_COLUMNS


def test_generator_dates_are_datetime():
    transactions = generate_transactions(start=date(2026, 1, 1), days=10)
    assert pd.api.types.is_datetime64_any_dtype(transactions["date"])


# --- ING data ---
# les trois tests qui lisent la fixture


def test_reader_dates_are_datetime():
    transactions = read_bank_statement(ING_SAMPLE)
    assert pd.api.types.is_datetime64_any_dtype(transactions["date"])


def test_reader_output_can_be_categorized():
    transactions = read_bank_statement(ING_SAMPLE)
    categories = transactions["label"].apply(categorize)
    assert categories.notna().all()


def test_reader_output_gives_non_empty_merchant():
    transactions = read_bank_statement(ING_SAMPLE)
    merchants = transactions["label"].apply(extract_merchant)
    assert (merchants.str.len() > 0).all()
