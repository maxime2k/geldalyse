
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