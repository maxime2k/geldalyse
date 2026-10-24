"""Shared pytest fixtures for the Geldalyse test suite."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def ing_sample() -> Path:
    """Path to the synthetic ING export used across tests."""
    return FIXTURES_DIR / "ing_export_sample.csv"