from spendlens.generator import MERCHANTS, RECURRING
from spendlens.categorizer import categorize, DEFAULT_CATEGORY

"""Integration tests: the categorizer must recognize every generated label."""


def test_all_merchants_are_categorized():
    for merchant in MERCHANTS:
        assert categorize(merchant) != DEFAULT_CATEGORY, f"{merchant} does not have a category"


def test_all_recurring_labels_are_categorized():
    for _, label, _ in RECURRING:
        assert categorize(label) != DEFAULT_CATEGORY, f"{label} does not have a category"
        
