"""Extract the merchant (or counterparty) name from an ING description.

Rules, by family of description:
- Card payment ("PAIEMENT ..."): 3rd segment between " - "
- Cash withdrawal ("RETRAIT D'ESPÈCES ..."): same rule as card payments
- Transfer ("VIREMENT ..."): text between "DE:" or "VERS:" and the next " - "
- Bank operation ("DÉCOMPTE DE FRAIS", "INTÉRÊTS"): the fixed value "ING"
- Anything else: the description, unchanged
"""

import pandas as pd

def extract_merchant(label: str) -> str:
    label_list = label.split(" - ")
    merchant = label_list[2]
    merchant_name = _remove_postal_code(name=merchant)
    
    return merchant_name


def _remove_postal_code(name: str) -> str:
    name_list = name.split()
    if name_list and name_list[-1].isdigit() and len(name_list[-1]) == 4:
        name_list.pop()

    return " ".join(name_list)