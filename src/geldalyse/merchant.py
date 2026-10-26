"""Extract the merchant (or counterparty) name from an ING description.

Rules, by family of description:
- Card payment ("PAIEMENT ..."): 3rd segment between " - " without the trailing postal code
- Cash withdrawal ("RETRAIT D'ESPÈCES ..."): the fixed value "RETRAIT D'ESPÈCES"
- Transfer ("VIREMENT ..."): text between "DE:" or "VERS:" and the next " - "
- Bank operation ("DÉCOMPTE DE FRAIS"): the fixed value "FRAIS COMPTE ING"
- Bank operation ("INTÉRÊTS-FRAIS"): the fixed value "INTÉRÊTS COMPTE ING"
- Anything else: the description, in in uppercase
"""


SEPARATOR = " - "

# Description prefix -> displayed name.
# A prefix must not be the start of another one placed after it.
FIXED_NAMES = {
    "RETRAIT D'ESPÈCES": "RETRAIT D'ESPÈCES",
    "DÉCOMPTE DE FRAIS": "FRAIS COMPTE ING",
    "INTÉRÊTS-FRAIS": "INTÉRÊTS COMPTE ING",
}

TRANSFER_PREFIX = "VIREMENT"
TRANSFER_RECEIVED_MARKER = "DE: "
TRANSFER_SENT_MARKER = "VERS: "
TRANSFER_MARKERS = (TRANSFER_RECEIVED_MARKER, TRANSFER_SENT_MARKER)

CARD_PAYMENT_PREFIX = "PAIEMENT"

def extract_merchant(label: str) -> str:
    """Return a short, readable name for a bank transaction description."""

    # Normalize here too, so the output is uniform whatever the source.
    label = label.upper()

    # 1. Fixed names first: these descriptions have no " - " segments.
    for prefix, name in FIXED_NAMES.items():
        if label.startswith(prefix):
            return name
        
    #2. Transfer rule: text between "DE:" or "VERS:" and the next " - "
    if label.startswith(TRANSFER_PREFIX):
        for marker in TRANSFER_MARKERS:
            if marker in label:
                after_marker = label.partition(marker)[2]
                return after_marker.split(SEPARATOR)[0]
        return label
    
    # 3. Not a card payment: no reliable rule, keep the description.
    if not label.startswith(CARD_PAYMENT_PREFIX):
        return label
    
    # 4. Card payment: 3rd segment, without the postal code.
    # Spaces matter: city names such as LOUVAIN-LA-NE contain hyphens.
    segments = label.split(SEPARATOR)
    if len(segments) < 3:
        return label
    merchant = segments[2]
    merchant_name = _remove_postal_code(name=merchant)
    
    return merchant_name


def _remove_postal_code(name: str) -> str:
    """Remove a trailing Belgian postal code (4 digits) from a name."""

    words = name.split()
    if words and words[-1].isdigit() and len(words[-1]) == 4:
        words.pop()

    return " ".join(words)


def is_received_transfer(label: str) -> bool:
    """Return True if the label is a transfer received from someone."""
    label = label.upper()

    return label.startswith(TRANSFER_PREFIX) and TRANSFER_RECEIVED_MARKER in label

