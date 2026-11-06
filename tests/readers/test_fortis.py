from io import StringIO

import pandas as pd
import pytest

from geldalyse.readers import FortisReader, InvalidStatementError
from geldalyse.readers.fortis import convert_amount, extract_counterparty
from geldalyse.schema import (
    CARD,
    CASH,
    CASH_WITHDRAWAL_NAME,
    MISSING_LABEL,
    OTHER,
    TRANSFER,
)

FORTIS_HEADER = (
    "Nº de séquence;Date d'exécution;Date valeur;Montant;Devise du compte;"
    "Numéro de compte;Type de transaction;Contrepartie;Nom de la contrepartie;"
    "Communication;Détails;Statut;Motif du refus"
)


def fortis_csv(
    amount: str = "-12.50",
    value_date: str = "03/01/2026",
    execution_date: str = "04/01/2026",
    operation_type_text: str = "Virement en euros",
    counterparty: str = "NOM FICTIF",
    details: str = "VIREMENT EN EUROS VERS NOM FICTIF REFERENCE BANQUE : 0000000000",
    status: str = "Accepté",
) -> StringIO:
    """Return an in-memory Fortis export with one transaction."""
    row = (
        f"2026-00001;{execution_date};{value_date};{amount};EUR;BE00000000000000;"
        f"{operation_type_text};BE00000000000000;{counterparty};;{details};{status};"
    )
    return StringIO(f"{FORTIS_HEADER}\n{row}\n")


@pytest.mark.parametrize(
    "amount",
    [
        "abc",
        "1232.253",
        "1.325,20",
        "1,255.20",
        "",
        "12 50",
        "12.",
        "12,",
        "--5",
    ],
)
def test_convert_amount_rejects_invalid_amounts(amount):
    with pytest.raises(ValueError):
        convert_amount(amount)


@pytest.mark.parametrize(
    "amount, expected",
    [
        ("0.15", 0.15),
        ("0,17", 0.17),
        ("1250", 1250),
        ("-69.50", -69.50),
        ("-14,00", -14.00),
        ("200.1", 200.1),
        ("100,05", 100.05),
        ("1584,00", 1584.00),
        ("3594.89", 3594.89),
    ],
)
def test_convert_amount_reads_valid_amounts(amount, expected):
    assert convert_amount(amount) == expected


def test_fortis_reader_rejects_invalid_amount():
    with pytest.raises(InvalidStatementError, match="Ligne 2"):
        FortisReader().read(fortis_csv(amount="15bc"))


def test_fortis_reader_rejects_invalid_date():
    with pytest.raises(InvalidStatementError, match="Ligne 2"):
        FortisReader().read(fortis_csv(value_date="2025-15-22"))


def test_fortis_reader_reads_value_date():
    transactions = FortisReader().read(
        fortis_csv(execution_date="04/01/2026", value_date="03/01/2026")
    )

    assert transactions["date"].iloc[0] == pd.Timestamp(2026, 1, 3)


def test_fortis_reader_return_operation_type():
    transactions = FortisReader().read(
        fortis_csv(operation_type_text="virement en euros")
    )

    assert transactions["operation_type"].iloc[0] == TRANSFER


def test_fortis_reader_return_unknow_operation_type():
    transactions = FortisReader().read(
        fortis_csv(operation_type_text="frais tenue de compte")
    )

    assert transactions["operation_type"].iloc[0] == OTHER


@pytest.mark.parametrize("label", ["", "   "])
def test_fortis_reader_replaces_missing_label(label):
    transactions = FortisReader().read(fortis_csv(details=label))
    assert transactions["label"].iloc[0] == MISSING_LABEL


@pytest.mark.parametrize(
    "name, operation_type, label, expected",
    [
        ("ami fictif", TRANSFER, "virement de ami fictif", "AMI FICTIF"),
        (
            "",
            CARD,
            (
                "PAIEMENT AVEC LA CARTE DE DEBIT NUMERO 0000 XXXX XXXX 0000 "
                "MAGASIN FICTIF 0000 1000 VILLE 30/12/2025 BANCONTACT REFERENCE BANQUE"
            ),
            "MAGASIN FICTIF",
        ),
        (
            "",
            CARD,
            (
                "PAIEMENT AVEC LA CARTE DE DEBIT NUMERO 0000 XXXX XXXX 0000 "
                "ENSEIGNE FICTIVE 29/12/2025 VISA DEBIT"
            ),
            "ENSEIGNE FICTIVE",
        ),
        ("", CARD, "PAIEMENT SANS DETAIL", "PAIEMENT SANS DETAIL"),
        (
            "",
            CASH,
            "RETRAIT D'ESPECES EN EUROS A D'AUTRES DISTRIBUTEURS ",
            CASH_WITHDRAWAL_NAME,
        ),
        (
            "",
            CARD,
            (
                "PAIEMENT AVEC LA CARTE DE DEBIT NUMERO 0000 XXXX XXXX 0000 0000 "
                "MAGASIN FICTIF QUARTIER 1000 VILLE 30/12/2025 BANCONTACT"
            ),
            "MAGASIN FICTIF QUARTIER",
        ),
        (
            "",
            CARD,
            (
                "PAIEMENT AVEC LA CARTE DE DEBIT NUMERO 0000 XXXX XXXX 0000 0000 "
                "ENSEIGNE FICTIVE 29/12/2025 VISA DEBIT"
            ),
            "ENSEIGNE FICTIVE",
        ),
        ("", OTHER, "FRAIS TENUE DE COMPTE", "FRAIS TENUE DE COMPTE"),
    ],
)
def test_extract_counterparty_returns_counterparty(
    name, operation_type, label, expected
):
    assert extract_counterparty(name, operation_type, label) == expected


def test_fortis_reader_uses_counterparty_name():
    transactions = FortisReader().read(fortis_csv(counterparty="ami fictif"))

    assert transactions["counterparty"].iloc[0] == "AMI FICTIF"


def test_fortis_reader_uses_missing_label_without_name_or_details():
    transactions = FortisReader().read(fortis_csv(counterparty="", details=""))

    assert transactions["counterparty"].iloc[0] == MISSING_LABEL
