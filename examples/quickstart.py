# -*- coding: utf-8 -*-
"""
Quickstart example for skonto_dach.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from skonto_dach import calculate_skonto, SkontoInvoice

def main():
    print("--- 1. Direkter Aufruf mit Parametern ---")
    res1 = calculate_skonto(
        gross_amount=15000.0,
        skonto_rate_pct=2.0,
        skonto_days=10,
        netto_days=30,
        bank_interest_rate_pct=11.5,
        country="DE",
        tax_rate_pct=19.0
    )
    print(f"Rechnungsbetrag:      {res1.gross_amount:.2f} €")
    print(f"Skonto-Ersparnis:     {res1.skonto_amount:.2f} €")
    print(f"Effektiver Jahreszins: {res1.effective_interest_rate_pa:.2f} % p.a.")
    print(f"Bank-Zinskosten:       {res1.bank_financing_cost:.2f} €")
    print(f"Reingewinn bei Kredit: +{res1.net_benefit_vs_bank:.2f} €")
    print(f"Vorsteuerkorrektur:    {res1.tax_correction.tax_correction_amount:.2f} € (§ 17 UStG)")
    print(f"Empfehlung:            {res1.recommendation}\n")

    print("--- 2. Verwendung mit Typed Dataclass (Schweiz) ---")
    inv_ch = SkontoInvoice(
        gross_amount=25000.0,
        skonto_rate_pct=3.0,
        skonto_days=14,
        netto_days=30,
        bank_interest_rate_pct=9.5,
        country="CH",
        tax_rate_pct=8.1
    )
    res_ch = calculate_skonto(inv_ch)
    print(f"Rechnungsbetrag:      {res_ch.gross_amount:.2f} CHF")
    print(f"Skonto-Ersparnis:     {res_ch.skonto_amount:.2f} CHF")
    print(f"Effektiver Jahreszins: {res_ch.effective_interest_rate_pa:.2f} % p.a.")
    print(f"MWST-Korrektur:        {res_ch.tax_correction.tax_correction_amount:.2f} CHF (Art. 41 MWSTG)")
    print(f"Reingewinn bei Kredit: +{res_ch.net_benefit_vs_bank:.2f} CHF")

if __name__ == "__main__":
    main()
