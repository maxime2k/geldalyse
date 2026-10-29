"""Overview page: key figures, totals by category and month by month."""

import streamlit as st
import altair as alt

from geldalyse.analysis import key_figures, expenses_by_category, incomes_by_category, monthly_totals, count_uncategorized
from components import category_chart, period_transactions_or_stop, page_card, TRANSACTIONS_PAGE


period_transactions = period_transactions_or_stop()
# --- Key figures ---------------------------------------------------------
incomes, expenses, balance = key_figures(period_transactions)
income_col, expenses_col, balance_col = st.columns(3)
income_col.metric("Entrées", f"{incomes:.2f} €", border=True)
expenses_col.metric("Sorties", f"{abs(expenses):.2f} €", border=True)
balance_col.metric("Solde", f"{balance:.2f} €", border=True)


left, right = st.columns([3, 2])

# --- Transactions details by category ---
with left:
    expenses_tabs, incomes_tabs = st.tabs([":material/arrow_upward: Sorties par catégorie", ":material/arrow_downward: Entrées par catégorie"])
    with expenses_tabs:
        total_expenses_by_category = expenses_by_category(period_transactions)
        expenses_details = category_chart(total_expenses_by_category)
        st.altair_chart(expenses_details, use_container_width=True)
    with incomes_tabs:
        total_incomes_by_category = incomes_by_category(period_transactions)
        incomes_details = category_chart(total_incomes_by_category)
        st.altair_chart(incomes_details, use_container_width=True)

    st.caption("Les remboursements de magasins sont déduits de leur catégorie de dépense.")

# -- Monthly transactions ---
total_monthly_transactions = monthly_totals(period_transactions)
total_monthly_transactions["flow"] = total_monthly_transactions["flow"].replace({"income": "Entrées", "expense": "Sorties"})

# -- graph monthly transactions ---
st.subheader("Entrées et Sorties par mois")
chart = (
    alt.Chart(total_monthly_transactions)
    .mark_bar()
    .encode(
        x=alt.X("month", title="Années-Mois", axis=alt.Axis(labelAngle=0)),
        y=alt.Y("amount", title="Montant (€)"),
        color=alt.Color("flow", title=None),
        xOffset="flow",
    )
)
st.altair_chart(chart, use_container_width=True)


# --- Other analysis pages ---
st.subheader("Aller plus loin")

evolution_col, transactions_col, habits_col = st.columns(3)

with transactions_col:
    page_card(
        page=TRANSACTIONS_PAGE,
        title="Transactions",
        icon=":material/list:",
        description="Voir le détail et corriger les catégories",
    )
