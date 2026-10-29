"""Streamlit display helpers shared by the pages."""

import pandas as pd

import streamlit as st
import altair as alt

PERIOD_TRANSACTIONS_KEY = "period_transactions"
ALL_TRANSACTIONS_KEY = "all_transactions"
NO_TRANSACTION_MSG = "Aucune transaction à afficher. Vérifiez la période sélectionnée ou le contenu de votre relevé."
EXPENSE_CHOICES_KEY = "expense_choices"
INCOME_CHOICES_KEY = "income_choices"

def category_chart(total_category: pd.DataFrame) -> alt.LayerChart:
    """Build a horizontal bar chart of totals by category, biggest first, with amount labels."""

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


def plural(count: int, word: str) -> str:
    """Return the count followed by the word, with an s when the count is above 1."""
    
    return f"{count} {word}s" if count > 1 else f"{count} {word}"

def period_transactions_or_stop() -> pd.DataFrame:
    """Return the transactions of the selected period, or stop the page if there are none."""
    period_transactions = st.session_state[PERIOD_TRANSACTIONS_KEY]
    if period_transactions.empty:
        st.warning(NO_TRANSACTION_MSG)
        st.stop()

    return period_transactions