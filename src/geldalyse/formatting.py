"""Turn analysis results into French text for the dashboard: months, baselines and summaries."""

import pandas as pd

from geldalyse.analysis import PREVIOUS_MONTH, LAST_THREE_MONTHS, SAME_MONTH_LAST_YEAR

MONTH_NAMES = {
    1: "janvier",
    2: "février",
    3: "mars",
    4: "avril",
    5: "mai",
    6: "juin",
    7: "juillet",
    8: "août",
    9: "septembre",
    10: "octobre",
    11: "novembre",
    12: "décembre",
}
VOWELS = ("a", "o")
BASELINE_LABELS = {
    PREVIOUS_MONTH: "Mois précédent",
    LAST_THREE_MONTHS: "Moyenne des 3 mois précédents",
    SAME_MONTH_LAST_YEAR: "Même mois l’an passé",
}
NBSP = "\u00a0"  #espace insécable


def format_month(month: str) -> str:
    """Return a YYYY-MM month as its French name and year, like “janvier 2026”."""
    
    date = pd.Timestamp(month)

    return f"{MONTH_NAMES[date.month]} {date.year}"


def format_baseline(months: list[str]) -> str:
    """Return the French description of the baseline months, like "la moyenne de juin à août 2026"."""    
    
    if len(months) == 1:
        return format_month(months[0])
    
    first_month, last_month = months[0], months[-1]
    same_year = pd.Timestamp(first_month).year == pd.Timestamp(last_month).year

    start = MONTH_NAMES[pd.Timestamp(first_month).month] if same_year else format_month(first_month)
    end = format_month(last_month)

    preposition = "d'" if start[0] in VOWELS else "de "

    return f"la moyenne {preposition}{start} à {end}"

def format_amount(amount: float) -> str:
    """Return the French amount format, ex: 1234.5 £ = 1 234,50 £.""" 
    
    english_format = f"{amount:,.2f}"
    french_format = english_format.replace(",", NBSP).replace(".", ",")

    return f"{french_format}{NBSP}€"

    
