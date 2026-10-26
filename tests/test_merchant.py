"""Unit tests for merchant name extraction.

Descriptions come from the ING fixture, in uppercase as produced by the reader.
"""

import pytest

from geldalyse.merchant import FIXED_NAMES, extract_merchant, is_received_transfer

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

