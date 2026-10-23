
from pathlib import Path

from geldalyse.merchant import extract_merchant

CARD_PAYMENT = "PAIEMENT BANCONTACT 04/01/26 - 18H12 - DELHAIZE IXELLES 1050 - ..."
CARD_PAYMENT_NO_POSTCODE = "PAIEMENT DEBIT MASTERCARD 14/02/26 - 10H00 - NETFLIX.COM - ..."

def test_card_payment_returns_third_segment():
    merchant = extract_merchant(CARD_PAYMENT)
    assert merchant == "DELHAIZE IXELLES"


def test_card_payment_without_postcode_returns_third_segment():
    merchant = extract_merchant(CARD_PAYMENT_NO_POSTCODE)
    assert merchant == "NETFLIX.COM"