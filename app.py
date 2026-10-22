"""Geldalyse dashboard: explore bank transactions by category and over time."""

import pandas as pd
from datetime import date

import streamlit as st
import altair as alt

from geldalyse.categorizer import categorize
from geldalyse.generator import generate_transactions
from geldalyse.analysis import key_figures, expenses_by_category, monthly_totals
from geldalyse.reader import read_bank_statement

DEMO_SOURCE = "Données de démo"
UPLOAD_SOURCE = "Importer un relevé ING"

st.title("Geldalyse")
st.write("Comprendre où part son argent.")

# --- Data source ---------------------------------------------------------

st.sidebar.title("Paramètres")
choice = st.sidebar.radio("Source de données", [DEMO_SOURCE, UPLOAD_SOURCE])

if choice == DEMO_SOURCE:
    transactions = generate_transactions(start=date(2026, 1, 1), days=180)
else:
    uploaded_file = st.sidebar.file_uploader("Relevé ING (CSV)", type="csv")
    if uploaded_file is None:
        st.info("Importez un relevé ING pour commencer.")
        st.stop()  # Nothing below can run without data.
        
        #A file in another format must not crash the app.

    try:  
        transactions = read_bank_statement(uploaded_file)
    except (KeyError, ValueError, UnicodeDecodeError, pd.errors.EmptyDataError):
        st.error("Veuillez importer un relevé ING en français, au format CSV")
        st.stop()

# Both sources share the standard format, so everything below is source-agnostic.
if transactions.empty:
    st.warning("Aucune transaction à afficher.")
    st.stop()

transactions["category"] = transactions["label"].apply(categorize)

# --- Filter by period ---
first_date = transactions["date"].min()
last_date = transactions["date"].max()
period = st.sidebar.date_input("Période", value=(first_date, last_date))
if len(period) != 2:
    st.stop()
start, end = period

in_period = transactions["date"].between(pd.Timestamp(start), pd.Timestamp(end))
transactions = transactions[in_period]
# --- Key figures ---------------------------------------------------------
incomes, expenses, balance = key_figures(transactions=transactions)
income_col, expenses_col, balance_col = st.columns(3)
income_col.metric("Revenus", f"{incomes:.2f} €")
expenses_col.metric("Dépenses", f"{abs(expenses):.2f} €")
balance_col.metric("Solde", f"{balance:.2f} €")

# --- Expenses by category ---
total_expenses_by_category = expenses_by_category(transactions=transactions)

# -- graph expenses by category ---
st.subheader("Dépenses par catégorie")
chart = (
    alt.Chart(total_expenses_by_category)                      
    .mark_bar()                              
    .encode(                                 
        x=alt.X("amount", title="Montant"),
        y=alt.Y("category", sort="-x", title=None),
    )
)
st.altair_chart(chart, use_container_width=True)

# -- Monthly transactions ---
total_monthly_transactions = monthly_totals(transactions=transactions)
total_monthly_transactions["flow"] = total_monthly_transactions["flow"].replace({"income": "Revenus", "expense": "Dépenses"})

# -- graph monthly transactions ---
st.subheader("Revenus et dépenses par mois")
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


# --- Transactions table --------------------------------------------------------

st.subheader("Transactions")
st.caption("Les plus récentes en premier.")
st.dataframe(
    transactions.sort_values("date", ascending=False),
    hide_index=True,
    column_config={
        "date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
        "label": st.column_config.TextColumn("Description"),
        "amount": st.column_config.NumberColumn("Montant", format="%.2f €"),
        "category": st.column_config.TextColumn("Catégorie"),
    },
)