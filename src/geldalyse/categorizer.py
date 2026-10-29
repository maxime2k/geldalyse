"""Assign a category to each transaction from its label and the sign of its amount.
    Order matters: the first matching category wins.
    Keywords in uppercase, accents included: labels are uppercased before matching.
    Keep keywords precise: "CAR" would also match "CARTE".
"""


import pandas as pd

from geldalyse.merchant import is_received_transfer

DEFAULT_EXPENSE_CATEGORY = "INCONNU"
DEFAULT_INCOME_CATEGORY = "AUTRES ENTRÉES"
REFUND_CATEGORY = "REMBOURSEMENT"

EXPENSE_CATEGORIES = {
    "ALIMENTATION": ["DELHAIZE", "COLRUYT", "CARREFOUR", "OKAY", "ALIMENTATION"],
    "TRANSPORT": ["STIB", "SNCB", "TOTALENERGIES", "PARKING", "DELIJN", "PARK BRU"],
    "SANTE": ["PHARMA"],
    "FACTURE": ["PROXIMUS", "NETFLIX", "DÉCOMPTE DE FRAIS", "INTÉRÊTS-FRAIS"],
    "LOGEMENT": ["LOYER"],
    "SHOPPING": ["ZALANDO", "ZARA", "C&A", "FNAC", "AMZN", "PAPETERIE"],
    "RESTAURATION": ["PAIN QUOTIDIEN", "RESTAURANT", "DELIVEROO", "SNACK"],
    "RETRAITS": ["RETRAIT D'ESPÈCES"],
}

# Searched before EXPENSE_CATEGORIES for positive amounts: an income keyword wins over a shop name.
INCOME_CATEGORIES = {
        "SALAIRE": ["SALAIRE"],
        "INVESTISSEMENT": ["INTÉRÊTS"],
}

EXPENSE_CATEGORY_NAMES = [*EXPENSE_CATEGORIES, DEFAULT_EXPENSE_CATEGORY]
INCOME_CATEGORY_NAMES = [*INCOME_CATEGORIES, DEFAULT_INCOME_CATEGORY, REFUND_CATEGORY]
SELECTABLE_EXPENSE_CATEGORIES = [
    category
    for category in EXPENSE_CATEGORY_NAMES
    if category != DEFAULT_EXPENSE_CATEGORY
]
#Match catégories with labels
def categorize(label: str, amount: float) -> str:
    """Return the first matching category, else a default that depends on the sign of amount."""
    if amount > 0:
        category = (
            _find_category(label=label, categories=INCOME_CATEGORIES)
            or _find_category(label=label, categories=EXPENSE_CATEGORIES)
        )
        default_category = REFUND_CATEGORY if is_received_transfer(label) else DEFAULT_INCOME_CATEGORY
    else:
        category = _find_category(label=label, categories=EXPENSE_CATEGORIES)
        default_category = DEFAULT_EXPENSE_CATEGORY
        
    return category or default_category

def _find_category(label: str, categories: dict[str, list[str]]) -> str | None:
        
    normalized_label = label.upper()
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in normalized_label:
                return category
    
    return None

# --- change transactions categories manually ---


def apply_manual_categories(transactions: pd.DataFrame, choices: dict[str, str]) -> pd.DataFrame:
    """Return a copy where each operation in choices gets the chosen category, if it matches the direction of the money."""
    transactions_copy = transactions.copy()
    chosen = transactions_copy["merchant"].map(choices)
    wrong_direction = (
        (chosen.isin(INCOME_CATEGORY_NAMES) & (transactions_copy["amount"] < 0))
        | (chosen.isin(EXPENSE_CATEGORY_NAMES) & (transactions_copy["amount"] > 0))
    )
    chosen = chosen.mask(wrong_direction)

    transactions_copy["category"] = chosen.fillna(transactions["category"])

    return transactions_copy


if __name__ == "__main__":
    print(categorize("DELHAIZE BRUXELLES", -10.0))
    print(categorize("VIREMENT SALAIRE", -250.5))
    print(categorize("BOULANGERIE DU COIN", -30.5))
    print(categorize("stib mivb", -2.7))