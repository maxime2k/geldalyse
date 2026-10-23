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
    
    return merchant