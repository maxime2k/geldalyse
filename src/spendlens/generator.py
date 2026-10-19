"""Generate fake bank transactions for Spendlens.

The data is entirely fictional: it lets us develop and demo the app
without ever touching real banking data.
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

# One-off purchases: label -> (min amount, max amount), in euros.
MERCHANTS: dict[str, tuple[float, float]] = {
    "DELHAIZE BRUXELLES": (15.0, 90.0),
    "COLRUYT ANDERLECHT": (20.0, 120.0),
    "CARREFOUR EXPRESS": (5.0, 35.0),
    "STIB MIVB": (2.1, 2.6),
    "SNCB NMBS": (8.0, 25.0),
    "TOTALENERGIES": (40.0, 75.0),
    "RESTAURANT LE PAIN QUOTIDIEN": (12.0, 40.0),
    "DELIVEROO": (15.0, 35.0),
    "PHARMACIE MULTIPHARMA": (5.0, 45.0),
    "ZALANDO": (25.0, 120.0),
}

# Fixed monthly operations: (day of month, label, signed amount).
# Positive = money in, negative = money out.
RECURRING: list[tuple[int, str, float]] = [
    (1, "VIREMENT SALAIRE EMPLOYEUR SA", 2350.00),
    (3, "LOYER APPARTEMENT", -850.00),
    (5, "PROXIMUS FACTURE", -45.99),
    (10, "NETFLIX.COM", -13.49),
    (15, "ASSURANCE ETHIAS", -32.50),
]

COLUMNS = ["date", "label", "amount"]


def generate_transactions(
    start: date,
    days: int = 90,
    seed: int | None = 42,
) -> pd.DataFrame:
    """Return a DataFrame of fake transactions covering `days` days from `start`.

    Using a fixed `seed` makes the output reproducible: the same seed
    always produces the same transactions.
    """
    rng = random.Random(seed)
    rows: list[dict] = []

    for offset in range(days):
        day = start + timedelta(days=offset)

        for day_of_month, label, amount in RECURRING:
            if day.day == day_of_month:
                rows.append({"date": day, "label": label, "amount": amount})

        for _ in range(rng.randint(0, 2)):
            label = rng.choice(list(MERCHANTS))
            low, high = MERCHANTS[label]
            amount = -round(rng.uniform(low, high), 2)
            rows.append({"date": day, "label": label, "amount": amount})

    return pd.DataFrame(rows, columns=COLUMNS)


def save_csv(transactions: pd.DataFrame, path: Path) -> None:
    """Write transactions to a CSV file, creating parent folders if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    transactions.to_csv(path, index=False)


if __name__ == "__main__":
    output = Path("data/transactions.csv")
    df = generate_transactions(start=date(2026, 1, 1), days=180)
    save_csv(df, output)
    print(f"{len(df)} transactions written to {output}")
