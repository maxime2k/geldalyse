"""How money moved, shared by all banks:
each reader maps its own descriptions to these types."""

STANDARD_COLUMNS = ["date", "label", "amount", "counterparty", "operation_type"]
MISSING_LABEL = "SANS DESCRIPTION"
CASH_WITHDRAWAL_NAME = "RETRAIT D'ESPÈCES"

CARD = "card"
MOBILE_PAYMENT = "mobile_payment"
TRANSFER = "transfer"
STANDING_ORDER = "standing_order"
DIRECT_DEBIT = "direct_debit"
CASH = "cash"
BANK_OPERATION = "bank_operation"
OTHER = "other"

OPERATION_TYPE_LABELS = {
    CARD: "Carte",
    MOBILE_PAYMENT: "Paiement mobile",
    TRANSFER: "Virement",
    STANDING_ORDER: "Ordre permanent",
    DIRECT_DEBIT: "Domiciliation",
    CASH: "Espèces",
    BANK_OPERATION: "Opération bancaire",
    OTHER: "Autre",
}
