"""Generate fake bank transactions for Spendlens (fictional data only)."""

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

# Shop -> (min amount, max amount), in euros.
MERCHANTS = {
    "DELHAIZE BRUXELLES": (15, 90),
    "COLRUYT ANDERLECHT": (20, 120),
    "CARREFOUR EXPRESS": (5, 35),
    "STIB MIVB": (2.1, 2.6),
    "SNCB NMBS": (8, 25),
    "TOTALENERGIES": (40, 75),
    "LE PAIN QUOTIDIEN": (12, 40),
    "DELIVEROO": (15, 35),
    "PHARMACIE MULTIPHARMA": (5, 45),
    "ZALANDO": (25, 120),
}

# (day of month, label, amount). Positive = money in, negative = money out.
RECURRING = [
    (1, "VIREMENT SALAIRE", 2350),
    (3, "LOYER APPARTEMENT", -850),
    (5, "PROXIMUS FACTURE", -45.99),
    (10, "NETFLIX.COM", -13.49),
]


def make_transaction(day: date, label: str, amount: float) -> dict:
    return {"date": day, "label": label, "amount": amount}


def generate_transactions(start: date, days: int, seed: int = 42) -> pd.DataFrame:
    """Return `days` days of fake transactions. Same seed, same result."""
    rng = random.Random(seed)
    transactions = []

    for i in range(days):
        day = start + timedelta(days=i)

        for day_of_month, label, amount in RECURRING:
            if day.day == day_of_month:
                transactions.append(make_transaction(day, label, amount))

        # Between 0 and 2 random purchases per day.
        for _ in range(rng.randint(0, 2)):
            shop = rng.choice(list(MERCHANTS))
            low, high = MERCHANTS[shop]
            amount = -round(rng.uniform(low, high), 2)
            transactions.append(make_transaction(day, shop, amount))

    return pd.DataFrame(transactions)


def save_csv(transactions: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    transactions.to_csv(path, index=False)


if __name__ == "__main__":
    output = Path("data/transactions.csv")
    transactions = generate_transactions(start=date(2026, 1, 1), days=180)
    save_csv(transactions, output)
    print(f"{len(transactions)} transactions written to {output}")