"""Unit tests for the bank statement reader."""

from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from geldalyse.readers.ing import (
    FIXED_NAMES,
    MISSING_LABEL,
    InvalidStatementError,
    extract_merchant,
    is_received_transfer,
    parse_amount,
    read_bank_statement,
)
from geldalyse.schema import STANDARD_COLUMNS

FIXTURES_DIR = Path(__file__).parent / "fixtures"
WRONG_COLUMNS = FIXTURES_DIR / "wrong_format.csv"
EMPTY_FILE = FIXTURES_DIR / "empty.csv"
HEADER_ONLY = FIXTURES_DIR / "header_only.csv"

CARD_PAYMENT = (
    "PAIEMENT BANCONTACT 04/01/26 - 18H12 - DELHAIZE IXELLES 1050 - BRUXELLES "
    "- BEL NUMÉRO DE CARTE 0000 XXXX XXXX 0000"
)
CARD_PAYMENT_NO_POSTCODE = (
    "PAIEMENT DEBIT MASTERCARD 14/02/26 - 10H00 - NETFLIX.COM - AMSTERDAM "
    "- NLD NUMÉRO DE CARTE 0000 XXXX XXXX 0000 RÉFÉRENCE ING: XXXX"
)
CASH_WITHDRAWAL = (
    "RETRAIT D'ESPÈCES BANCONTACT 11/02/26 - 14H48 - CASH 1000 - BRUXELLES "
    "- BEL NUMÉRO DE CARTE 0000 XXXX XXXX 0000"
)
BANK_FEES = "DÉCOMPTE DE FRAIS N° 000000000 PIÈCE JUSTIFICATIVE EN ANNEXE"
INTEREST = "INTÉRÊTS-FRAIS AU 31/12/25 DÉCOMPTE EN ANNEXE"
TRANSFER_RECEIVED = (
    "VIREMENT EN EUROS (SEPA) DE: SOCIÉTÉ FICTIVE SA - BE00 0000 0000 0000 "
    "COMMUNICATION: SALAIRE JANVIER"
)
TRANSFER_SENT = (
    "VIREMENT INSTANTANÉ: ING APP VERS: AMI FICTIF - BE00 0000 0000 0000 "
    "INSTANTANÉ LE 20/02 - 18:30:00 INFO PERSONNELLE: XXXX"
)

TRANSFER_WITHOUT_MARKER = (
    "VIREMENT INSTANTANÉ: ING APP XXX - BE00 0000 0000 0000 "
    "INSTANTANÉ LE 20/02 - 18:30:00 INFO PERSONNELLE: XXXX"
)
UNKNOWN_WITH_SEGMENTS = "OPÉRATION DIVERSE - RÉFÉRENCE 0000 - TRAITEMENT DU 01/03/26"
MALFORMED_CARD_PAYMENT = "PAIEMENT BANCONTACT SANS DÉTAIL"

HEADER = (
    "Numéro de compte;Nom du compte;Compte contrepartie;Numéro de mouvement;"
    "Date comptable;Date valeur;Montant;Devise;Libellés;Détails du mouvement;Message"
)


def ing_csv(
    amount: str = "-12,50",
    date: str = "03/01/2026",
    label: str = "Retrait d'espèces Bancontact 11/02/26 - 14h48 - CASH 1000 - BRUSSELS",
) -> StringIO:
    """Return an in-memory ING export with one transaction of the given amount."""
    row = f";;;7;12/02/2026;{date};{amount};EUR;{label};;"
    return StringIO(f"{HEADER}\n{row}\n")


def test_output_columns_match(ing_sample):
    transactions = read_bank_statement(ing_sample)
    assert list(transactions.columns) == STANDARD_COLUMNS


def test_small_negative_amount_keeps_sign(ing_sample):
    transactions = read_bank_statement(ing_sample)
    assert transactions["amount"][3] == -0.5


def test_dates_are_converted(ing_sample):
    transactions = read_bank_statement(ing_sample)
    assert transactions["date"][0] == pd.Timestamp(2025, 12, 31)


def test_output_has_no_missing_values(ing_sample):
    transactions = read_bank_statement(ing_sample)
    assert not transactions.isna().any().any()


def test_non_ing_file_raises_key_error():
    with pytest.raises(KeyError):
        read_bank_statement(WRONG_COLUMNS)


def test_empty_file_raises_empty_data_error():
    with pytest.raises(pd.errors.EmptyDataError):
        read_bank_statement(EMPTY_FILE)


def test_header_only_returns_empty_table():
    transactions = read_bank_statement(HEADER_ONLY)
    assert transactions.empty
    assert list(transactions) == STANDARD_COLUMNS


