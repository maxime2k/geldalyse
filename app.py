"""Geldalyse dashboard: explore bank transactions by category and over time."""

import pandas as pd
from datetime import date

import streamlit as st
import altair as alt

from geldalyse.analysis import key_figures, expenses_by_category, incomes_by_category, monthly_totals, count_uncategorized, uncategorized_by_operation
from geldalyse.categorizer import categorize, DEFAULT_EXPENSE_CATEGORY, EXPENSE_CATEGORIES, apply_manual_categories, SELECTABLE_EXPENSE_CATEGORIES, INCOME_CATEGORY_NAMES
from components import category_chart, transactions_editor, category_changes, plural
from geldalyse.generator import generate_transactions
from geldalyse.merchant import extract_merchant
from geldalyse.reader import read_bank_statement

st.set_page_config(page_title="Geldalyse")

DEMO_SOURCE = "Données de démo"
UPLOAD_SOURCE = "Importer un relevé ING"
EXPENSE_CHOICES_KEY = "expense_choices"
INCOME_CHOICES_KEY = "income_choices"
NO_TRANSACTION_MSG = "Aucune transaction à afficher. Vérifiez la période sélectionnée ou le contenu de votre relevé."




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

# --- Empty period ---

if period_transactions.empty:
    st.warning(NO_TRANSACTION_MSG)
    st.stop()


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
    st.sidebar.warning(message)
    st.sidebar.caption(f"Filtrez le tableau sur {DEFAULT_EXPENSE_CATEGORY} pour les afficher.")

# --- Key figures ---------------------------------------------------------
incomes, expenses, balance = key_figures(period_transactions)
income_col, expenses_col, balance_col = st.columns(3)
income_col.metric("Entrées", f"{incomes:.2f} €")
expenses_col.metric("Sorties", f"{abs(expenses):.2f} €")
balance_col.metric("Solde", f"{balance:.2f} €")

# --- Transactions details by category ---
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

# --- Uncategorized transactions table -------------------------

if total_uncategorized > 0:
    st.subheader("Transactions non catégorisées, par opération")
    uncategorized_table = uncategorized_by_operation(period_transactions)
    uncategorized_table["category"] = None
    edited_table = st.data_editor(
                            uncategorized_table,
                            hide_index=True,
                            placeholder = "Choisir une catégorie",
                            column_config={
                                "merchant": st.column_config.TextColumn("Opération"),
                                "transaction_count": st.column_config.NumberColumn("Transactions"),
                                "total_amount": st.column_config.NumberColumn("Total", format="%.2f €"),
                                "category": st.column_config.SelectboxColumn("Catégorie", options=sorted(EXPENSE_CATEGORIES)),
                            },
                            disabled=["merchant", "transaction_count", "total_amount"]
                        )
    chosen_rows = edited_table[edited_table["category"].notna()]
    new_choices = dict(zip(chosen_rows["merchant"], chosen_rows["category"]))
    if new_choices:
        st.session_state[EXPENSE_CHOICES_KEY].update(new_choices)
        st.rerun()
    
    st.caption(
        f"{plural(total_uncategorized, 'transaction')} regroupées en {plural(len(uncategorized_table), 'opération')}"
        if total_uncategorized > 1
        else "1 transaction"
    )

# --- All transactions table --------------------------------------------------------
# Only the table is filtered: figures and charts keep all categories.
st.subheader("Transactions")
st.caption("Les plus récentes en premier.")

selected = st.multiselect("Catégories ", 
                          options=sorted(period_transactions["category"].unique())
            )

if not selected:
    shown_transactions = period_transactions
else:
    shown_transactions = period_transactions[period_transactions["category"].isin(selected)]

sorted_transactions = shown_transactions.sort_values("date", ascending=False)
expenses_transactions = sorted_transactions[sorted_transactions["amount"] <= 0]
incomes_transactions = sorted_transactions[sorted_transactions["amount"] > 0]


expenses_msg = (
    "Aucune sortie pour la période et les catégories sélectionnées. Les résultats sont dans l'onglet Entrées."
    if not incomes_transactions.empty
    else NO_TRANSACTION_MSG
)
income_msg = (
    "Aucune entrée pour la période et les catégories sélectionnées. Les résultats sont dans l'onglet Sorties."
    if not expenses_transactions.empty
    else NO_TRANSACTION_MSG
)

with st.form("transactions"):
   expenses_transactions_tab, incomes_transactions_tab = st.tabs([
       f"Sorties ({len(expenses_transactions)})", 
       f"Entrées ({len(incomes_transactions)})"
    ])
   with expenses_transactions_tab:
    edited_expenses = transactions_editor(
        expenses_transactions, SELECTABLE_EXPENSE_CATEGORIES, "expenses_editor", expenses_msg
    )

   with incomes_transactions_tab:
    edited_incomes = transactions_editor(
        incomes_transactions, INCOME_CATEGORY_NAMES, "incomes_editor", income_msg
    )

   submitted = st.form_submit_button("Enregistrer les modifications")
st.caption("Cliquez sur une catégorie pour la modifier, puis enregistrez. Un changement s’applique à toutes les transactions de cette opération.")

if submitted:
    expense_changes = category_changes(expenses_transactions, edited_expenses)
    income_changes = category_changes(incomes_transactions, edited_incomes)

    if expense_changes or income_changes:
        st.session_state[EXPENSE_CHOICES_KEY].update(expense_changes)
        st.session_state[INCOME_CHOICES_KEY].update(income_changes)

        st.rerun()
 
