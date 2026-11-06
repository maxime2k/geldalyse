import pandas as pd
import pytest

from geldalyse.readers import InvalidStatementError
from geldalyse.schema import OPERATION_TYPE_LABELS, STANDARD_COLUMNS
from tests.readers.statements import (
    BANK_READERS,
    EMPTY_STATEMENTS,
    INVALID_FILES,
    OTHER_BANK_STATEMENTS,
    VALID_STATEMENTS,
)


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


@pytest.mark.parametrize("reader, statement", EMPTY_STATEMENTS)
def test_reader_returns_standar_colums_for_empty_file(reader, statement):
    transactions = reader.read(statement)

    assert transactions.empty
    assert list(transactions) == STANDARD_COLUMNS


@pytest.mark.parametrize("reader, statement", VALID_STATEMENTS)
def test_reader_matches_its_statement(reader, statement):
    assert reader.matches(statement)


@pytest.mark.parametrize("statement", INVALID_FILES)
@pytest.mark.parametrize("reader", BANK_READERS)
def test_reader_does_not_match_invalid_file(reader, statement):
    assert not reader.matches(statement)


@pytest.mark.parametrize("reader, statement", OTHER_BANK_STATEMENTS)
def test_reader_does_not_match_other_bank_statement(reader, statement):
    assert not reader.matches(statement)
