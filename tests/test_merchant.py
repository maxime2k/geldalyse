
from pathlib import Path

from geldalyse.merchant import extract_merchant



def test_card_payment_returns_third_segment():
    merchant = extract_merchant("PAIEMENT BANCONTACT 04/01/26 - 18H12 - DELHAIZE IXELLES 1050 - BRUXELLES - BEL …")
    assert merchant == "DELHAIZE IXELLES 1050"