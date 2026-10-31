"""Compute figures and aggregates for the dashboard."""

from collections.abc import Callable

import numpy as np
import pandas as pd
from datetime import date

from geldalyse.categorizer import DEFAULT_EXPENSE_CATEGORY, EXPENSE_CATEGORY_NAMES, INCOME_CATEGORY_NAMES

PREVIOUS_MONTH = "previous_month"
LAST_THREE_MONTHS = "last_three_months"
SAME_MONTH_LAST_YEAR = "same_month_last_year"

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
    expense_rows = transactions[transactions["category"].isin(EXPENSE_CATEGORY_NAMES)]
    expense_rows = expense_rows.assign(amount=-expense_rows["amount"])
  
    return _totals_by_category(expense_rows)


def incomes_by_category(transactions: pd.DataFrame) -> pd.DataFrame:
    """Return total incomes per category, biggest first."""
    income_rows = transactions[transactions["category"].isin(INCOME_CATEGORY_NAMES)]

    return _totals_by_category(income_rows)


def _totals_by_category(rows: pd.DataFrame) -> pd.DataFrame:
    """Return total amount per category, biggest first."""
    total = (
        rows.groupby("category")["amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    return total

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


def month_range(transactions: pd.DataFrame) -> list[str]:
    """Return the list of months, enven if, there are no transactions"""
    date_range = pd.period_range(transactions["date"].min(), transactions["date"].max(), freq="M")
    
    return date_range.strftime("%Y-%m").tolist()


def available_baselines(months: list[str], chosen_month: str) -> list[str]:
    """Return the baselines the history allows for the chosen month, shortest first."""
    month_index = months.index(chosen_month)

    baselines = []
    if month_index >= 1:
        baselines.append(PREVIOUS_MONTH)
    if month_index >= 3:
        baselines.append(LAST_THREE_MONTHS)
    if month_index >= 12:
        baselines.append(SAME_MONTH_LAST_YEAR)
    return baselines


def baseline_months(months: list[str], chosen_month: str, baseline: str) -> list[str]:
    """Return the months that make up the baseline of the chosen month."""

    month_index = months.index(chosen_month)

    if baseline == PREVIOUS_MONTH:
        return [months[month_index - 1]]
    if baseline == LAST_THREE_MONTHS:
        return months[month_index - 3:month_index]
    if baseline == SAME_MONTH_LAST_YEAR:
        return [months[month_index - 12]]
    
    raise ValueError(f"Unknown baseline: {baseline}")
    

def category_variations(
    
    transactions: pd.DataFrame,
    chosen_month: str,
    months_of_baseline: list[str],
    totals_by_category: Callable[[pd.DataFrame], pd.DataFrame],
) -> pd.DataFrame:
    """Compare the totals by category of the chosen month with the average of its baseline months."""

    rows = _month_rows(transactions, [chosen_month])
    current = totals_by_category(rows).rename(columns={"amount": "current"})

    baseline = totals_by_category(_month_rows(transactions, months_of_baseline))
    baseline = baseline.assign(amount=baseline["amount"] / len(months_of_baseline))
    baseline = baseline.rename(columns={"amount": "baseline"})
   
    variations = current.merge(baseline, on="category", how="outer").fillna(0)
    variations = variations.assign(change=variations["current"] - variations["baseline"])
    variations = variations.assign(change_pct=variations["change"] / variations["baseline"].where(variations["baseline"] != 0))

    return ( 
        variations.sort_values("change", key=abs, ascending=False)
            .reset_index(drop=True)
    )


def _month_rows(transactions: pd.DataFrame, months: list[str]) -> pd.DataFrame:
    """Return the transactions whose month, formatted as YYYY-MM, is in months."""

    month = transactions["date"].dt.strftime("%Y-%m")

    return transactions[month.isin(months)]


def key_figures_variations(
    transactions: pd.DataFrame,
    chosen_month: str,
    months_of_baseline: list[str],
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Return the key figures of the chosen month and the average key figures of its baseline months."""

    current_key_figures = key_figures(_month_rows(transactions, [chosen_month]))
    baseline_totals = key_figures(_month_rows(transactions, months_of_baseline))
    baseline_key_figures = tuple(value / len(months_of_baseline) for value in baseline_totals)

    return current_key_figures, baseline_key_figures