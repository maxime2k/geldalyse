"""Unit tests for transactions analysis."""

import pandas as pd

from geldalyse.analysis import (
    key_figures, expenses_by_category, incomes_by_category, monthly_totals, 
    count_uncategorized, uncategorized_by_operation, month_range
)

TRANSACTIONS = pd.DataFrame([
    {"date": pd.Timestamp(2026, 3, 10), "label": "INTÉRÊTS-FRAIS EPARGNE", "amount": 100.0, "category": "INVESTISSEMENT"},
    {"date": pd.Timestamp(2026, 3, 15), "label": "SALAIRE", "amount": 500.0, "category": "SALAIRE"},
    {"date": pd.Timestamp(2026, 3, 17), "label": "DELHAIZE", "amount": -30.0, "category": "ALIMENTATION"},
    {"date": pd.Timestamp(2026, 1, 20), "label": "CARREFOUR", "amount": -20.0, "category": "ALIMENTATION"},
    {"date": pd.Timestamp(2026, 1, 15), "label": "CARREFOUR", "amount": -20.0, "category": "ALIMENTATION"},
    {"date": pd.Timestamp(2026, 2, 15), "label": "CARREFOUR", "amount": -100.0, "category": "RETRAITS"},
    {"date": pd.Timestamp(2026, 1, 12), "label": "CARREFOUR", "amount": -10.0, "category": "FACTURE"},
    {"date": pd.Timestamp(2026, 2, 14), "label": "CARREFOUR", "amount": -20.0, "category": "FACTURE"},

])

UNKNOWN_TRANSACTIONS = pd.DataFrame([
    {"date": pd.Timestamp(2026, 3, 15), "label": "SALAIRE DE: SOCIETE FICTIVE SA", "amount": 500.0, "category": "SALAIRE", "merchant": "SOCIETE FICTIVE SA"},
    {"date": pd.Timestamp(2026, 3, 17), "label": "PAIEMENT CARTE - 17/03 10:12 - BOULANGERIE DUPONT 1000", "amount": -30.0, "category": "INCONNU", "merchant": "BOULANGERIE DUPONT"},
    {"date": pd.Timestamp(2026, 1, 20), "label": "PAIEMENT CARTE - 20/03 14:20 - BOULANGERIE DUPONT 1000", "amount": -20.0, "category": "INCONNU", "merchant": "BOULANGERIE DUPONT"},
])

UNCATEGORIZED_TRANSACTIONS = pd.DataFrame([
    {"date": pd.Timestamp(2026, 3, 15), "label": "SALAIRE DE: SOCIETE FICTIVE SA", "amount": 500.0, "category": "SALAIRE", "merchant": "SOCIETE FICTIVE SA"},
    {"date": pd.Timestamp(2026, 3, 17), "label": "PAIEMENT CARTE - 17/03 10:12 - FRITERIE AS 1050", "amount": -35.0, "category": "INCONNU", "merchant": "FRITERIE AS"},
    {"date": pd.Timestamp(2026, 1, 20), "label": "PAIEMENT CARTE - 20/01 14:20 - FRITERIE AS 1050", "amount": -20.0, "category": "INCONNU", "merchant": "FRITERIE AS"},
    {"date": pd.Timestamp(2026, 3, 17), "label": "PAIEMENT CARTE - 17/03 10:12 - BOULANGERIE DUPONT 1000", "amount": -30.0, "category": "INCONNU", "merchant": "BOULANGERIE DUPONT"},
])

# --- Key figures ---


def test_income_match_transactions_income():
     income, _, _ = key_figures(transactions=TRANSACTIONS)
     assert income == 600.0


def test_expenses_match_transactions_expenses():
     _, expenses, _ = key_figures(transactions=TRANSACTIONS)
     assert expenses == -200.0


def test_balance_is_income_plus_expenses():
     _, _, balance = key_figures(transactions=TRANSACTIONS)
     assert balance == 400.0


def test_category_totals_match_balance():
     transactions = pd.DataFrame([
          {"amount": 500.0, "category": "SALAIRE"},
          {"amount": -50.0, "category": "SHOPPING"},
          {"amount": 20.0, "category": "SHOPPING"},
     ])

     _, _, balance = key_figures(transactions)
     incomes_table = incomes_by_category(transactions)
     expenses_table = expenses_by_category(transactions)

     assert incomes_table["amount"].sum() - expenses_table["amount"].sum() == balance


# --- Expenses by category ---


def test_expenses_by_category_are_positive():
     expenses_by_cat = expenses_by_category(transactions=TRANSACTIONS)
     assert (expenses_by_cat["amount"] > 0).all(), "Expenses by category must be positive amounts"


def test_expenses_by_category_excludes_income():
     expenses_by_cat = expenses_by_category(transactions=TRANSACTIONS)
     assert "SALAIRE" not in expenses_by_cat["category"].tolist()


def test_expense_by_category_biggest_first():
     expenses_by_cat = expenses_by_category(transactions=TRANSACTIONS)
     assert expenses_by_cat["category"].iloc[0] == "RETRAITS"


def test_expenses_by_category_deducts_shop_refunds():
    transactions = pd.DataFrame([
        {"category": "SHOPPING", "amount": -500.0},
        {"category": "SHOPPING", "amount": 100.0},
    ])

    result = expenses_by_category(transactions)

    assert result["amount"].iloc[0] == 400.0


# --- Income by category ---

def test_incomes_by_category_excludes_expenses():
     income_by_cat = incomes_by_category(transactions=TRANSACTIONS)
     assert "ALIMENTATION" not in income_by_cat["category"].tolist()


def test_incomes_by_category_biggest_first():
     income_by_cat = incomes_by_category(transactions=TRANSACTIONS)
     assert income_by_cat["category"].iloc[0] == "SALAIRE"


def test_incomes_by_category_excludes_shop_refunds():
     transactions = pd.DataFrame([
          {"amount": 500.0, "category": "SALAIRE"},
          {"amount": 20.0, "category": "SHOPPING"},
     ])

     result = incomes_by_category(transactions)

     assert "SHOPPING" not in result["category"].tolist()
     assert "SALAIRE"  in result["category"].tolist()

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


def test_month_range_includes_months_without_transactions():
    transactions = pd.DataFrame({
        "date": [
            pd.Timestamp(2026, 1, 15),
            pd.Timestamp(2026, 2, 3),
            pd.Timestamp(2026, 4, 28),
        ],
    })

    assert month_range(transactions) == ["2026-01", "2026-02", "2026-03", "2026-04"]