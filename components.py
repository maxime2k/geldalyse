

import pandas as pd
from datetime import date

import streamlit as st
import altair as alt

def category_chart(total_category: pd.DataFrame) -> alt.Chart:
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
