from pathlib import Path

import pandas as pd
import pytest

from geldalyse.readers import INGReader
from geldalyse.schema import OPERATION_TYPE_LABELS, STANDARD_COLUMNS

FIXTURES_DIR = Path(__file__).parents[1] / "fixtures"

READERS = [
    pytest.param(INGReader(), FIXTURES_DIR / "ing_export_sample.csv", id="ing"),
]


@pytest.mark.parametrize("reader, statement", READERS)
def test_reader_returns_standard_columns(reader, statement):
    transactions = reader.read(statement)

    assert list(transactions.columns) == STANDARD_COLUMNS


@pytest.mark.parametrize("reader, statement", READERS)
def test_reader_returns_no_missing_values(reader, statement):
    transactions = reader.read(statement)
    assert not transactions.isna().any().any()


@pytest.mark.parametrize("reader, statement", READERS)
def test_reader_returns_dates(reader, statement):
    transactions = reader.read(statement)

    assert pd.api.types.is_datetime64_any_dtype(transactions["date"])


@pytest.mark.parametrize("reader, statement", READERS)
def test_reader_returns_numeric_amounts(reader, statement):
    transactions = reader.read(statement)

    assert pd.api.types.is_any_real_numeric_dtype(transactions["amount"])


@pytest.mark.parametrize("reader, statement", READERS)
def test_reader_returns_known_operation_types(reader, statement):
    transactions = reader.read(statement)

    assert set(transactions["operation_type"]) <= set(OPERATION_TYPE_LABELS)