@pytest.mark.parametrize(
    "amount, expected",
    [
        ("1250", 1250.0),
        ("1.350", 1350.0),
        ("-2200", -2200.0),
        ("1 350 480", 1350480.0),
        ("2.480.255", 2480255.0),
        ("12,5", 12.5),
        ("1.235,50", 1235.50),
        ("-1.235,50", -1235.50),
    ],
)
def test_parse_amount_reads_valid_amounts(amount, expected):
    assert parse_amount(amount) == expected


@pytest.mark.parametrize(
    "amount",
    [
        ("abc"),
        ("12.50"),
        (" "),
        (""),
        ("1.25"),
        ("1.25,00"),
        ("1.2345,00"),
        ("12,345"),
        ("12,"),
        ("1,2,3"),
        ("--5"),
    ],
)
def test_parse_amount_rejects_invalid_amounts(amount):
    with pytest.raises(ValueError):
        parse_amount(amount)


@pytest.mark.parametrize("amount", ["abc", "", "12.50"])
def test_read_bank_statement_rejects_invalid_amount(amount):
    with pytest.raises(InvalidStatementError, match="Ligne 2"):
        read_bank_statement(ing_csv(amount=amount))


@pytest.mark.parametrize(
    "date",
    ["", "any text", "30/02/2015", "25/01/203", "2026/02/15", "2026-01-03"],
)
def test_read_bank_statement_rejects_invalid_date(date):
    with pytest.raises(InvalidStatementError, match="Ligne 2"):
        read_bank_statement(ing_csv(date=date))


def test_read_bank_statement_reads_day_first():
    transactions = read_bank_statement(ing_csv(date="05/01/2021"))
    assert transactions["date"].iloc[0] == pd.Timestamp(2021, 1, 5)


@pytest.mark.parametrize("label", ["", "   "])
def test_read_bank_statement_replaces_missing_label(label):
    transactions = read_bank_statement(ing_csv(label=label))
    assert transactions["label"].iloc[0] == MISSING_LABEL


# --- Card payments ---


def test_card_payment_returns_third_segment():
    assert extract_merchant(CARD_PAYMENT) == "DELHAIZE IXELLES"


def test_card_payment_without_postcode_keeps_full_name():
    # Nothing to remove: the name must stay intact.
    assert extract_merchant(CARD_PAYMENT_NO_POSTCODE) == "NETFLIX.COM"


def test_malformed_card_payment_is_returned_unchanged():
    assert extract_merchant(MALFORMED_CARD_PAYMENT) == MALFORMED_CARD_PAYMENT


# --- Fixed names ---


def test_cash_withdrawal_returns_fixed_name():
    assert extract_merchant(CASH_WITHDRAWAL) == FIXED_NAMES["RETRAIT D'ESPÈCES"]


def test_bank_fees_return_fixed_name():
    assert extract_merchant(BANK_FEES) == FIXED_NAMES["DÉCOMPTE DE FRAIS"]


def test_interest_returns_fixed_name():
    assert extract_merchant(INTEREST) == FIXED_NAMES["INTÉRÊTS-FRAIS"]


@pytest.mark.parametrize("prefix, name", FIXED_NAMES.items())
def test_every_fixed_prefix_returns_its_name(prefix, name):
    # Checks that no prefix is shadowed by another one in the dictionary.
    assert extract_merchant(prefix + " ANY FOLLOWING TEXT") == name


# --- Unknown descriptions ---


@pytest.mark.parametrize("label", ["opération diverse", "abc - def"])
def test_unknown_description_is_returned_in_uppercase(label):
    assert extract_merchant(label) == label.upper()


def test_unknown_description_with_segments_is_returned_unchanged():
    assert extract_merchant(UNKNOWN_WITH_SEGMENTS) == UNKNOWN_WITH_SEGMENTS


# --- Transfers ---


def test_transfer_receive():
    assert extract_merchant(TRANSFER_RECEIVED) == "SOCIÉTÉ FICTIVE SA"


def test_transfer_sent():
    assert extract_merchant(TRANSFER_SENT) == "AMI FICTIF"


def test_transfer_without_marker_is_returned_unchanged():
    assert extract_merchant(TRANSFER_WITHOUT_MARKER) == TRANSFER_WITHOUT_MARKER


def test_is_received_transfer_true_for_received_transfer():
    assert is_received_transfer(TRANSFER_RECEIVED)


def test_is_received_transfer_false_for_sent_transfer():
    assert not is_received_transfer(TRANSFER_SENT)


def test_is_received_transfer_false_for_card_payment():
    assert not is_received_transfer(CARD_PAYMENT)
