"""Generate fake bank transactions for Geldalyse (fictional data only)."""

import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


@dataclass(frozen=True)
class Merchant:
    """A fictional shop of the demo, paid by card."""

    name: str
    city: str
    card: str
    low: float
    high: float
    country: str = "BEL"


@dataclass(frozen=True)
class Recurring:
    """A fictional payment repeated each month on the same day."""

    day: int
    family: str
    fields: dict[str, str]
    amount: float


ING_HEADER = (
    "Numéro de compte;Nom du compte;Compte contrepartie;Numéro de mouvement;"
    "Date comptable;Date valeur;Montant;Devise;Libellés;Détails du mouvement;Message"
)
# Fictional card number, as masked in ING exports.
CARD_NUMBER = "Numéro de carte 0000 XXXX XXXX 0000"

# ING description of each family, as in real exports: only the {fields} vary.
ING_LABEL_TEMPLATES = {
    "bancontact": (
        "Paiement Bancontact {date} - {time} - {merchant} - {city} - BEL " + CARD_NUMBER
    ),
    "mastercard": (
        "Paiement Debit Mastercard {date} - {time} - {merchant}"
        " - {city} - {country} " + CARD_NUMBER + " Référence ING: XXXX"
    ),
    "cash_withdrawal": (
        "Retrait d'espèces Bancontact {date} - {time} - CASH {postal_code}"
        " - {city} - BEL " + CARD_NUMBER
    ),
    "transfer_received": (
        "Virement en euros (SEPA) De: {name} - {iban} Communication: {communication}"
    ),
    "transfer_sent": (
        "Virement en euros (SEPA) Vers: {name} - {iban} Communication: {communication}"
    ),
    "instant_transfer_received": (
        "Virement instantané: DE: {name} - {iban} Instantané le {short_date}"
        " - {clock} Info personnelle: XXXX"
    ),
    "instant_transfer_sent": (
        "Virement instantané: ING app Vers: {name} - {iban} Instantané le {short_date}"
        " - {clock} Info personnelle: XXXX"
    ),
    "account_fees": "Décompte de frais n° 000000000 Pièce justificative en annexe",
    "interest": "Intérêts-Frais au {date} Décompte en annexe",
    # Approximate structure: only the start is confirmed by a real export.
    "direct_debit": "Domiciliation en euros Vers: {name} - {reference}",
    # Approximate structure: only the start is confirmed by a real export.
    "standing_order": (
        "Ordre permanent Vers: {name} - {iban} Communication: {communication}"
    ),
}

FAKE_IBAN = "BE00 0000 0000 0000"

MERCHANTS = [
    Merchant("DELHAIZE IXELLES 1050", "BRUXELLES", "bancontact", 15, 90),
    Merchant("COLRUYT ANDERLECHT 1070", "BRUXELLES", "bancontact", 20, 120),
    Merchant("CARREFOUR EXPRESS 1000", "BRUXELLES", "bancontact", 5, 35),
    Merchant("STIB MIVB 1000", "BRUXELLES", "bancontact", 2.1, 2.6),
    Merchant("SNCB NMBS 1060", "BRUXELLES", "bancontact", 8, 25),
    Merchant("TOTALENERGIES 1050", "BRUXELLES", "bancontact", 40, 75),
    Merchant("LE PAIN QUOTIDIEN 1000", "BRUXELLES", "mastercard", 12, 40),
    Merchant("DELIVEROO.BE", "BRUXELLES", "mastercard", 15, 35),
    Merchant("PHARMACIE MULTIPHARMA 1050", "BRUXELLES", "bancontact", 5, 45),
    Merchant("ZALANDO SE", "BERLIN", "mastercard", 25, 120, country="DEU"),
    # Unknown to the categorizer: the demo also needs operations to classify.
    Merchant("BOULANGERIE FICTIVE 1050", "BRUXELLES", "bancontact", 3, 12),
    Merchant("LIBRAIRIE DU COIN 1060", "BRUXELLES", "bancontact", 8, 30),
]

RECURRING = [
    Recurring(
        1,
        "transfer_received",
        {"name": "SOCIÉTÉ FICTIVE SA", "iban": FAKE_IBAN, "communication": "SALAIRE"},
        2350.00,
    ),
    Recurring(1, "account_fees", {}, -1.90),
    Recurring(
        3,
        "standing_order",
        {"name": "PROPRIÉTAIRE FICTIF", "iban": FAKE_IBAN, "communication": "LOYER"},
        -850.00,
    ),
    Recurring(5, "direct_debit", {"name": "PROXIMUS", "reference": "XXXX"}, -45.99),
    Recurring(
        10,
        "mastercard",
        {"merchant": "NETFLIX.COM", "city": "AMSTERDAM", "country": "NLD"},
        -13.49,
    ),
]


def _ing_row(
    number: int,
    day: date,
    family: str,
    fields: dict[str, str],
    amount: float,
    rng: random.Random,
) -> str:
    """Return one line of an ING CSV export, with a fictional description."""
    hour = rng.randint(7, 22)
    minute = rng.randint(0, 59)
    all_fields = fields | {
        "date": day.strftime("%d/%m/%y"),
        "short_date": day.strftime("%d/%m"),
        "time": f"{hour}h{minute:02d}",
        "clock": f"{hour:02d}:{minute:02d}:00",
    }
    label = ING_LABEL_TEMPLATES[family].format(**all_fields)

    value_date = day.strftime("%d/%m/%Y")
    booking_date = (day + timedelta(days=1)).strftime("%d/%m/%Y")
    ing_amount = f"{amount:.2f}".replace(".", ",")

    return f";;;{number};{booking_date};{value_date};{ing_amount};EUR;{label};;"


def generate_ing_export(start: date, days: int, seed: int = 42) -> str:
    """Return the text of a fictional ING CSV export. Same seed, same result."""
    rng = random.Random(seed)
    rows = []

    for i in range(days):
        day = start + timedelta(days=i)

        for payment in RECURRING:
            if day.day == payment.day:
                rows.append(
                    _ing_row(
                        len(rows) + 1,
                        day,
                        payment.family,
                        payment.fields,
                        payment.amount,
                        rng,
                    )
                )

        # Between 0 and 2 random purchases per day.
        for _ in range(rng.randint(0, 2)):
            shop = rng.choice(MERCHANTS)
            amount = -round(rng.uniform(shop.low, shop.high), 2)
            fields = {"merchant": shop.name, "city": shop.city, "country": shop.country}
            rows.append(_ing_row(len(rows) + 1, day, shop.card, fields, amount, rng))

    return "\n".join([ING_HEADER, *rows]) + "\n"


if __name__ == "__main__":
    output = Path("data/ing_demo_export.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    export = generate_ing_export(start=date(2026, 1, 1), days=180)
    output.write_text(export, encoding="utf-8")
    print(f"{len(export.splitlines()) - 1} transactions written to {output}")
