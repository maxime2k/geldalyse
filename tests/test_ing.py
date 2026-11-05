"""Unit tests for the ing bank statement reader."""

from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from geldalyse.readers.ing import (
    FIXED_NAMES,
    MISSING_LABEL,
    INGReader,
    InvalidStatementError,
    extract_counterparty,
    operation_type,
    parse_amount,
)
from geldalyse.schema import (
    BANK_OPERATION,
    CARD,
    CASH,
    DIRECT_DEBIT,
    OTHER,
    STANDARD_COLUMNS,
    STANDING_ORDER,
    TRANSFER,
)

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
DIRECT_DEBIT_LABEL = "DOMICILIATION EN EUROS VERS: PROXIMUS - XXXX"
STANDING_ORDER_LABEL = (
    "ORDRE PERMANENT VERS: PROPRIÉTAIRE FICTIF - "
    "BE00 0000 0000 0000 COMMUNICATION: LOYER"
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
    transactions = INGReader().read(ing_sample)
    assert list(transactions.columns) == STANDARD_COLUMNS


def test_small_negative_amount_keeps_sign(ing_sample):
    transactions = INGReader().read(ing_sample)
    assert transactions["amount"][3] == -0.5


def test_dates_are_converted(ing_sample):
    transactions = INGReader().read(ing_sample)
    assert transactions["date"][0] == pd.Timestamp(2025, 12, 31)


def test_output_has_no_missing_values(ing_sample):
    transactions = INGReader().read(ing_sample)
    assert not transactions.isna().any().any()


def test_non_ing_file_raises_key_error():
    with pytest.raises(KeyError):
        INGReader().read(WRONG_COLUMNS)


def test_empty_file_raises_empty_data_error():
    with pytest.raises(pd.errors.EmptyDataError):
        INGReader().read(EMPTY_FILE)


def test_header_only_returns_empty_table():
    transactions = INGReader().read(HEADER_ONLY)
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
def test_ing_reader_rejects_invalid_amount(amount):
    with pytest.raises(InvalidStatementError, match="Ligne 2"):
        INGReader().read(ing_csv(amount=amount))


@pytest.mark.parametrize(
    "date",
    ["", "any text", "30/02/2015", "25/01/203", "2026/02/15", "2026-01-03"],
)
def test_ing_reader_rejects_invalid_date(date):
    with pytest.raises(InvalidStatementError, match="Ligne 2"):
        INGReader().read(ing_csv(date=date))


def test_ing_reader_reads_day_first():
    transactions = INGReader().read(ing_csv(date="05/01/2021"))
    assert transactions["date"].iloc[0] == pd.Timestamp(2021, 1, 5)


@pytest.mark.parametrize("label", ["", "   "])
def test_ing_reader_replaces_missing_label(label):
    transactions = INGReader().read(ing_csv(label=label))
    assert transactions["label"].iloc[0] == MISSING_LABEL


# --- Card payments ---


def test_card_payment_returns_third_segment():
    assert extract_counterparty(CARD_PAYMENT, CARD) == "DELHAIZE IXELLES"


def test_card_payment_without_postcode_keeps_full_name():
    # Nothing to remove: the name must stay intact.
    assert extract_counterparty(CARD_PAYMENT_NO_POSTCODE, CARD) == "NETFLIX.COM"


def test_malformed_card_payment_is_returned_unchanged():
    assert extract_counterparty(MALFORMED_CARD_PAYMENT, CARD) == MALFORMED_CARD_PAYMENT


# --- Fixed names ---


def test_cash_withdrawal_returns_fixed_name():
    assert (
        extract_counterparty(CASH_WITHDRAWAL, CASH) == FIXED_NAMES["RETRAIT D'ESPÈCES"]
    )


def test_bank_fees_return_fixed_name():
    assert (
        extract_counterparty(BANK_FEES, BANK_OPERATION)
        == FIXED_NAMES["DÉCOMPTE DE FRAIS"]
    )


def test_interest_returns_fixed_name():
    assert (
        extract_counterparty(INTEREST, BANK_OPERATION) == FIXED_NAMES["INTÉRÊTS-FRAIS"]
    )


# --- Unknown descriptions ---


@pytest.mark.parametrize("label", ["opération diverse", "abc - def"])
def test_unknown_description_is_returned_in_uppercase(label):
    assert extract_counterparty(label, OTHER) == label.upper()


def test_unknown_description_with_segments_is_returned_unchanged():
    assert extract_counterparty(UNKNOWN_WITH_SEGMENTS, OTHER) == UNKNOWN_WITH_SEGMENTS


# --- Direct debits and standing orders ---


def test_direct_debit_returns_creditor():
    assert extract_counterparty(DIRECT_DEBIT_LABEL, DIRECT_DEBIT) == "PROXIMUS"


def test_standing_order_returns_beneficiary():
    assert (
        extract_counterparty(STANDING_ORDER_LABEL, STANDING_ORDER)
        == "PROPRIÉTAIRE FICTIF"
    )


# --- Transfers ---


def test_transfer_received():
    assert extract_counterparty(TRANSFER_RECEIVED, TRANSFER) == "SOCIÉTÉ FICTIVE SA"


def test_transfer_sent():
    assert extract_counterparty(TRANSFER_SENT, TRANSFER) == "AMI FICTIF"


def test_transfer_without_marker_is_returned_unchanged():
    assert (
        extract_counterparty(TRANSFER_WITHOUT_MARKER, TRANSFER)
        == TRANSFER_WITHOUT_MARKER
    )


@pytest.mark.parametrize(
    "label, expected",
    [
        (
            (
                "Paiement Bancontact 04/01/26 - 18h12 - DELHAIZE IXELLES 1050"
                " - BRUXELLES - BEL Numéro de carte 0000 XXXX XXXX 0000"
            ).upper(),
            CARD,
        ),
        (
            (
                "Paiement Debit Mastercard 07/01/26 - 19h35 - PARKING FICTIF 1000"
                " - BRUSSEL - BEL Numéro de carte 0000 XXXX XXXX 0000 Référence ING: XX"
            ).upper(),
            CARD,
        ),
        (
            ("Décompte de frais n° 000000000 Pièce justificative en annexe").upper(),
            BANK_OPERATION,
        ),
        (
            (
                "Ordre permanent Vers: PROPRIÉTAIRE FICTIF"
                " - BE00 0000 0000 0000 Communication: LOYER"
            ).upper(),
            STANDING_ORDER,
        ),
        (
            (
                "Virement instantané: ING app Vers: AMI FICTIF - "
                "BE00 0000 0000 0000 Instantané le 20/02 - 18:30:00 Info personnelle:XX"
            ).upper(),
            TRANSFER,
        ),
        (("Domiciliation en euros Vers: PROXIMUS - XXXX").upper(), DIRECT_DEBIT),
        (("Rectification xxx ").upper(), OTHER),
        (
            (
                "Retrait d'espèces Bancontact 11/02/26 - 14h48 - CASH 1000 - "
                "BRUXELLES - BEL Numéro de carte 0000 XXXX XXXX 0000"
            ).upper(),
            CASH,
        ),
        (
            (
                "Virement en euros (SEPA) De: SOCIÉTÉ FICTIVE SA"
                " - BE00 0000 0000 0000 Communication: SALAIRE JANVIER"
            ).upper(),
            TRANSFER,
        ),
        (("Intérêts-Frais au 31/12/25 Décompte en annexe").upper(), BANK_OPERATION),
    ],
)
def test_operation_type_returns_correct_type(label, expected):
    assert operation_type(label) == expected
