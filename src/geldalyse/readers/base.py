from abc import ABC, abstractmethod

import pandas as pd


class BankReader(ABC):
    """Read one bank's export into the standard transaction format."""

    @abstractmethod
    def read(self, file) -> pd.DataFrame:
        """Read, validate and parse the file into the standard format."""


class InvalidStatementError(ValueError):
    """Raised when a bank statement has an invalid value."""


def parse_dates(dates: pd.Series) -> pd.Series:
    """Parse each day-first date, or raise ValueError with its line in the file."""

    parsed = pd.to_datetime(dates, format="%d/%m/%Y", errors="coerce")
    invalid = parsed.isna()
    if invalid.any():
        index = invalid.idxmax()
        raise InvalidStatementError(
            f"Ligne {index + 2}. Date invalide : « {dates[index]} »."
        )
    return parsed
