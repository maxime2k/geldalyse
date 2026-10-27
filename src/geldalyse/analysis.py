"""Compute figures and aggregates for the dashboard."""

import numpy as np
import pandas as pd
from datetime import date

from geldalyse.categorizer import DEFAULT_EXPENSE_CATEGORY

# --- Key figures ---------------------------------------------------------

def key_figures(transactions: pd.DataFrame) -> tuple[float, float, float]:
    """Return incomes, expenses and balance. Expenses stay negative."""
    income_rows = transactions[transactions["amount"] > 0]
    expense_rows = transactions[transactions["amount"] < 0]

    incomes = income_rows["amount"].sum()
    expenses = expense_rows["amount"].sum()  # Negative: money going out.
    balance = incomes + expenses
 
    return incomes, expenses, balance

# --- Expenses by category ---

def expenses_by_category(transactions: pd.DataFrame) -> pd.DataFrame:
    """Return total expenses per category, as positive amounts, biggest first."""
    expense_rows = transactions[transactions["amount"] < 0]
    total_expenses_by_category = (
        expense_rows.groupby("category")["amount"]
        .sum()
        .abs()
        .sort_values(ascending=False)
        .reset_index()
    )

    return total_expenses_by_category

# --- Monthly transactions ---


def monthly_totals(transactions: pd.DataFrame) -> pd.DataFrame:
    # Copy: adding a column must not modify the caller's DataFrame.
    transactions_copy = transactions.copy()
    transactions_copy["month"] = transactions_copy["date"].dt.strftime("%Y-%m")
    transactions_copy["flow"] = np.where(transactions_copy["amount"] > 0, "income", "expense")

    total_monthly_transactions = (
        transactions_copy.groupby(["month", "flow"])["amount"]
        .sum()
        .abs()
        .reset_index()
            # "YYYY-MM" strings sort in chronological order.
        .sort_values("month")  # Explicit: groupby already sorts, but the order is intended.
        
    )

    return total_monthly_transactions


def count_uncategorized(transactions:pd.DataFrame) -> int:
        # int(): .sum() returns a NumPy integer, not a Python int.

    return int((transactions["category"] == DEFAULT_EXPENSE_CATEGORY).sum())


def uncategorized_by_operation(transactions: pd.DataFrame) -> pd.DataFrame:
    """Group uncategorized transactions by merchant, most frequent first."""
    uncategorized = transactions[transactions["category"] == DEFAULT_EXPENSE_CATEGORY]
    grouped_uncategorized = (
        uncategorized.groupby("merchant")
        .agg(transaction_count=("amount", "count"), total_amount=("amount", "sum")) 
        .reset_index()
        .sort_values(["transaction_count", "total_amount"], ascending=[False, True])
    )

    return grouped_uncategorized