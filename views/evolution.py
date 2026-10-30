"""Evolution page: compare a month with its baseline, as key figures and by category."""

import streamlit as st

from components import ALL_TRANSACTIONS_KEY
from geldalyse.analysis import month_range
from geldalyse.formatting import format_month


st.title("Évolution")
st.caption("Suivre l'évolution de vos transactions")

all_transactions = st.session_state[ALL_TRANSACTIONS_KEY]
months = month_range(all_transactions)
default_index = len(months) - 2 if len(months) >= 2 else 0
chosen_month = st.selectbox("Mois", months, index=default_index, format_func=format_month)

