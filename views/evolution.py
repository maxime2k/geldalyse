"""Evolution page: compare a month with its baseline, as key figures and by category."""

import streamlit as st

from components import ALL_TRANSACTIONS_KEY, comparison_metric
from geldalyse.analysis import month_range, available_baselines, LAST_THREE_MONTHS, baseline_months, key_figures_variations
from geldalyse.formatting import (
    format_month, BASELINE_LABELS, format_baseline, format_amount
)


st.title("Évolution")
st.caption("Comparez un mois à vos habitudes. Cette page compare des mois entiers : elle n’utilise pas le filtre de période.")

all_transactions = st.session_state[ALL_TRANSACTIONS_KEY]
months = month_range(all_transactions)
default_index = len(months) - 2 if len(months) >= 2 else 0

month_col, baseline_col = st.columns(2)
with month_col:
    chosen_month = st.selectbox("Mois", months, index=default_index, format_func=format_month)

baselines = available_baselines(months, chosen_month)
if not baselines:
    st.info("Pas assez d'historique pour comparer ce mois. Choisissez un mois plus récent.")
    st.stop()

default_baseline_index = baselines.index(LAST_THREE_MONTHS) if LAST_THREE_MONTHS in baselines else 0

with baseline_col:
    chosen_baseline = st.selectbox(
        "Base de comparaison", baselines, index=default_baseline_index, format_func=BASELINE_LABELS.get
    )

months_of_baseline = baseline_months(months, chosen_month, chosen_baseline)
st.caption(f"{format_month(chosen_month).capitalize()}, comparé à {format_baseline(months_of_baseline)}.")


current, baseline = key_figures_variations(all_transactions, chosen_month, months_of_baseline)

current_incomes, current_expenses, current_balance = current
base_incomes, base_expenses, base_balance = baseline
base_description = format_baseline(months_of_baseline)
month_name = format_month(chosen_month)

incomes_col, expenses_col, balance_col = st.columns(3)
with incomes_col:
    comparison_metric(f"Entrées en {month_name}", current_incomes, base_incomes, base_description)
with expenses_col:
    comparison_metric(
        f"Sorties en {month_name}",
        abs(current_expenses),
        abs(base_expenses),
        base_description,
        delta_color="inverse",
    )
with balance_col:
    comparison_metric(f"Solde en {month_name}", current_balance, base_balance, base_description, show_pct=False)