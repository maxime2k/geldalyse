from pathlib import Path

import pandas as pd
import pytest

from geldalyse.readers import INGReader, InvalidStatementError
from geldalyse.schema import OPERATION_TYPE_LABELS, STANDARD_COLUMNS

FIXTURES_DIR = Path(__file__).parents[1] / "fixtures"
ING_SAMPLE = "ing_export_sample.csv"
WRONG_COLUMNS = FIXTURES_DIR / "wrong_format.csv"
EMPTY_FILE = FIXTURES_DIR / "empty.csv"

VALID_STATEMENTS = [
    pytest.param(INGReader(), FIXTURES_DIR / ING_SAMPLE, id="ing"),
]
BANK_READERS = [
    pytest.param(INGReader(), id="ing"),
]

INVALID_FILES = [
    pytest.param(WRONG_COLUMNS, id="wrong-columns"),
    pytest.param(EMPTY_FILE, id="empty"),
]


@pytest.mark.parametrize("reader, statement", VALID_STATEMENTS)
def test_reader_returns_standard_columns(reader, statement):
    transactions = reader.read(statement)

    assert list(transactions.columns) == STANDARD_COLUMNS


@pytest.mark.parametrize("reader, statement", VALID_STATEMENTS)
def test_reader_returns_no_missing_values(reader, statement):
    transactions = reader.read(statement)
    assert not transactions.isna().any().any()


@pytest.mark.parametrize("reader, statement", VALID_STATEMENTS)
def test_reader_returns_dates(reader, statement):
    transactions = reader.read(statement)

    assert pd.api.types.is_datetime64_any_dtype(transactions["date"])


@pytest.mark.parametrize("reader, statement", VALID_STATEMENTS)
def test_reader_returns_numeric_amounts(reader, statement):
    transactions = reader.read(statement)

    assert pd.api.types.is_any_real_numeric_dtype(transactions["amount"])


@pytest.mark.parametrize("reader, statement", VALID_STATEMENTS)
def test_reader_returns_known_operation_types(reader, statement):
    transactions = reader.read(statement)

    assert set(transactions["operation_type"]) <= set(OPERATION_TYPE_LABELS)


@pytest.mark.parametrize("column", ["label", "counterparty"])
@pytest.mark.parametrize("reader, statement", VALID_STATEMENTS)
def test_reader_returns_no_empty_text(reader, statement, column):
    transactions = reader.read(statement)

    assert (transactions[column].str.strip() != "").all()


@pytest.mark.parametrize("column", ["label", "counterparty"])
@pytest.mark.parametrize("reader, statement", VALID_STATEMENTS)
def test_reader_returns_uppercase_text(reader, statement, column):
    transactions = reader.read(statement)

    assert (transactions[column] == transactions[column].str.upper()).all()


@pytest.mark.parametrize("statement", INVALID_FILES)
@pytest.mark.parametrize("reader", BANK_READERS)
def test_reader_rejects_invalid_file(reader, statement):
    with pytest.raises(InvalidStatementError):
        reader.read(statement)
