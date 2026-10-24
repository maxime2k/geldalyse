# Order matters: the first matching category wins.
# Keywords in uppercase, accents included: labels are uppercased before matching.
# Keep keywords precise: "CAR" would also match "CARTE".

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


if __name__ == "__main__":
    print(categorize("DELHAIZE BRUXELLES"))
    print(categorize("VIREMENT SALAIRE"))
    print(categorize("BOULANGERIE DU COIN"))
    print(categorize("stib mivb"))