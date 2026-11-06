"""Read ING exports into the standard format, and parse their descriptions.

Counterparty, by operation type:
- Card: 3rd " - " segment, without the postal code
- Transfer, direct debit, standing order: text after "DE:" or "VERS:" up to " - "
- Cash, bank operation: a fixed name ("RETRAIT D'ESPÈCES", "FRAIS COMPTE ING"...)
- Anything else: the description, in uppercase
"""

import re

import pandas as pd

from geldalyse.readers import InvalidStatementError
from geldalyse.readers.base import (
    BankReader,
    check_columns,
    clean_labels,
    parse_amounts,
    parse_dates,
)
from geldalyse.schema import (
    BANK_OPERATION,
    CARD,
    CASH,
    CASH_WITHDRAWAL_NAME,
    DIRECT_DEBIT,
    OTHER,
    STANDARD_COLUMNS,
    STANDING_ORDER,
    TRANSFER,
)

ING_OPERATION_TYPES = {
    "PAIEMENT BANCONTACT": CARD,
    "PAIEMENT DEBIT MASTERCARD": CARD,
    "RETRAIT D'ESPÈCES": CASH,
    "VIREMENT EN EUROS": TRANSFER,
    "VIREMENT INSTANTANÉ": TRANSFER,
    "DOMICILIATION": DIRECT_DEBIT,
    "ORDRE PERMANENT": STANDING_ORDER,
    "DÉCOMPTE DE FRAIS": BANK_OPERATION,
    "INTÉRÊTS-FRAIS": BANK_OPERATION,
}
# ING columns to Geldalyse columns
COLUMN_MAPPING = {
    "Date valeur": "date",
    "Libellés": "label",
    "Montant": "amount",
}
AMOUNT_PATTERN = re.compile(r"-?(?:\d{1,3}(?:[. ]\d{3})+|\d+)(?:,\d{1,2})?")


SEPARATOR = " - "

# Description prefix -> displayed name.
# A prefix must not be the start of another one placed after it.
FIXED_NAMES = {
    "RETRAIT D'ESPÈCES": CASH_WITHDRAWAL_NAME,
    "DÉCOMPTE DE FRAIS": "FRAIS COMPTE ING",
    "INTÉRÊTS-FRAIS": "INTÉRÊTS COMPTE ING",
}


TRANSFER_RECEIVED_MARKER = "DE: "
TRANSFER_SENT_MARKER = "VERS: "
TRANSFER_MARKERS = (TRANSFER_RECEIVED_MARKER, TRANSFER_SENT_MARKER)


class INGReader(BankReader):
    """Reader for ING Belgium exports in French, as downloaded from Home'Bank."""

    separator = ";"
    required_columns = list(COLUMN_MAPPING)

    def read(self, file) -> pd.DataFrame:
        """Read an ING export into the standard transaction format.

        Raise InvalidStatementError for an invalid value, and KeyError, ValueError
        or EmptyDataError if the file is not an ING export.
        """
        try:
            df = pd.read_csv(
                file, sep=self.separator, dtype={"Montant": str}, keep_default_na=False
            )
        except pd.errors.EmptyDataError as error:
            raise InvalidStatementError("Le fichier est vide.") from error

        check_columns(df=df, required=self.required_columns)
        transactions = df[self.required_columns]

        # Drop the separator rows (only semicolons): they are not transactions.
        # A row with any value is kept, so a missing amount is still reported.
        transactions = transactions[~transactions.eq("").all(axis=1)]
        transactions = transactions.rename(columns=COLUMN_MAPPING)

        # Explicit day-first format: 03/01 must be January 3rd, not March 1st.
        transactions["date"] = parse_dates(transactions["date"])
        transactions["label"] = clean_labels(transactions["label"])
        transactions["operation_type"] = transactions["label"].map(operation_type)
        transactions["counterparty"] = [
            extract_counterparty(label, operation)
            for label, operation in zip(
                transactions["label"], transactions["operation_type"]
            )
        ]
        transactions["amount"] = parse_amounts(transactions["amount"], convert_amount)

        return transactions[STANDARD_COLUMNS].reset_index(drop=True)


def convert_amount(text: str) -> float:
    """Convert an ING amount like "-1.235,50" to a float, or raise ValueError."""
    if AMOUNT_PATTERN.fullmatch(text) is None:
        raise ValueError(f"Montant invalide : « {text} ».")
    return float(text.replace(".", "").replace(" ", "").replace(",", "."))


def extract_counterparty(label: str, operation_type: str) -> str:
    """Return a short, readable name for a bank transaction description."""
    # Normalize here too, so the output is uniform whatever the source.
    label = label.upper()
    parser = COUNTERPARTY_PARSERS.get(operation_type, _whole_label)
    return parser(label)


def _fixed_counterparty(label: str) -> str:
    """Return the fixed name of a known description, else the label."""
    for prefix, name in FIXED_NAMES.items():
        if label.startswith(prefix):
            return name
    return label


def _counterparty_after_marker(label: str) -> str:
    """Return the text after "DE:" or "VERS:" up to " - ", else the label."""
    for marker in TRANSFER_MARKERS:
        if marker in label:
            after_marker = label.partition(marker)[2]
            return after_marker.split(SEPARATOR)[0]
    return label


def _card_counterparty(label: str) -> str:
    """Return the 3rd segment without its postal code, else the label."""
    segments = label.split(SEPARATOR)
    if len(segments) < 3:
        return label
    counterparty = segments[2]
    counterparty_name = _remove_postal_code(name=counterparty)

    return counterparty_name


def _whole_label(label: str) -> str:
    """Return the label unchanged: its counterparty cannot be told apart."""
    return label


COUNTERPARTY_PARSERS = {
    CARD: _card_counterparty,
    TRANSFER: _counterparty_after_marker,
    DIRECT_DEBIT: _counterparty_after_marker,
    STANDING_ORDER: _counterparty_after_marker,
    CASH: _fixed_counterparty,
    BANK_OPERATION: _fixed_counterparty,
}


def _remove_postal_code(name: str) -> str:
    """Remove a trailing Belgian postal code (4 digits) from a name."""

    words = name.split()
    if words and words[-1].isdigit() and len(words[-1]) == 4:
        words.pop()

    return " ".join(words)


def operation_type(label: str) -> str:
    """Return the operation type of an ING description, or OTHER if it is unknown."""
    for prefix, operation in ING_OPERATION_TYPES.items():
        if label.startswith(prefix):
            return operation
    return OTHER
