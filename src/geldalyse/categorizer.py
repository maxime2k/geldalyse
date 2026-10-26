# Order matters: the first matching category wins.
# Keywords in uppercase, accents included: labels are uppercased before matching.
# Keep keywords precise: "CAR" would also match "CARTE".

import pandas as pd

DEFAULT_CATEGORY = "INCONNU"
CATEGORIES = {
    "ALIMENTATION": ["DELHAIZE", "COLRUYT", "CARREFOUR"],
    "TRANSPORT": ["STIB", "SNCB", "TOTALENERGIES", "PARKING"],
    "SANTE": ["PHARMACIE"],
    "FACTURE": ["PROXIMUS", "NETFLIX", "DÉCOMPTE DE FRAIS"],
    "LOGEMENT": ["LOYER"],
    "SHOPPING": ["ZALANDO", "ZARA", "C&A"],
    "REVENUS": ["SALAIRE", "INTÉRÊTS"],
    "RESTAURATION": ["PAIN QUOTIDIEN", "RESTAURANT", "DELIVEROO"],
    "RETRAITS": ["RETRAIT D'ESPÈCES"],
}

#Match catégories with labels
def categorize(label: str) -> str:
    """Return the first category whose keyword appears in the label, else DEFAULT_CATEGORY."""
    normalized_label = label.upper()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in normalized_label:
                return category
    
    return DEFAULT_CATEGORY

# --- change transactions categories manually ---


def apply_manual_categories(transactions: pd.DataFrame, choices: dict[str, str]) -> pd.DataFrame:
    """Return a copy where each operation in choices gets the chosen category."""
    transactions_copy = transactions.copy()
    transactions_copy["category"] = transactions_copy["merchant"].map(choices).fillna(transactions["category"])

    return transactions_copy


if __name__ == "__main__":
    print(categorize("DELHAIZE BRUXELLES"))
    print(categorize("VIREMENT SALAIRE"))
    print(categorize("BOULANGERIE DU COIN"))
    print(categorize("stib mivb"))