
DEFAULT_CATEGORY = "INCONNU"
CATEGORIES = {
    "ALIMENTATION": ["DELHAIZE", "COLRUYT", "CARREFOUR"],
    "TRANSPORT": ["STIB", "SNCB", "TOTALENERGIES"],
    "SANTE": ["PHARMACIE"],
    "FACTURE": ["PROXIMUS", "NETFLIX"],
    "LOGEMENT": ["LOYER"],
    "SHOPPING": ["ZALANDO", "ZARA", "C&A"],
    "REVENUS": ["SALAIRE"],
    "RESTAURATION": ["PAIN QUOTIDIEN", "RESTAURANT", "DELIVEROO"],
}

#Match catégories with labels
def categorize(label: str) -> str:
    normalized_label = label.upper()
    for category, keywords in CATEGORIES.items():
        for keyword in keywords:
            if keyword in normalized_label:
                return category
    
    return DEFAULT_CATEGORY


if __name__ == "__main__":
    print(categorize("DELHAIZE BRUXELLES"))
    print(categorize("VIREMENT SALAIRE"))
    print(categorize("BOULANGERIE DU COIN"))
    print(categorize("stib mivb"))