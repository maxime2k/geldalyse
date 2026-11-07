from pathlib import Path

import pytest

from geldalyse.readers.fortis import FortisReader
from geldalyse.readers.ing import INGReader

FIXTURES_DIR = Path(__file__).parents[1] / "fixtures"
ING_SAMPLE = FIXTURES_DIR / "ing_export_sample.csv"
ING_HEADER_ONLY = FIXTURES_DIR / "ing_header_only.csv"
FORTIS_SAMPLE = FIXTURES_DIR / "fortis_export_sample.csv"
FORTIS_HEADER_ONLY = FIXTURES_DIR / "fortis_header_only.csv"
WRONG_COLUMNS = FIXTURES_DIR / "wrong_format.csv"
EMPTY_FILE = FIXTURES_DIR / "empty.csv"

SAMPLE_STATEMENTS = [
    pytest.param(ING_SAMPLE, id="ing"),
    pytest.param(FORTIS_SAMPLE, id="fortis"),
]

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
