"""Transactions page: uncategorized operations and editable transactions."""

import streamlit as st

from geldalyse.analysis import count_uncategorized, uncategorized_by_operation
from geldalyse.categorizer import EXPENSE_CATEGORIES, SELECTABLE_EXPENSE_CATEGORIES, INCOME_CATEGORY_NAMES
from components import (
    transactions_editor, category_changes, plural, 
    NO_TRANSACTION_MSG, EXPENSE_CHOICES_KEY, INCOME_CHOICES_KEY, period_transactions_or_stop
)




# --- Uncategorized transactions table -------------------------
period_transactions = period_transactions_or_stop()

total_uncategorized = count_uncategorized(period_transactions)
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
 
