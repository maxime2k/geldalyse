"""Turn analysis results into French text for the dashboard: months, baselines and summaries."""

import pandas as pd

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
def format_month(month: str) -> str:
    """Return a YYYY-MM month as its French name and year, like “janvier 2026”."""
    
    date = pd.Timestamp(month)

    return f"{MONTH_NAMES[date.month]} {date.year}"