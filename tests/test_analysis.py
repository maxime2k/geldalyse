"""Unit tests for transactions analysis."""

import pandas as pd

from spendlens.analysis import key_figures, expenses_by_category

TRANSACTIONS = pd.DataFrame([
    {"label": "SALAIRE", "amount": 500.0, "category": "REVENUS"},
    {"label": "DELHAIZE", "amount": -30.0, "category": "ALIMENTATION"},
    {"label": "CARREFOUR", "amount": -20.0, "category": "ALIMENTATION"},
    {"label": "CARREFOUR", "amount": -20.0, "category": "ALIMENTATION"},
    {"label": "CARREFOUR", "amount": -100.0, "category": "RETRAIT"},
    {"label": "CARREFOUR", "amount": -10.0, "category": "FACTURE"},
    {"label": "CARREFOUR", "amount": -20.0, "category": "FACTURE"},

])

# --- Key figures ---


def test_income_match_transactions_income():
     income, _, _ = key_figures(transactions=TRANSACTIONS)
     assert income == 500.0


def test_expenses_match_transactions_expenses():
     _, expenses, _ = key_figures(transactions=TRANSACTIONS)
     assert expenses == -200.0


def test_balance_is_the_difference_of_income_and_expenses():
     _, _, balance = key_figures(transactions=TRANSACTIONS)
     assert balance == 300.0


# --- Expenses by category ---


def test_expenses_by_category_are_positive():
     expenses_by_cat = expenses_by_category(transactions=TRANSACTIONS)
     assert (expenses_by_cat["amount"] > 0).all(), "Expenses by category must be positive amounts"


def test_income_not_in_expenses():
     expenses_by_cat = expenses_by_category(transactions=TRANSACTIONS)
     assert "REVENUS" not in expenses_by_cat["category"].tolist()


def test_biggest_expenses_category_is_top():
     expenses_by_cat = expenses_by_category(transactions=TRANSACTIONS)
     assert expenses_by_cat["category"][0] == "RETRAIT"