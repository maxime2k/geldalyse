from datetime import date

import streamlit as st

from spendlens.categorizer import categorize
from spendlens.generator import generate_transactions
from spendlens.reader import read_bank_statement



DEMO_SOURCE = "Données de démo"
UPLOAD_SOURCE = "Importer un relevé ING"

st.title("Spendlens")
st.write("Comprendre où part son argent.")

st.sidebar.title("Paramètres")
choice = st.sidebar.radio("Source de données", [DEMO_SOURCE, UPLOAD_SOURCE])

if choice == DEMO_SOURCE:
    st.write("Données de démo")
    transactions = generate_transactions(start=date(2026,1,1), days=180)
    
else:
    st.write("Données d'un relevé ING")
    uploaded_file = st.sidebar.file_uploader("Relevé ING", type="csv")

    if uploaded_file is None:
        st.info("Importe un relevé ING pour commencer.")
        st.stop()
    
    transactions = read_bank_statement(uploaded_file)

transactions["category"] = transactions["label"].apply(categorize)
st.dataframe(transactions, hide_index=True)