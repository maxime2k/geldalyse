"""Read bank statement exports and convert them to the Geldalyse standard format."""

from pathlib import Path

import pandas as pd

from geldalyse.schema import STANDARD_COLUMNS

#ING columns to Geldalyse columns
COLUMN_MAPPING = {
    "Date valeur": "date",
    "Description": "label",
    "Montant": "amount",
    
}


def read_bank_statement(path: Path) -> pd.DataFrame:
    """Raise KeyError, ValueError or EmptyDataError if the file is not a valid ING export."""

    df = pd.read_csv(path, sep=";", decimal=",")
    transactions = df[list(COLUMN_MAPPING)]

    # After the selection: account columns are always empty in ING exports.
    # how="all": never drop a row that still has an amount.
    transactions = transactions.dropna(how="all")
    transactions = transactions.rename(columns=COLUMN_MAPPING)

    # Explicit day-first format: 03/01 must be January 3rd, not March 1st.
    transactions["date"] = pd.to_datetime(transactions["date"], format="%d/%m/%Y")
    transactions["label"] = transactions["label"].str.strip().str.upper()

    return transactions[STANDARD_COLUMNS].reset_index(drop=True)
