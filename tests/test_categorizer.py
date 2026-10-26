"""Unit tests for the keyword-based categorizer."""

import pandas as pd

from geldalyse.categorizer import categorize, DEFAULT_CATEGORY, apply_manual_categories


def test_supermarket_is_food():
    assert categorize("DELHAIZE BRUXELLES", -10.0) == "ALIMENTATION"


def test_lowercase_label_is_recognized():
    assert categorize("virement du salaire", 2500.0) == "REVENUS"


def test_unknown_label_returns_default():
    assert categorize("pret bancaire", 10000.0) == DEFAULT_CATEGORY


def test_interest_with_fees_in_label_is_income():
    assert categorize("Intérêts-Frais au 31/12/25 Décompte en annexe", 12.7) == "REVENUS"


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