"""Geldalyse dashboard: explore bank transactions by category and over time."""

import pandas as pd
from datetime import date

import streamlit as st
import altair as alt

from geldalyse.analysis import key_figures, expenses_by_category, incomes_by_category, monthly_totals, count_uncategorized, uncategorized_by_operation
from geldalyse.categorizer import categorize, DEFAULT_EXPENSE_CATEGORY, EXPENSE_CATEGORIES, apply_manual_categories, SELECTABLE_EXPENSE_CATEGORIES, INCOME_CATEGORY_NAMES
from geldalyse.generator import generate_transactions
from geldalyse.merchant import extract_merchant
from geldalyse.reader import read_bank_statement

st.set_page_config(page_title="Geldalyse")

DEMO_SOURCE = "Données de démo"
UPLOAD_SOURCE = "Importer un relevé ING"
EXPENSE_CHOICES_KEY = "expense_choices"
INCOME_CHOICES_KEY = "income_choices"
NO_TRANSACTION_MSG = "Aucune transaction à afficher. Vérifiez la période sélectionnée ou le contenu de votre relevé."

def details_graph_by_category(total_category: pd.DataFrame) -> alt.Chart:
    base = alt.Chart(total_category).encode(
        x=alt.X("amount", title="Montant (€)"),
        y=alt.Y("category", sort="-x", title=None),
        tooltip=[
            alt.Tooltip("category", title="Catégorie"),
            alt.Tooltip("amount", title="Montant (€)", format=".2f"),
        ],
    )
    bars = base.mark_bar()
    # Light text: the app theme is dark (.streamlit/config.toml).
    labels = base.mark_text(align="left", dx=3, color="#FAFAFA").encode(
        text=alt.Text("amount", format=".2f"),
    )
    return bars + labels


def transactions_editor(
        transactions: pd.DataFrame, 
        options: list[str], 
        key: str, 
        empty_message: str
    ) -> pd.DataFrame:
    """Show an editable transactions table, where only the category can be changed, or a message if there is no transaction."""

    if transactions.empty:
        st.info(empty_message)
        return transactions
    
    return st.data_editor(
        transactions,
        key=key,
        hide_index=True,
        column_order=["date", "merchant", "amount", "category", "label"],
        column_config={
            "date": st.column_config.DateColumn("Date", format="DD/MM/YYYY", width="small"),
            "label": st.column_config.TextColumn("Description"),
            "amount": st.column_config.NumberColumn("Montant", format="%.2f €", width="small"),
            "category": st.column_config.SelectboxColumn("Catégorie", options=sorted(options)),
            "merchant": st.column_config.TextColumn("Opération"),
        },
        disabled=["date", "label", "amount", "merchant"],
    )
    

def category_changes(original: pd.DataFrame, edited: pd.DataFrame) -> dict[str, str]:
    """Return the new category of each operation whose category was changed."""

    changed_rows = edited[edited["category"] != original["category"]]
        
    return dict(zip(changed_rows["merchant"], changed_rows["category"]))


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
    st.warning(NO_TRANSACTION_MSG)
    st.stop()

transactions["category"] = transactions.apply(lambda row: categorize(row["label"], row["amount"]), axis=1)
# Short, readable name shown in the table; the full description is kept too.
transactions["merchant"] = transactions["label"].apply(extract_merchant)

# --- Manual categories by user ---

if EXPENSE_CHOICES_KEY not in st.session_state:
    st.session_state[EXPENSE_CHOICES_KEY] = {}
if INCOME_CHOICES_KEY not in st.session_state:
    st.session_state[INCOME_CHOICES_KEY] = {}

transactions = apply_manual_categories(transactions, st.session_state[EXPENSE_CHOICES_KEY])
transactions = apply_manual_categories(transactions, st.session_state[INCOME_CHOICES_KEY])

# --- Filter by period ---
first_date = transactions["date"].min()
last_date = transactions["date"].max()
period = st.sidebar.date_input("Période", value=(first_date, last_date))
if len(period) != 2:
    st.stop()
start, end = period

in_period = transactions["date"].between(pd.Timestamp(start), pd.Timestamp(end))
transactions = transactions[in_period]

# --- Empty period ---

if transactions.empty:
    st.warning(NO_TRANSACTION_MSG)
    st.stop()

# --- Count uncategorized transactions ---

total_uncategorized = count_uncategorized(transactions)
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
incomes, expenses, balance = key_figures(transactions=transactions)
income_col, expenses_col, balance_col = st.columns(3)
income_col.metric("Entrées", f"{incomes:.2f} €")
expenses_col.metric("Sorties", f"{abs(expenses):.2f} €")
balance_col.metric("Solde", f"{balance:.2f} €")

# --- Transactions details by category ---
expenses_tabs, incomes_tabs = st.tabs([":material/arrow_upward: Sorties par catégorie", ":material/arrow_downward: Entrées par catégorie"])

with expenses_tabs:
    total_expenses_by_category = expenses_by_category(transactions=transactions)
    expenses_details = details_graph_by_category(total_expenses_by_category)
    st.altair_chart(expenses_details, use_container_width=True)

with incomes_tabs:
    total_incomes_by_category = incomes_by_category(transactions=transactions)
    incomes_details = details_graph_by_category(total_incomes_by_category)
    st.altair_chart(incomes_details, use_container_width=True)

st.caption("Les remboursements de magasins sont déduits de leur catégorie de dépense.")

# -- Monthly transactions ---
total_monthly_transactions = monthly_totals(transactions=transactions)
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
    st.subheader("Transactions non catégorisées")
    uncategorized_table = uncategorized_by_operation(transactions=transactions)
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

# --- Transactions table --------------------------------------------------------
# Only the table is filtered: figures and charts keep all categories.
st.subheader("Transactions")
st.caption("Les plus récentes en premier.")

selected = st.multiselect("Catégories ", 
                          options=sorted(transactions["category"].unique())
            )

if not selected:
    shown_transactions = transactions
else:
    shown_transactions = transactions[transactions["category"].isin(selected)]

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
 
