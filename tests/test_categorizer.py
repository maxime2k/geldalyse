"""Unit tests for the keyword-based categorizer."""

import pandas as pd

from geldalyse.categorizer import categorize, DEFAULT_INCOME_CATEGORY, apply_manual_categories, REFUND_CATEGORY


def test_supermarket_is_food():
    assert categorize("DELHAIZE BRUXELLES", -10.0) == "ALIMENTATION"


def test_lowercase_label_is_recognized():
    assert categorize("virement du salaire", 2500.0) == "SALAIRE"


def test_unknown_expense_returns_default_expense():
    assert categorize("delhaize bruxelles", -15.0) == "ALIMENTATION"


def test_unknown_income_returns_default_income():
    assert categorize("nouveau virement", 100.0) == DEFAULT_INCOME_CATEGORY

def test_interest_with_fees_in_label_is_income():
    assert categorize("Intérêts-Frais au 31/12/25 Décompte en annexe", 12.7) == "INVESTISSEMENT"


def test_salary_transfers_returns_salary():
    assert categorize("VIREMENT DE: SOCIETE FICTIVE SA SALAIRE JANVIER", 2500.0) == "SALAIRE"


def test_shop_refund_returns_expense_category():
    assert categorize("REMBOURSEMENT VOTRE ACHAT ZALANDO", 50.0) == "SHOPPING"


def test_received_transfer_returns_refund():
    assert categorize("virement de: ami fictif", 50.0) == REFUND_CATEGORY


def test_apply_manual_categories_changes_chosen_operation():
    transactions = pd.DataFrame([{"merchant": "FRITERIE AS", "category": "INCONNU"}])
    choices = {"FRITERIE AS": "ALIMENTATION"}

    result = apply_manual_categories(transactions, choices)
    
    assert result["category"].iloc[0] == "ALIMENTATION"


def test_apply_manual_categories_keeps_other_operations():
    transactions = pd.DataFrame([
            {"merchant": "FRITERIE AS", "category": "INCONNU"},
            {"merchant": "SOCIETE FICTIVE SA", "category": "REVENUS"}
        ]
    )
    choices = {"FRITERIE AS": "ALIMENTATION"}

    result = apply_manual_categories(transactions, choices)
    societe_fictive = result[result["merchant"] == "SOCIETE FICTIVE SA"]
    
    assert societe_fictive["category"].iloc[0] == "REVENUS"