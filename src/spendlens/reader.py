"""Read bank statement exports and convert them to the Spendlens standard format."""

from pathlib import Path

import pandas as pd

from spendlens.schema import STANDARD_COLUMNS

COLUMN_MAPPING = {
    "Date valeur": "date",
    "Description": "label",
    "Montant": "amount",
    
}


def read_bank_statement(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";", decimal=",")
    transactions = df[list(COLUMN_MAPPING)]
    transactions = transactions.rename(columns=COLUMN_MAPPING)
    transactions["date"] = pd.to_datetime(transactions["date"], format="%d/%m/%Y")
    transactions["label"] = transactions["label"].str.strip().str.upper()

    return transactions[STANDARD_COLUMNS]
