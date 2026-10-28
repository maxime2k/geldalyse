"""Unit tests for the keyword-based categorizer."""

import pandas as pd

import pytest

from geldalyse.categorizer import categorize, DEFAULT_INCOME_CATEGORY, DEFAULT_EXPENSE_CATEGORY, apply_manual_categories, REFUND_CATEGORY, SELECTABLE_EXPENSE_CATEGORIES, INCOME_CATEGORY_NAMES


def test_supermarket_is_food():
    assert categorize("DELHAIZE BRUXELLES", -10.0) == "ALIMENTATION"


def test_lowercase_label_is_recognized():
    assert categorize("virement du salaire", 2500.0) == "SALAIRE"


def test_unknown_expense_returns_default_expense():
    assert categorize("delhaize bruxelles", -15.0) == "ALIMENTATION"


def test_unknown_income_returns_default_income():
    assert categorize("nouveau virement", 100.0) == DEFAULT_INCOME_CATEGORY

def test_positive_interest_is_investment():
    assert categorize("Intérêts-Frais au 31/12/25 Décompte en annexe", 12.7) == "INVESTISSEMENT"


def test_negative_interest_is_bank_fee():
    assert categorize("Intérêts-Frais au 31/12/25 Décompte en annexe", -2.7) == "FACTURE"


def test_salary_transfers_returns_salary():
    assert categorize("VIREMENT DE: SOCIETE FICTIVE SA SALAIRE JANVIER", 2500.0) == "SALAIRE"


def test_shop_refund_returns_expense_category():
    assert categorize("REMBOURSEMENT VOTRE ACHAT ZALANDO", 50.0) == "SHOPPING"


def test_received_transfer_returns_refund():
    assert categorize("virement de: ami fictif", 50.0) == REFUND_CATEGORY


def test_apply_manual_categories_changes_chosen_operation():
    transactions = pd.DataFrame([{"merchant": "FRITERIE AS", "amount": -15.0, "category": DEFAULT_EXPENSE_CATEGORY}])
    choices = {"FRITERIE AS": "ALIMENTATION"}

    result = apply_manual_categories(transactions, choices)
    
    assert result["category"].iloc[0] == "ALIMENTATION"


def test_apply_manual_categories_keeps_other_operations():
    transactions = pd.DataFrame([
            {"merchant": "FRITERIE AS", "amount": -15.0, "category": DEFAULT_EXPENSE_CATEGORY},
            {"merchant": "SOCIETE FICTIVE SA", "amount": 1000.0, "category": "SALAIRE"}
        ]
    )
    choices = {"FRITERIE AS": "ALIMENTATION"}

    result = apply_manual_categories(transactions, choices)
    societe_fictive = result[result["merchant"] == "SOCIETE FICTIVE SA"]
    
    assert societe_fictive["category"].iloc[0] == "SALAIRE"

@pytest.mark.parametrize(
    "chosen, amount, original, expected",
    [
        # Income category on an expense: refused, the expense keeps its category.
        ("SALAIRE", -40.0, DEFAULT_EXPENSE_CATEGORY, DEFAULT_EXPENSE_CATEGORY),
        # Income category on an income: applied.
        ("SALAIRE", 50.0, REFUND_CATEGORY, "SALAIRE"),
        # Expense category on an income: refused, the income keeps its category.
        ("RESTAURATION", 50.0, REFUND_CATEGORY, REFUND_CATEGORY),
        # Expense category on an expense: applied.
        ("RESTAURATION", -40.0, DEFAULT_EXPENSE_CATEGORY, "RESTAURATION"),
    ],
)
def test_apply_manual_categories_respects_money_direction(chosen, amount, original, expected):
    transactions = pd.DataFrame([{"merchant": "AMI FICTIF", "amount": amount, "category": original}])
    choices = {"AMI FICTIF": chosen}

    result = apply_manual_categories(transactions, choices)

    assert result["category"].iloc[0] == expected


def test_selectable_expense_categories_are_expenses_only():
    assert DEFAULT_EXPENSE_CATEGORY not in SELECTABLE_EXPENSE_CATEGORIES
    assert "ALIMENTATION" in SELECTABLE_EXPENSE_CATEGORIES   # une catégorie de sortie
    assert "SALAIRE" not in SELECTABLE_EXPENSE_CATEGORIES   # une catégorie d'entrée