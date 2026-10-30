"""Evolution page: compare a month with its baseline, as key figures and by category."""

import streamlit as st

from components import ALL_TRANSACTIONS_KEY
from geldalyse.analysis import month_range, available_baselines, LAST_THREE_MONTHS, baseline_months
from geldalyse.formatting import format_month, BASELINE_LABELS, format_baseline


st.title("Évolution")
st.caption("Comparez un mois à vos habitudes. Cette page compare des mois entiers : elle n’utilise pas le filtre de période.")

all_transactions = st.session_state[ALL_TRANSACTIONS_KEY]
months = month_range(all_transactions)
default_index = len(months) - 2 if len(months) >= 2 else 0

month_col, baseline_col = st.columns(2)
with month_col:
    chosen_month = st.selectbox("Mois", months, index=default_index, format_func=format_month)

baselines = available_baselines(months, chosen_month)
if not baselines:
    st.info("Pas assez d'historique pour comparer ce mois. Choisissez un mois plus récent.")
    st.stop()

default_baseline_index = baselines.index(LAST_THREE_MONTHS) if LAST_THREE_MONTHS in baselines else 0

with baseline_col:
    chosen_baseline = st.selectbox(
        "Base de comparaison", baselines, index=default_baseline_index, format_func=BASELINE_LABELS.get
    )
    
months_of_baseline = baseline_months(months, chosen_month, chosen_baseline)
st.caption(f"{format_month(chosen_month)}, comparé à {format_baseline(months_of_baseline)}.")