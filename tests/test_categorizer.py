from geldalyse.categorizer import categorize, DEFAULT_CATEGORY


"""Unit tests for the keyword-based categorizer."""


def test_supermarket_is_food():
    assert categorize("DELHAIZE BRUXELLES") == "ALIMENTATION"


def test_lowercase_label_is_recognized():
    assert categorize("virement du salaire") == "REVENUS"


def test_unknown_label_returns_default():
    assert categorize("pret bancaire") == DEFAULT_CATEGORY


def test_interest_with_fees_in_label_is_income():
    assert categorize("Intérêts-Frais au 31/12/25 Décompte en annexe") == "REVENUS"