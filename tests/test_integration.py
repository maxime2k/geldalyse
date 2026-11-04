"""Integration tests: modules must work together on generated and ING data."""

from datetime import date
from io import StringIO

import pandas as pd

from geldalyse.categorizer import DEFAULT_EXPENSE_CATEGORY, categorize
from geldalyse.generator import generate_ing_export
from geldalyse.readers import read_statement
from geldalyse.schema import OTHER

# --- Generated data ---


EXPECTED_UNKNOWN = {"BOULANGERIE FICTIVE", "LIBRAIRIE DU COIN"}


def test_only_expected_demo_merchants_are_uncategorized():
    export = generate_ing_export(start=date(2026, 1, 1), days=90)
    transactions = read_statement(StringIO(export))
    merchants = transactions["merchant"]
    categories = transactions.apply(
        lambda row: categorize(row["label"], row["amount"], row["operation_type"]),
        axis=1,
    )
    assert set(merchants[categories == DEFAULT_EXPENSE_CATEGORY]) == EXPECTED_UNKNOWN


def test_export_is_a_valid_ing_statement():
    export = generate_ing_export(start=date(2026, 1, 1), days=90)
    transactions = read_statement(StringIO(export))

    assert len(transactions) == len(export.splitlines()) - 1


def test_demo_transactions_has_no_other_operation_type():
    export = generate_ing_export(start=date(2026, 1, 1), days=90)
    transactions = read_statement(StringIO(export))
    operations = transactions["operation_type"]
    assert OTHER not in operations.tolist()


# --- ING data ---
# les trois tests qui lisent la fixture


def test_reader_dates_are_datetime(ing_sample):
    transactions = read_statement(ing_sample)
    assert pd.api.types.is_datetime64_any_dtype(transactions["date"])


def test_reader_output_can_be_categorized(ing_sample):
    transactions = read_statement(ing_sample)
    categories = transactions.apply(
        lambda row: categorize(row["label"], row["amount"], row["operation_type"]),
        axis=1,
    )
    assert categories.notna().all()


def test_reader_output_gives_non_empty_merchant(ing_sample):
    transactions = read_statement(ing_sample)
    merchants = transactions["merchant"]
    assert (merchants.str.len() > 0).all()
