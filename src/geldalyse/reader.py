"""Read bank statement exports and convert them to the Geldalyse standard format."""

import re
from pathlib import Path

import pandas as pd

from geldalyse.schema import STANDARD_COLUMNS

# ING columns to Geldalyse columns
COLUMN_MAPPING = {
    "Date valeur": "date",
    "Libellés": "label",
    "Montant": "amount",
}
AMOUNT_PATTERN = re.compile(r"-?(?:\d{1,3}(?:[. ]\d{3})+|\d+)(?:,\d{1,2})?")
MISSING_LABEL = "SANS DESCRIPTION"


def read_bank_statement(path: Path) -> pd.DataFrame:
    """Raise KeyError, ValueError, EmptyDataError if the file is invalid ING export."""

    df = pd.read_csv(path, sep=";", dtype={"Montant": str}, keep_default_na=False)
    transactions = df[list(COLUMN_MAPPING)]

    # Drop the separator rows (only semicolons): they are not transactions.
    # A row with any value is kept, so a missing amount is still reported.
    transactions = transactions[~transactions.eq("").all(axis=1)]
    transactions = transactions.rename(columns=COLUMN_MAPPING)

    # Explicit day-first format: 03/01 must be January 3rd, not March 1st.
    transactions["date"] = _parse_dates(transactions["date"])
    transactions["label"] = transactions["label"].str.strip().str.upper()
    transactions["label"] = transactions["label"].replace("", MISSING_LABEL)

    transactions["amount"] = _parse_amounts(transactions["amount"])

    return transactions[STANDARD_COLUMNS].reset_index(drop=True)


def _parse_amounts(amounts: pd.Series) -> pd.Series:
    """Parse each amount, or raise ValueError with its line in the file."""
    values = []
    for index, text in amounts.items():
        try:
            values.append(parse_amount(text))
        except ValueError as error:
            raise ValueError(f"Ligne {index + 2}. {error}") from error
    return pd.Series(values, index=amounts.index)


def parse_amount(text: str) -> float:
    """Convert an ING amount like "-1.235,50" to a float, or raise ValueError."""
    if AMOUNT_PATTERN.fullmatch(text) is None:
        raise ValueError(f"Montant invalide : « {text} ».")
    return float(text.replace(".", "").replace(" ", "").replace(",", "."))


def _parse_dates(dates: pd.Series) -> pd.Series:
    """Parse each day-first date, or raise ValueError with its line in the file."""
    # Explicit day-first format: 03/01 must be January 3rd, not March 1st.
    parsed = pd.to_datetime(dates, format="%d/%m/%Y", errors="coerce")
    invalid = parsed.isna()
    if invalid.any():
        index = invalid.idxmax()
        raise ValueError(f"Ligne {index + 2}. Date invalide : « {dates[index]} ».")
    return parsed
