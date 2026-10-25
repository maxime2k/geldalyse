"""Unit tests for transactions analysis."""

import pandas as pd

from geldalyse.analysis import key_figures, expenses_by_category, monthly_totals, count_uncategorized, uncategorized_by_operation

TRANSACTIONS = pd.DataFrame([
    {"date": pd.Timestamp(2026, 3, 15), "label": "SALAIRE", "amount": 500.0, "category": "REVENUS"},
    {"date": pd.Timestamp(2026, 3, 17), "label": "DELHAIZE", "amount": -30.0, "category": "ALIMENTATION"},
    {"date": pd.Timestamp(2026, 1, 20), "label": "CARREFOUR", "amount": -20.0, "category": "ALIMENTATION"},
    {"date": pd.Timestamp(2026, 1, 15), "label": "CARREFOUR", "amount": -20.0, "category": "ALIMENTATION"},
    {"date": pd.Timestamp(2026, 2, 15), "label": "CARREFOUR", "amount": -100.0, "category": "RETRAIT"},
    {"date": pd.Timestamp(2026, 1, 12), "label": "CARREFOUR", "amount": -10.0, "category": "FACTURE"},
    {"date": pd.Timestamp(2026, 2, 14), "label": "CARREFOUR", "amount": -20.0, "category": "FACTURE"},

])

UNKNOWN_TRANSACTIONS = pd.DataFrame([
    {"date": pd.Timestamp(2026, 3, 15), "label": "SALAIRE DE: SOCIETE FICTIVE SA", "amount": 500.0, "category": "REVENUS", "merchant": "SOCIETE FICTIVE SA"},
    {"date": pd.Timestamp(2026, 3, 17), "label": "PAIEMENT CARTE - 17/03 10:12 - BOULANGERIE DUPONT 1000", "amount": -30.0, "category": "INCONNU", "merchant": "BOULANGERIE DUPONT"},
    {"date": pd.Timestamp(2026, 1, 20), "label": "PAIEMENT CARTE - 20/03 14:20 - BOULANGERIE DUPONT 1000", "amount": -20.0, "category": "INCONNU", "merchant": "BOULANGERIE DUPONT"},
])

UNCATEGORIZED_TRANSACTIONS = pd.DataFrame([
    {"date": pd.Timestamp(2026, 3, 15), "label": "SALAIRE DE: SOCIETE FICTIVE SA", "amount": 500.0, "category": "REVENUS", "merchant": "SOCIETE FICTIVE SA"},
    {"date": pd.Timestamp(2026, 3, 17), "label": "PAIEMENT CARTE - 17/03 10:12 - FRITERIE AS 1050", "amount": -35.0, "category": "INCONNU", "merchant": "FRITERIE AS"},
    {"date": pd.Timestamp(2026, 1, 20), "label": "PAIEMENT CARTE - 20/01 14:20 - FRITERIE AS 1050", "amount": -20.0, "category": "INCONNU", "merchant": "FRITERIE AS"},
    {"date": pd.Timestamp(2026, 3, 17), "label": "PAIEMENT CARTE - 17/03 10:12 - BOULANGERIE DUPONT 1000", "amount": -30.0, "category": "INCONNU", "merchant": "BOULANGERIE DUPONT"},
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

# --- Expenses by month ---


def test_monthly_totals_columns():
     monthly_trans = monthly_totals(TRANSACTIONS)
     assert list(monthly_trans) == ["month", "flow", "amount"]


def test_monthly_expenses_are_summed_per_month():
     monthly_trans = monthly_totals(TRANSACTIONS)
     montly_row = monthly_trans[(monthly_trans["month"] == "2026-01") & (monthly_trans["flow"] == "expense")]
     # January expenses: 20 + 10 + 20 = 50
     assert montly_row["amount"].iloc[0] == 50


def test_monthly_expenses_are_sorted_by_month():
    monthly_trans = monthly_totals(TRANSACTIONS)
    assert monthly_trans["month"].iloc[0] == "2026-01"



def test_count_uncategorized_counts_default_category_rows():
    total_count = count_uncategorized(UNKNOWN_TRANSACTIONS)
    assert total_count == 2


def test_uncategorized_by_operation_excludes_categorized():
     uncategorized = uncategorized_by_operation(UNCATEGORIZED_TRANSACTIONS)

     assert "SOCIETE FICTIVE SA" not in uncategorized["merchant"].tolist()


def test_uncategorized_by_operation_groups_same_merchant():
     uncategorized = uncategorized_by_operation(UNCATEGORIZED_TRANSACTIONS)
     friterie = uncategorized[uncategorized["merchant"] == "FRITERIE AS"]
     assert len(uncategorized) == 2
     assert friterie["transaction_count"].iloc[0]== 2
     assert friterie["total_amount"].iloc[0]== -55.0


def test_uncategorized_by_operation_ties_sorted_by_amount():
    tied_transactions = pd.DataFrame([
        {"category": "INCONNU", "merchant": "BOULANGERIE DUPONT", "amount": -20.0},
        {"category": "INCONNU", "merchant": "FRITERIE AS", "amount": -50.0},
    ])
    uncategorized = uncategorized_by_operation(tied_transactions)
    assert uncategorized["merchant"].iloc[0] == "FRITERIE AS"