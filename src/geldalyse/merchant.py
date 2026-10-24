"""Extract the merchant (or counterparty) name from an ING description.

Rules, by family of description:
- Card payment ("PAIEMENT ..."): 3rd segment between " - "
- Cash withdrawal ("RETRAIT D'ESPÈCES ..."): the fixed value "RETRAIT D'ESPÈCES"
- Transfer ("VIREMENT ..."): text between "DE:" or "VERS:" and the next " - "
- Bank operation ("DÉCOMPTE DE FRAIS"): the fixed value "FRAIS COMPTE ING"
- Bank operation ("INTÉRÊTS-FRAIS"): the fixed value "INTÉRÊTS COMPTE ING"
- Anything else: the description, in capital case
"""

import pandas as pd

SEPARATOR = " - "
FIXED_NAMES = {
    "RETRAIT D'ESPÈCES": "RETRAIT D'ESPÈCES",
    "DÉCOMPTE DE FRAIS": "FRAIS COMPTE ING",
    "INTÉRÊTS-FRAIS":"INTÉRÊTS COMPTE ING"
}
TRANSFER_PREFIX = "VIREMENT"
TRANSFER_MARKERS = ("DE: ", "VERS: ")

def extract_merchant(label: str) -> str:
    """Return a short, readable name for a bank transaction description."""

    # Normalize here too, so the output is uniform whatever the source.
    label = label.upper()

    # Fixed names first: these descriptions have no " - " segments.
    for prefix, name in FIXED_NAMES.items():
        if label.startswith(prefix):
            return name
        
    #Transfer rule: text between "DE:" or "VERS:" and the next " - "
    if label.startswith(TRANSFER_PREFIX):
        for marker in TRANSFER_MARKERS:
            if marker in label:
                after_marker = label.partition(marker)[2]
                return after_marker.split(SEPARATOR)[0]
        return label
   
    # Spaces matter: city names such as LOUVAIN-LA-NE contain hyphens.
    segments = label.split(SEPARATOR)
    if len(segments) < 3:
        return label
    merchant = segments[2]
    merchant_name = _remove_postal_code(name=merchant)
    
    return merchant_name


def _remove_postal_code(name: str) -> str:
    """Remove a trailing Belgian postal code (4 digits) from a name."""

    segments = name.split()
    if segments and segments[-1].isdigit() and len(segments[-1]) == 4:
        segments.pop()

    return " ".join(segments)