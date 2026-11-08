"""Integration tests: modules must work together on generated and bank data."""

from datetime import date
from io import StringIO

import pytest

from geldalyse.categorizer import (
    DEFAULT_EXPENSE_CATEGORY,
    EXPENSE_CATEGORY_NAMES,
    INCOME_CATEGORY_NAMES,
    categorize,
)
from geldalyse.generator import generate_ing_export
from geldalyse.readers import read_statement
from geldalyse.schema import OTHER
from tests.readers.statements import SAMPLE_STATEMENTS

# --- Generated data ---


EXPECTED_UNKNOWN = {"MAISON LUMEN", "AS DEV SPRL"}


def test_only_expected_demo_counterparties_are_uncategorized():
    export = generate_ing_export(start=date(2026, 1, 1), days=90)
    transactions = read_statement(StringIO(export))
    counterparties = transactions["counterparty"]
    categories = transactions.apply(
        lambda row: categorize(row["label"], row["amount"], row["operation_type"]),
        axis=1,
    )
    assert (
        set(counterparties[categories == DEFAULT_EXPENSE_CATEGORY]) == EXPECTED_UNKNOWN
    )


def test_export_is_a_valid_ing_statement():
    export = generate_ing_export(start=date(2026, 1, 1), days=90)
    transactions = read_statement(StringIO(export))

    assert len(transactions) == len(export.splitlines()) - 1


def test_demo_transactions_has_no_other_operation_type():
    export = generate_ing_export(start=date(2026, 1, 1), days=90)
    transactions = read_statement(StringIO(export))
    operations = transactions["operation_type"]
    assert OTHER not in operations.tolist()


# --- Bank statements ---


@pytest.mark.parametrize("statement", SAMPLE_STATEMENTS)
def test_bank_statement_gets_known_categories(statement):
    transactions = read_statement(statement)
    categories = transactions.apply(
        lambda row: categorize(row["label"], row["amount"], row["operation_type"]),
        axis=1,
    )
    assert set(categories) <= set(INCOME_CATEGORY_NAMES) | set(EXPENSE_CATEGORY_NAMES)
