from pathlib import Path

import pandas as pd
import pytest

from geldalyse.readers import FortisReader, INGReader, InvalidStatementError
from geldalyse.schema import OPERATION_TYPE_LABELS, STANDARD_COLUMNS

FIXTURES_DIR = Path(__file__).parents[1] / "fixtures"
ING_SAMPLE = FIXTURES_DIR / "ing_export_sample.csv"
ING_HEADER_ONLY = FIXTURES_DIR / "ing_header_only.csv"
FORTIS_SAMPLE = FIXTURES_DIR / "fortis_export_sample.csv"
FORTIS_HEADER_ONLY = FIXTURES_DIR / "fortis_header_only.csv"
WRONG_COLUMNS = FIXTURES_DIR / "wrong_format.csv"
EMPTY_FILE = FIXTURES_DIR / "empty.csv"


VALID_STATEMENTS = [
    pytest.param(INGReader(), ING_SAMPLE, id="ing"),
    pytest.param(FortisReader(), FORTIS_SAMPLE, id="fortis"),
]
BANK_READERS = [
    pytest.param(INGReader(), id="ing"),
    pytest.param(FortisReader(), id="fortis"),
]
EMPTY_STATEMENTS = [
    pytest.param(INGReader(), ING_HEADER_ONLY, id="ing"),
    pytest.param(FortisReader(), FORTIS_HEADER_ONLY, id="fortis"),
]
INVALID_FILES = [
    pytest.param(WRONG_COLUMNS, id="wrong-columns"),
    pytest.param(EMPTY_FILE, id="empty"),
]

OTHER_BANK_STATEMENTS = [
    pytest.param(INGReader(), FORTIS_SAMPLE, id="ing-reads-fortis"),
    pytest.param(FortisReader(), ING_SAMPLE, id="fortis-reads-ing"),
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
