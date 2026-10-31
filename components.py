"""Streamlit display helpers shared by the pages."""

import pandas as pd

import streamlit as st
import altair as alt

from geldalyse.formatting import (
    format_change, format_amount, NBSP, format_top_variation
)

PERIOD_TRANSACTIONS_KEY = "period_transactions"
ALL_TRANSACTIONS_KEY = "all_transactions"
NO_TRANSACTION_MSG = "Aucune transaction à afficher. Vérifiez la période sélectionnée ou le contenu de votre relevé."
EXPENSE_CHOICES_KEY = "expense_choices"
INCOME_CHOICES_KEY = "income_choices"

TRANSACTIONS_PAGE = "views/transactions.py"
OVERVIEW_PAGE = "views/overview.py"
EVOLUTION_PAGE = "views/evolution.py"
FAVORABLE_COLOR = "#29663D"
UNFAVORABLE_COLOR = "#A73737"
LABEL_COLOR = "#FAFAFA"
LABEL_MARGIN = 0.4  # share of the largest change, left free for the labels


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
    labels = base.mark_text(align="left", dx=3, color=LABEL_COLOR).encode(
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


def page_card(page: str, title: str, icon: str, description: str) -> None:
    """Show a bordered card with a link to a page and a short description."""
    with st.container(border=True):
        st.page_link(page, label=f"**{title}**", icon=icon)
        st.caption(description)


def comparison_metric(
    label: str,
    current_amount: float,
    base_amount: float,
    base_description: str,
    delta_color: str = "normal",
    show_pct: bool = True,
) -> None:
    """Show a key figure of the chosen month with its change from the baseline."""
    change = current_amount - base_amount
    is_stable = round(change, 2) == 0

    if is_stable:
        delta = None
    elif show_pct:
        change_pct = change / base_amount if base_amount != 0 else float("nan")
        delta = format_change(change, change_pct)
    else:
        delta = format_amount(change, signed=True)

    with st.container(border=True):
        st.metric(label, format_amount(current_amount), delta=delta, delta_color=delta_color)
        if is_stable:
            caption = f"Identique à {base_description}."
        else:
            caption = f"{base_description.capitalize()}{NBSP}: {format_amount(base_amount)}"
        st.caption(caption)


def variation_tab(
        variations: pd.DataFrame,
        name: str,
        month_name: str,
        base_description: str, 
        delta_color: str = "normal"
) -> None:
    """Show the top category change for one tab."""

    if variations.empty:
        st.info(f"Pas de {name} ce mois-ci, ni dans la base de comparaison.")
        return
    
    top_variation = variations.iloc[0]
    category = top_variation["category"]
    change = top_variation["change"]

    if round(change, 2) == 0:
            st.info(f"Vos {name} sont identiques dans chaque catégorie.")
            return

    st.markdown(f"**{format_top_variation(category, change)}**")
    st.caption(
        f"{month_name.capitalize()} comparé à {base_description}, par catégorie{NBSP}: "
        "à droite une hausse, à gauche une baisse."
    )
    st.altair_chart(variation_chart(variations, delta_color=delta_color))


def variation_chart(
    variations: pd.DataFrame, delta_color: str = "normal"
) -> alt.LayerChart:
    """Return a diverging bar chart of the category changes."""

    key_variations = variations[variations["change"].round(2) != 0]
    change = key_variations["change"]
    key_variations = key_variations.assign(
        label=change.map(
            lambda value: format_amount(value, signed=True)
        ),
        favorable=(change > 0) if delta_color == "normal" else (change < 0)
    )
    margin = change.abs().max() * LABEL_MARGIN
    low = min(change.min(), 0) - margin
    high = max(change.max(), 0) + margin

    base = alt.Chart(key_variations).encode(
        y=alt.Y("category", title=None, sort=None),
        x=alt.X(
            "change",
            title=None,
            axis=alt.Axis(labels=False, ticks=False),
            scale=alt.Scale(domain=[low, high]),
        ),
    )
    bars = base.mark_bar().encode(
        color=alt.condition(
            alt.datum.favorable,
            alt.value(FAVORABLE_COLOR),
            alt.value(UNFAVORABLE_COLOR),
        )
    )
   
    increase_labels = (
        base.mark_text(align="left", dx=3, color=LABEL_COLOR)
        .encode(text="label")
        .transform_filter(alt.datum.change > 0)
    )
    decrease_labels = (
        base.mark_text(align="right", dx=-3, color=LABEL_COLOR)
        .encode(text="label")
        .transform_filter(alt.datum.change < 0)
    )
    return bars + increase_labels + decrease_labels
    