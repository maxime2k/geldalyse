"""Compute figures and aggregates for the dashboard."""

import numpy as np
import pandas as pd
from datetime import date

# --- Key figures ---------------------------------------------------------

def key_figures(transactions: pd.DataFrame) -> tuple[float, float, float]:
    income_rows = transactions[transactions["amount"] > 0]
    expense_rows = transactions[transactions["amount"] < 0]

    incomes = income_rows["amount"].sum()
    expenses = expense_rows["amount"].sum()  # Negative: money going out.
    balance = incomes + expenses
 
    return incomes, expenses, balance

# --- Expenses by category ---

def expenses_by_category(transactions: pd.DataFrame) -> pd.DataFrame:
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
    transactions_copy = transactions.copy()
    transactions_copy["month"] = transactions_copy["date"].dt.strftime("%Y-%m")
    transactions_copy["flow"] = np.where(transactions_copy["amount"] > 0, "income", "expense")

    total_monthly_transactions = (
        transactions_copy.groupby(["month", "flow"])["amount"]
        .sum()
        .abs()
        .reset_index()
        .sort_values("month")
        
    )

    return total_monthly_transactions
