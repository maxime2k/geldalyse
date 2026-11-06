from abc import ABC, abstractmethod
from collections.abc import Callable

import pandas as pd

from geldalyse.schema import MISSING_LABEL


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


def parse_amounts(amounts: pd.Series, parse: Callable[[str], float]) -> pd.Series:
    """Parse each amount, or raise InvalidStatementError with its line in the file."""

    values = []
    for index, text in amounts.items():
        try:
            values.append(parse(text))
        except ValueError as error:
            raise InvalidStatementError(f"Ligne {index + 2}. {error}") from error
    return pd.Series(values, index=amounts.index)


def clean_labels(labels: pd.Series) -> pd.Series:
    """Strip and uppercase each label, or replace it with MISSING_LABEL if empty."""
    labels = labels.str.strip().str.upper()

    return labels.replace("", MISSING_LABEL)
