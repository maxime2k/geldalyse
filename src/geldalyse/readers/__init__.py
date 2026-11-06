"""Bank readers: each one turns a bank's export into the standard format."""

import pandas as pd

from geldalyse.readers.base import InvalidStatementError
from geldalyse.readers.fortis import FortisReader
from geldalyse.readers.ing import INGReader

__all__ = ["InvalidStatementError", "read_statement", "FortisReader"]


def read_statement(file) -> pd.DataFrame:
    """Read a bank export into the standard transaction format."""
    return INGReader().read(file)
