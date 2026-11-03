"""Read ING exports into the standard format, and parse their descriptions.

Merchant name, by family of description:
- Card payment ("PAIEMENT ..."): 3rd segment between " - ", without postal code
- Cash withdrawal ("RETRAIT D'ESPÈCES ..."): the fixed value "RETRAIT D'ESPÈCES"
- Transfer ("VIREMENT ..."): text between "DE:" or "VERS:" and the next " - "
- Bank operation ("DÉCOMPTE DE FRAIS"): the fixed value "FRAIS COMPTE ING"
- Bank operation ("INTÉRÊTS-FRAIS"): the fixed value "INTÉRÊTS COMPTE ING"
- Anything else: the description, in uppercase

Received transfer: a "VIREMENT ..." description containing "DE:".
"""

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

SEPARATOR = " - "

# Description prefix -> displayed name.
# A prefix must not be the start of another one placed after it.
FIXED_NAMES = {
    "RETRAIT D'ESPÈCES": "RETRAIT D'ESPÈCES",
    "DÉCOMPTE DE FRAIS": "FRAIS COMPTE ING",
    "INTÉRÊTS-FRAIS": "INTÉRÊTS COMPTE ING",
}

TRANSFER_PREFIX = "VIREMENT"
TRANSFER_RECEIVED_MARKER = "DE: "
TRANSFER_SENT_MARKER = "VERS: "
TRANSFER_MARKERS = (TRANSFER_RECEIVED_MARKER, TRANSFER_SENT_MARKER)

CARD_PAYMENT_PREFIX = "PAIEMENT"


class InvalidStatementError(ValueError):
    """Raised when a bank statement has an invalid value."""


def read_bank_statement(path: Path) -> pd.DataFrame:
    """Read an ING export into the standard transaction format.

    Raise InvalidStatementError for an invalid value, and KeyError, ValueError
    or EmptyDataError if the file is not an ING export.
    """
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
            raise InvalidStatementError(f"Ligne {index + 2}. {error}") from error
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
        raise InvalidStatementError(
            f"Ligne {index + 2}. Date invalide : « {dates[index]} »."
        )
    return parsed


def extract_merchant(label: str) -> str:
    """Return a short, readable name for a bank transaction description."""

    # Normalize here too, so the output is uniform whatever the source.
    label = label.upper()

    # 1. Fixed names first: these descriptions have no " - " segments.
    for prefix, name in FIXED_NAMES.items():
        if label.startswith(prefix):
            return name

    # 2. Transfer rule: text between "DE:" or "VERS:" and the next " - "
    if label.startswith(TRANSFER_PREFIX):
        for marker in TRANSFER_MARKERS:
            if marker in label:
                after_marker = label.partition(marker)[2]
                return after_marker.split(SEPARATOR)[0]
        return label

    # 3. Not a card payment: no reliable rule, keep the description.
    if not label.startswith(CARD_PAYMENT_PREFIX):
        return label

    # 4. Card payment: 3rd segment, without the postal code.
    # Spaces matter: city names such as LOUVAIN-LA-NE contain hyphens.
    segments = label.split(SEPARATOR)
    if len(segments) < 3:
        return label
    merchant = segments[2]
    merchant_name = _remove_postal_code(name=merchant)

    return merchant_name


def _remove_postal_code(name: str) -> str:
    """Remove a trailing Belgian postal code (4 digits) from a name."""

    words = name.split()
    if words and words[-1].isdigit() and len(words[-1]) == 4:
        words.pop()

    return " ".join(words)


def is_received_transfer(label: str) -> bool:
    """Return True if the label is a transfer received from someone."""
    label = label.upper()

    return label.startswith(TRANSFER_PREFIX) and TRANSFER_RECEIVED_MARKER in label
