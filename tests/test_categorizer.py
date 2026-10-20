from spendlens.categorizer import categorize, DEFAULT_CATEGORY


"""Unit tests for the keyword-based categorizer."""


def test_supermarket_is_food():
    assert categorize("DELHAIZE BRUXELLES") == "ALIMENTATION"


def test_lowercase_label_is_recognized():
    assert categorize("virement du salaire") == "REVENUS"


def test_unknown_label_returns_default():
    assert categorize("pret bancaire") == DEFAULT_CATEGORY