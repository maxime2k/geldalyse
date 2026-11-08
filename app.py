"""Geldalyse entry point: sidebar, data loading and navigation between pages."""

from datetime import date
from io import StringIO

import pandas as pd
import streamlit as st

from components import (
    ALL_TRANSACTIONS_KEY,
    EVOLUTION_PAGE,
    EXPENSE_CHOICES_KEY,
    INCOME_CHOICES_KEY,
    NO_TRANSACTION_MSG,
    OVERVIEW_PAGE,
    PERIOD_TRANSACTIONS_KEY,
    TRANSACTIONS_PAGE,
)
from geldalyse.analysis import count_uncategorized
from geldalyse.categorizer import (
    apply_manual_categories,
    categorize,
)
from geldalyse.generator import generate_ing_export
from geldalyse.readers import InvalidStatementError, read_statement

st.set_page_config(page_title="Geldalyse", layout="wide")

DEMO_SOURCE = "Données de démo"
UPLOAD_SOURCE = "Importer un relevé ING ou Fortis"
INVALID_FILE_MSG = (
    "Ce fichier ne correspond pas à un export ING ou BNP Paribas Fortis. "
    "Téléchargez à nouveau votre relevé depuis votre app bancaire, "
    "sans l’ouvrir ni l’enregistrer dans Excel."
)
INSTALLATION_URL = "https://github.com/maxime2k/geldalyse#installation"

PRIVACY_MSG = (
    "Votre relevé est traité sur les serveurs de Streamlit Cloud, "
    "le temps de la session, puis n’est pas conservé. "
    "Pour que vos données ne quittent pas votre ordinateur, "
    f"utilisez l’application en [local]({INSTALLATION_URL})."
)
st.title("Geldalyse")
st.write("Comprendre où part son argent.")

# --- Data source ---------------------------------------------------------

st.sidebar.title("Paramètres")
choice = st.sidebar.radio("Source de données", [DEMO_SOURCE, UPLOAD_SOURCE])

if choice == DEMO_SOURCE:
    export = generate_ing_export(start=date(2026, 1, 1), days=180)
    all_transactions = read_statement(StringIO(export))

else:
    st.sidebar.warning(f"{PRIVACY_MSG}")
    agree = st.sidebar.checkbox("J'ai compris, importer mon relevé")

    if not agree:
        st.info(
            "Lisez l’avertissement ci-contre, puis cochez la case "
            "avant d'importer votre fichier."
        )
        st.stop()

    uploaded_file = st.sidebar.file_uploader("Relevé ING ou Fortis (CSV)", type="csv")
    if uploaded_file is None:
        st.info("Importez un relevé ING ou Fortis pour commencer.")
        st.stop()  # Nothing below can run without data.

        # A file in another format must not crash the app.

    try:
        all_transactions = read_statement(uploaded_file)
    except InvalidStatementError as error:
        st.error(INVALID_FILE_MSG)
        st.caption(str(error))
        st.stop()
    except (KeyError, ValueError, UnicodeDecodeError, pd.errors.EmptyDataError):
        st.error(INVALID_FILE_MSG)
        st.stop()

# Both sources share the standard format, so everything below is source-agnostic.
if all_transactions.empty:
    st.warning(NO_TRANSACTION_MSG)
    st.stop()

all_transactions["category"] = all_transactions.apply(
    lambda row: categorize(row["label"], row["amount"], row["operation_type"]), axis=1
)

# --- Manual categories by user ---

if EXPENSE_CHOICES_KEY not in st.session_state:
    st.session_state[EXPENSE_CHOICES_KEY] = {}
if INCOME_CHOICES_KEY not in st.session_state:
    st.session_state[INCOME_CHOICES_KEY] = {}

all_transactions = apply_manual_categories(
    all_transactions, st.session_state[EXPENSE_CHOICES_KEY]
)
all_transactions = apply_manual_categories(
    all_transactions, st.session_state[INCOME_CHOICES_KEY]
)

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

page = st.navigation(
    [
        st.Page(
            OVERVIEW_PAGE,
            title="Vue d'ensemble",
            icon=":material/dashboard:",
            default=True,
        ),
        st.Page(EVOLUTION_PAGE, title="Évolution", icon=":material/trending_up:"),
        st.Page(TRANSACTIONS_PAGE, title="Transactions", icon=":material/list:"),
    ]
)

# After st.navigation: page links need the pages to be declared.
# Before page.run(): a page that calls st.stop() must not hide the indicator.
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
        st.page_link(
            TRANSACTIONS_PAGE, label="Les classer", icon=":material/arrow_forward:"
        )


page.run()
