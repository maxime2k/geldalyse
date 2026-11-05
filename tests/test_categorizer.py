"""Unit tests for the keyword-based categorizer."""

import pandas as pd
import pytest

from geldalyse.categorizer import (
    DEFAULT_EXPENSE_CATEGORY,
    DEFAULT_INCOME_CATEGORY,
    EXPENSE_CATEGORY_NAMES,
    RECEIVED_TRANSFER_CATEGORY,
    apply_manual_categories,
    categorize,
)
from geldalyse.schema import BANK_OPERATION, CARD, CASH, OTHER, TRANSFER


def test_supermarket_is_food():
    assert categorize("DELHAIZE BRUXELLES", -10.0, CARD) == "ALIMENTATION"


def test_lowercase_label_is_recognized():
    assert categorize("virement du salaire", 2500.0, TRANSFER) == "SALAIRE"


def test_unknown_expense_returns_default_expense():
    assert categorize("BOULANGERIE DU COIN", -15.0, CARD) == DEFAULT_EXPENSE_CATEGORY


def test_unknown_income_returns_default_income():
    assert categorize("nouveau virement", 100.0, OTHER) == DEFAULT_INCOME_CATEGORY


def test_positive_interest_is_investment():
    assert (
        categorize(
            "Intérêts-Frais au 31/12/25 Décompte en annexe", 12.7, BANK_OPERATION
        )
        == "INVESTISSEMENT"
    )


def test_negative_interest_is_bank_fee():
    assert (
        categorize(
            "Intérêts-Frais au 31/12/25 Décompte en annexe", -2.7, BANK_OPERATION
        )
        == "FACTURE"
    )


def test_cash_type_is_withdrawal_without_keyword():
    assert categorize("CASH WITHDRAWAL", -50.0, CASH) == "RETRAITS"


def test_bank_operation_type_is_bank_fee_without_keyword():
    assert categorize("FRAIS DE TENUE DE COMPTE", -1.9, BANK_OPERATION) == "FACTURE"


def test_salary_transfers_returns_salary():
    assert (
        categorize("VIREMENT DE: SOCIETE FICTIVE SA SALAIRE JANVIER", 2500.0, TRANSFER)
        == "SALAIRE"
    )


def test_shop_refund_returns_expense_category():
    assert categorize("REMBOURSEMENT VOTRE ACHAT ZALANDO", 50.0, OTHER) == "SHOPPING"


def test_received_transfer_returns_received_transfer_category():
    assert (
        categorize("virement de: ami fictif", 50.0, TRANSFER)
        == RECEIVED_TRANSFER_CATEGORY
    )


def test_apply_manual_categories_changes_chosen_operation():
    transactions = pd.DataFrame(
        [
            {
                "counterparty": "FRITERIE AS",
                "amount": -15.0,
                "category": DEFAULT_EXPENSE_CATEGORY,
            }
        ]
    )
    choices = {"FRITERIE AS": "ALIMENTATION"}

    result = apply_manual_categories(transactions, choices)

    assert result["category"].iloc[0] == "ALIMENTATION"


def test_apply_manual_categories_keeps_other_operations():
    transactions = pd.DataFrame(
        [
            {
                "counterparty": "FRITERIE AS",
                "amount": -15.0,
                "category": DEFAULT_EXPENSE_CATEGORY,
            },
            {
                "counterparty": "SOCIETE FICTIVE SA",
                "amount": 1000.0,
                "category": "SALAIRE",
            },
        ]
    )
    choices = {"FRITERIE AS": "ALIMENTATION"}

    result = apply_manual_categories(transactions, choices)
    societe_fictive = result[result["counterparty"] == "SOCIETE FICTIVE SA"]

    assert societe_fictive["category"].iloc[0] == "SALAIRE"


@pytest.mark.parametrize(
    "chosen, amount, original, expected",
    [
        # Income category on an expense: refused, the expense keeps its category.
        ("SALAIRE", -40.0, DEFAULT_EXPENSE_CATEGORY, DEFAULT_EXPENSE_CATEGORY),
        # Income category on an income: applied.
        ("SALAIRE", 50.0, RECEIVED_TRANSFER_CATEGORY, "SALAIRE"),
        # Expense category on an income: refused, the income keeps its category.
        ("RESTAURATION", 50.0, RECEIVED_TRANSFER_CATEGORY, RECEIVED_TRANSFER_CATEGORY),
        # Expense category on an expense: applied.
        ("RESTAURATION", -40.0, DEFAULT_EXPENSE_CATEGORY, "RESTAURATION"),
    ],
)
def test_apply_manual_categories_respects_money_direction(
    chosen, amount, original, expected
):
    transactions = pd.DataFrame(
        [{"counterparty": "AMI FICTIF", "amount": amount, "category": original}]
    )
    choices = {"AMI FICTIF": chosen}

    result = apply_manual_categories(transactions, choices)

    assert result["category"].iloc[0] == expected


def test_expense_category_names_are_expenses_only():
    assert DEFAULT_EXPENSE_CATEGORY in EXPENSE_CATEGORY_NAMES  # displayed in the table
    assert "ALIMENTATION" in EXPENSE_CATEGORY_NAMES  # an expense category
    assert "SALAIRE" not in EXPENSE_CATEGORY_NAMES  # an income category
