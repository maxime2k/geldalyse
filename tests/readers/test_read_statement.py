"""Tests for the automatic choice of the bank reader."""

from io import StringIO

import pandas as pd
import pytest

from geldalyse.readers import READERS, InvalidStatementError, read_statement
from tests.readers.statements import VALID_STATEMENTS, WRONG_COLUMNS


@pytest.mark.parametrize("reader, statement", VALID_STATEMENTS)
def test_read_statement_uses_the_reader_of_the_bank(reader, statement):
    pd.testing.assert_frame_equal(read_statement(statement), reader.read(statement))


@pytest.mark.parametrize("reader, statement", VALID_STATEMENTS)
def test_read_statement_reads_an_open_file(reader, statement):
    open_file = StringIO(statement.read_text(encoding="utf-8"))
    pd.testing.assert_frame_equal(read_statement(open_file), reader.read(statement))


def test_read_statement_rejects_unknown_format():
    with pytest.raises(InvalidStatementError):
        read_statement(WRONG_COLUMNS)


def test_read_statement_names_supported_banks():
    with pytest.raises(InvalidStatementError) as error:
        read_statement(WRONG_COLUMNS)
    for reader in READERS:
        assert reader.bank_name in str(error.value)
