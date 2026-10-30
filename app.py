"""Geldalyse entry point: sidebar, data loading and navigation between pages."""

import pandas as pd
from datetime import date

import streamlit as st

from geldalyse.analysis import count_uncategorized
from geldalyse.categorizer import categorize, DEFAULT_EXPENSE_CATEGORY, apply_manual_categories
from components import (
    PERIOD_TRANSACTIONS_KEY, NO_TRANSACTION_MSG, EXPENSE_CHOICES_KEY, 
    INCOME_CHOICES_KEY, ALL_TRANSACTIONS_KEY, PERIOD_TRANSACTIONS_KEY, TRANSACTIONS_PAGE,
    OVERVIEW_PAGE, EVOLUTION_PAGE
)
from geldalyse.generator import generate_transactions
from geldalyse.merchant import extract_merchant
from geldalyse.reader import read_bank_statement

st.set_page_config(page_title="Geldalyse", layout="wide")

DEMO_SOURCE = "Données de démo"
UPLOAD_SOURCE = "Importer un relevé ING"

st.title("Geldalyse")
st.write("Comprendre où part son argent.")

# --- Data source ---------------------------------------------------------

st.sidebar.title("Paramètres")
choice = st.sidebar.radio("Source de données", [DEMO_SOURCE, UPLOAD_SOURCE])

if choice == DEMO_SOURCE:
    all_transactions = generate_transactions(start=date(2026, 1, 1), days=180)
else:
    uploaded_file = st.sidebar.file_uploader("Relevé ING (CSV)", type="csv")
    if uploaded_file is None:
        st.info("Importez un relevé ING pour commencer.")
        st.stop()  # Nothing below can run without data.
        
        #A file in another format must not crash the app.

    try:  
        all_transactions = read_bank_statement(uploaded_file)
    except (KeyError, ValueError, UnicodeDecodeError, pd.errors.EmptyDataError):
        st.error("Veuillez importer un relevé ING en français, au format CSV")
        st.stop()

# Both sources share the standard format, so everything below is source-agnostic.
if all_transactions.empty:
    st.warning(NO_TRANSACTION_MSG)
    st.stop()

all_transactions["category"] = all_transactions.apply(lambda row: categorize(row["label"], row["amount"]), axis=1)
# Short, readable name shown in the table; the full description is kept too.
all_transactions["merchant"] = all_transactions["label"].apply(extract_merchant)

# --- Manual categories by user ---

if EXPENSE_CHOICES_KEY not in st.session_state:
    st.session_state[EXPENSE_CHOICES_KEY] = {}
if INCOME_CHOICES_KEY not in st.session_state:
    st.session_state[INCOME_CHOICES_KEY] = {}

all_transactions = apply_manual_categories(all_transactions, st.session_state[EXPENSE_CHOICES_KEY])
all_transactions = apply_manual_categories(all_transactions, st.session_state[INCOME_CHOICES_KEY])

# --- Filter by period ---
first_date = all_transactions["date"].min()
last_date = all_transactions["date"].max()
period = st.sidebar.date_input("Période", value=(first_date, last_date))
if len(period) != 2:
    st.stop()
start, end = period

in_period = all_transactions["date"].between(pd.Timestamp(start), pd.Timestamp(end))
period_transactions = all_transactions[in_period]

# --- save all and period transactions in the user session ---

st.session_state[ALL_TRANSACTIONS_KEY] = all_transactions
st.session_state[PERIOD_TRANSACTIONS_KEY] = period_transactions

page = st.navigation([
    st.Page(OVERVIEW_PAGE, title="Vue d'ensemble", icon=":material/dashboard:", default=True),
    st.Page(EVOLUTION_PAGE, title="Évolution", icon=":material/trending_up:"),
    st.Page(TRANSACTIONS_PAGE, title="Transactions", icon=":material/list:"),
])
page.run()


# --- Count uncategorized transactions ---

total_uncategorized = count_uncategorized(period_transactions)
if total_uncategorized == 0:
    st.sidebar.success("Toutes vos transactions sont dans une catégorie.")
else:
    message = (
    f"{total_uncategorized} transactions non catégorisées."
    if total_uncategorized > 1
    else "Une transaction n'a pas de catégorie."
    )
    with st.sidebar.container(border=True):
        st.warning(message)
        st.page_link(TRANSACTIONS_PAGE, label="Les classer", icon=":material/arrow_forward:")