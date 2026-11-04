"""Assign a category to each transaction from its label and the sign of its amount.
Order matters: the first matching category wins.
Keywords in uppercase, accents included: labels are uppercased before matching.
Keep keywords precise: "CAR" would also match "CARTE".
"""

import pandas as pd

from geldalyse.schema import BANK_OPERATION, CASH, TRANSFER

DEFAULT_EXPENSE_CATEGORY = "INCONNU"
DEFAULT_INCOME_CATEGORY = "AUTRES ENTRÉES"
REFUND_CATEGORY = "REMBOURSEMENT"
RECEIVED_TRANSFER_CATEGORY = "VIREMENTS REÇUS"

EXPENSE_CATEGORIES = {
    "ALIMENTATION": ["DELHAIZE", "COLRUYT", "CARREFOUR", "OKAY", "ALIMENTATION"],
    "TRANSPORT": ["STIB", "SNCB", "TOTALENERGIES", "PARKING", "DELIJN", "PARK BRU"],
    "SANTE": ["PHARMA"],
    "FACTURE": ["PROXIMUS", "NETFLIX"],
    "LOGEMENT": ["LOYER"],
    "SHOPPING": ["ZALANDO", "ZARA", "C&A", "FNAC", "AMZN", "PAPETERIE"],
    "RESTAURATION": ["PAIN QUOTIDIEN", "RESTAURANT", "DELIVEROO", "SNACK"],
    "RETRAITS": [],
}

# Searched before EXPENSE_CATEGORIES for positive amounts.
INCOME_CATEGORIES = {
    "SALAIRE": ["SALAIRE"],
    "INVESTISSEMENT": [],
}
# Decided by the operation type, before any keyword: the type is a fact from the reader.
EXPENSE_TYPE_CATEGORIES = {CASH: "RETRAITS", BANK_OPERATION: "FACTURE"}
INCOME_TYPE_CATEGORIES = {BANK_OPERATION: "INVESTISSEMENT"}

EXPENSE_CATEGORY_NAMES = [*EXPENSE_CATEGORIES, DEFAULT_EXPENSE_CATEGORY]
INCOME_CATEGORY_NAMES = [
    *INCOME_CATEGORIES,
    DEFAULT_INCOME_CATEGORY,
    REFUND_CATEGORY,
    RECEIVED_TRANSFER_CATEGORY,
]


def categorize(label: str, amount: float, operation_type: str) -> str:
    """Return the first matching category, else a default based on the sign."""
    if amount > 0:
        category = (
            INCOME_TYPE_CATEGORIES.get(operation_type)
            or _find_category(label=label, categories=INCOME_CATEGORIES)
            or _find_category(label=label, categories=EXPENSE_CATEGORIES)
        )
        default_category = (
            RECEIVED_TRANSFER_CATEGORY
            if operation_type == TRANSFER
            else DEFAULT_INCOME_CATEGORY
        )
    else:
        category = EXPENSE_TYPE_CATEGORIES.get(operation_type) or _find_category(
            label=label, categories=EXPENSE_CATEGORIES
        )
        default_category = DEFAULT_EXPENSE_CATEGORY

    return category or default_category


def _find_category(label: str, categories: dict[str, list[str]]) -> str | None:
    """Return the first category whose keyword appears in the label, or None."""
    normalized_label = label.upper()
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in normalized_label:
                return category

    return None


# --- change transactions categories manually ---


def apply_manual_categories(
    transactions: pd.DataFrame, choices: dict[str, str]
) -> pd.DataFrame:
    """Return a copy with the chosen categories that match the money direction."""
    transactions_copy = transactions.copy()
    chosen = transactions_copy["counterparty"].map(choices)
    wrong_direction = (
        chosen.isin(INCOME_CATEGORY_NAMES) & (transactions_copy["amount"] < 0)
    ) | (chosen.isin(EXPENSE_CATEGORY_NAMES) & (transactions_copy["amount"] > 0))
    chosen = chosen.mask(wrong_direction)

    transactions_copy["category"] = chosen.fillna(transactions["category"])

    return transactions_copy
