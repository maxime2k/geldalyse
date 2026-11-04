"""Overview page: key figures, totals by category and month by month."""

import streamlit as st

from components import (
    EVOLUTION_PAGE,
    TRANSACTIONS_PAGE,
    category_chart,
    monthly_chart,
    page_card,
    period_transactions_or_stop,
)
from geldalyse.analysis import (
    expenses_by_category,
    incomes_by_category,
    key_figures,
    monthly_totals,
)
from geldalyse.formatting import format_amount

period_transactions = period_transactions_or_stop()
# --- Key figures ---------------------------------------------------------
incomes, expenses, balance = key_figures(period_transactions)
income_col, expenses_col, balance_col = st.columns(3)
income_col.metric("Entrées", f"{format_amount(incomes)}", border=True)
expenses_col.metric("Sorties", f"{format_amount(abs(expenses))}", border=True)
balance_col.metric("Solde", f"{format_amount(balance)}", border=True)


left, right = st.columns([3, 2])

# --- Transactions details by category ---
with left:
    expenses_tabs, incomes_tabs = st.tabs(
        [
            ":material/arrow_upward: Sorties par catégorie",
            ":material/arrow_downward: Entrées par catégorie",
        ]
    )
    with expenses_tabs:
        total_expenses_by_category = expenses_by_category(period_transactions)
        expenses_details = category_chart(total_expenses_by_category)
        st.altair_chart(expenses_details, use_container_width=True)
    with incomes_tabs:
        total_incomes_by_category = incomes_by_category(period_transactions)
        incomes_details = category_chart(total_incomes_by_category)
        st.altair_chart(incomes_details, use_container_width=True)

    st.caption(
        "Les remboursements de magasins sont déduits de leur catégorie de dépense."
    )

# -- Monthly transactions ---
total_monthly_transactions = monthly_totals(period_transactions)
total_monthly_transactions["flow"] = total_monthly_transactions["flow"].replace(
    {"income": "Entrées", "expense": "Sorties"}
)

# -- graph monthly transactions ---
st.subheader("Entrées et Sorties par mois")
chart = monthly_chart(total_monthly_transactions)
st.altair_chart(chart, use_container_width=True)


# --- Other analysis pages ---
st.subheader("Aller plus loin")

evolution_col, transactions_col, habits_col = st.columns(3)

with evolution_col:
    page_card(
        page=EVOLUTION_PAGE,
        title="Évolution",
        icon=":material/trending_up:",
        description="Suivre l'évolution de vos transactions",
    )

with transactions_col:
    page_card(
        page=TRANSACTIONS_PAGE,
        title="Transactions",
        icon=":material/list:",
        description="Voir le détail et corriger les catégories",
    )
