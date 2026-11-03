from abc import ABC, abstractmethod

import pandas as pd


class BankReader(ABC):
    """Read one bank's export into the standard transaction format."""

    @abstractmethod
    def read(self, file) -> pd.DataFrame:
        """Read, validate and parse the file into the standard format."""


class InvalidStatementError(ValueError):
    """Raised when a bank statement has an invalid value."""
