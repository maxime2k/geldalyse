"""Reader for BNP Paribas Fortis CSV exports.

Only accepted transactions are kept. Amounts use a point or a comma as
decimal separator, without thousands separator.

Counterparty:
- the "Nom de la contrepartie" column, when it is filled;
- card payment: the merchant, without store number or location;
- cash withdrawal: a fixed name;
- anything else: the description, in uppercase.
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
    CARD,
    CASH,
    CASH_WITHDRAWAL_NAME,
    DIRECT_DEBIT,
    OTHER,
    STANDARD_COLUMNS,
    STANDING_ORDER,
    TRANSFER,
)

# Fortis columns to Geldalyse columns
COLUMN_MAPPING = {
    "Date valeur": "date",
    "Détails": "label",
    "Montant": "amount",
    "Type de transaction": "operation_type",
    "Nom de la contrepartie": "counterparty",
}
STATUS_COLUMN = "Statut"
ACCEPTED_STATUS = "Accepté"
REQUIRED_COLUMNS = [*COLUMN_MAPPING, STATUS_COLUMN]

AMOUNT_PATTERN = re.compile(r"-?\d+(?:[.,]\d{1,2})?")

FORTIS_OPERATION_TYPES = {
    "PAIEMENT PAR CARTE": CARD,
    "RETRAIT D'ESPÈCES PAR CARTE": CASH,
    "VIREMENT EN EUROS": TRANSFER,
    "VIREMENT INSTANTANÉ EN EUROS": TRANSFER,
    "DOMICILIATION": DIRECT_DEBIT,
    "ORDRE PERMANENT": STANDING_ORDER,
}
CARD_PATTERN = re.compile(r"NUMERO \d{4} XXXX XXXX \d{4} (.+?) \d{2}/\d{2}/\d{4}")
POSTAL_CODE_PATTERN = re.compile(r"(.+?) \d{4}\b")
STORE_NUMBER_PATTERN = re.compile(r"^\d{4} ")


class FortisReader(BankReader):
    def read(self, file) -> pd.DataFrame:
        """Read a Fortis export into the standard transaction format.

        Raise InvalidStatementError for an invalid value, and KeyError, ValueError
        or EmptyDataError if the file is not an ING export.
        """
        try:
            df = pd.read_csv(file, sep=";", dtype=str, keep_default_na=False)
        except pd.errors.EmptyDataError as error:
            raise InvalidStatementError("Le fichier est vide") from error

        check_columns(df=df, required=REQUIRED_COLUMNS)
        all_transactions = df[REQUIRED_COLUMNS]
        accepted_transactions = all_transactions[
            all_transactions[STATUS_COLUMN] == ACCEPTED_STATUS
        ]
        transactions = accepted_transactions.rename(columns=COLUMN_MAPPING)
        transactions["label"] = clean_labels(transactions["label"])
        transactions["amount"] = parse_amounts(transactions["amount"], convert_amount)
        transactions["date"] = parse_dates(transactions["date"])
        transactions["operation_type"] = transactions["operation_type"].map(
            operation_type
        )
        transactions["counterparty"] = [
            extract_counterparty(name, operation_type, label)
            for name, operation_type, label in zip(
                transactions["counterparty"],
                transactions["operation_type"],
                transactions["label"],
            )
        ]
        return transactions[STANDARD_COLUMNS].reset_index(drop=True)


def convert_amount(text: str) -> float:
    """Convert a Fortis amount like "-1235,50" to a float, or raise ValueError."""

    if AMOUNT_PATTERN.fullmatch(text) is None:
        raise ValueError(f"Le montant est invalide : {text}")

    return float(text.replace(",", "."))


def operation_type(text: str) -> str:
    """Return the operation type based on a Fortis transaction type,
    or OTHER if unknown."""
    return FORTIS_OPERATION_TYPES.get(text.upper(), OTHER)


def extract_counterparty(name: str, operation_type: str, label: str) -> str:
    """Return a readable counterparty name, or the description if none is found."""
    name = name.strip().upper()
    if name:
        return name
    if operation_type == CASH:
        return CASH_WITHDRAWAL_NAME
    if operation_type == CARD:
        return _card_counterparty(label)

    return label


def _card_counterparty(label: str) -> str:
    """Return the merchant of a card payment, without store number or location."""
    match = CARD_PATTERN.search(label)
    if match is None:
        return label
    merchant = re.sub(STORE_NUMBER_PATTERN, "", match.group(1))
    counterparty = POSTAL_CODE_PATTERN.search(merchant)
    return merchant if counterparty is None else counterparty.group(1)
