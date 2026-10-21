"""Spendlens dashboard: explore bank transactions by category and over time."""

from datetime import date

import streamlit as st
import altair as alt

from spendlens.categorizer import categorize
from spendlens.generator import generate_transactions
from spendlens.analysis import key_figures, expenses_by_category
from spendlens.reader import read_bank_statement

DEMO_SOURCE = "Données de démo"
UPLOAD_SOURCE = "Importer un relevé ING"

st.title("Spendlens")
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
    transactions = read_bank_statement(uploaded_file)

# Both sources share the standard format, so everything below is source-agnostic.
transactions["category"] = transactions["label"].apply(categorize)

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


# --- Transactions --------------------------------------------------------

st.dataframe(transactions, hide_index=True)