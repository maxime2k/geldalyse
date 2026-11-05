from pathlib import Path

import pytest

from geldalyse.readers import INGReader
from geldalyse.schema import STANDARD_COLUMNS

FIXTURES_DIR = Path(__file__).parents[1] / "fixtures"

READERS = [(INGReader(), FIXTURES_DIR / "ing_export_sample.csv")]


@pytest.mark.parametrize("reader, statement", READERS)
def test_reader_returns_standard_columns(reader, statement):
    transactions = reader.read(statement)

    assert list(transactions.columns) == STANDARD_COLUMNS
