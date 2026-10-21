"""Integration tests: generated data must match the categorizer, the standard format
    and any output can be categorized
"""

from pathlib import Path
from datetime import date

from spendlens.generator import MERCHANTS, RECURRING, generate_transactions
from spendlens.categorizer import categorize, DEFAULT_CATEGORY
from spendlens.schema import STANDARD_COLUMNS
from spendlens.reader import read_bank_statement

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "ing_export_sample.csv"


def test_all_merchants_are_categorized():
    for merchant in MERCHANTS:
        assert categorize(merchant) != DEFAULT_CATEGORY, f"{merchant} does not have a category"


def test_all_recurring_labels_are_categorized():
    for _, label, _ in RECURRING:
        assert categorize(label) != DEFAULT_CATEGORY, f"{label} does not have a category"
        

def test_output_generator_columns_match_standard_columns():
    transactions = generate_transactions(start=date(2026, 1, 1), days=10)
    assert list(transactions.columns) == STANDARD_COLUMNS


def test_reader_output_can_be_categorized():
    transactions = read_bank_statement(FIXTURE_PATH)
    transactions["category"] = transactions["label"].apply(categorize)
    assert transactions["category"].notna().all()
