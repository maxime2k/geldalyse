"""Bank readers: each one turns a bank's export into the standard format."""

import pandas as pd

from geldalyse.readers.base import InvalidStatementError
from geldalyse.readers.fortis import FortisReader
from geldalyse.readers.ing import INGReader

READERS = [FortisReader(), INGReader()]

__all__ = [
    "InvalidStatementError",
    "read_statement",
    "FortisReader",
    "INGReader",
    "READERS",
]


def read_statement(file) -> pd.DataFrame:
    """Read a bank export into the standard transaction format."""
    for reader in READERS:
        if reader.matches(file):
            return reader.read(file)
    banks = ", ".join(reader.bank_name for reader in READERS)
    raise InvalidStatementError(
        f"Format non reconnu. Banques prises en charge : {banks}."
    )
