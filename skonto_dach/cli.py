# -*- coding: utf-8 -*-
"""
Command-Line Interface (CLI) for DACH Skonto & Effektivzins-Rechner 2026.
Entrypoint: dach-skonto
"""

import sys
import argparse
import json
from typing import List, Optional
from .models import SkontoInvoice
from .calculator import calculate_skonto
from .rates import get_country_config


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dach-skonto",
        description="DACH Skonto-, Zahlungsziel- & Effektivzins-Rechner 2026 (DE, AT, CH)"
    )
    parser.add_argument(
        "--amount", "-a",
        type=float,
        required=True,
        help="Rechnungsbetrag brutto (z.B. 10000.0)"
    )
    parser.add_argument(
        "--skonto-rate", "-s",
        type=float,
        default=2.0,
        help="Gewaehrter Skontosatz in Prozent (z.B. 2.0 oder 3.0)"
    )
    parser.add_argument(
        "--skonto-days", "-d",
        type=int,
        default=10,
        help="Skontofrist in Tagen (z.B. 10 oder 14)"
    )
    parser.add_argument(
        "--netto-days", "-n",
        type=int,
        default=30,
        help="Nettozahlungsziel in Tagen (z.B. 30 oder 60)"
    )
    parser.add_argument(
        "--bank-rate", "-b",
        type=float,
        default=None,
        help="Sollzinssatz des Bank-Kontokorrentkredits p.a. in Prozent (Standard: 11.5 Prozent DE/AT, 9.5 Prozent CH)"
    )
    parser.add_argument(
        "--country", "-c",
        choices=["DE", "AT", "CH", "de", "at", "ch"],
        default="DE",
        help="Laendercode: DE (Deutschland), AT (Oesterreich), CH (Schweiz)"
    )
    parser.add_argument(
        "--tax-rate", "-t",
        type=float,
        default=None,
        help="Umsatzsteuersatz in Prozent (z.B. 19.0 fuer DE, 20.0 fuer AT, 8.1 fuer CH)"
    )
    parser.add_argument(
        "--days-in-year", "-y",
        type=int,
        choices=[360, 365, 366],
        default=360,
        help="Zinsberechnungsmethode: 360 (deutsche kaufmaennische Methode 30/360) oder 365 (act/365)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Ausgabe als maschinenlesbares JSON-Format"
    )
    return parser


def format_currency(val: float, symbol: str) -> str:
    return f"{val:,.2f} {symbol}".replace(",", "X").replace(".", ",").replace("X", ".")


def run_cli(args: Optional[List[str]] = None) -> int:
    parser = create_parser()
    try:
        parsed = parser.parse_args(args)
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 0

    country = parsed.country.upper()
    cfg = get_country_config(country)
    sym = cfg["currency_symbol"]

    try:
        res = calculate_skonto(
            gross_amount=parsed.amount,
            skonto_rate_pct=parsed.skonto_rate,
            skonto_days=parsed.skonto_days,
            netto_days=parsed.netto_days,
            bank_interest_rate_pct=parsed.bank_rate,
            country=country,
            tax_rate_pct=parsed.tax_rate,
            days_in_year=parsed.days_in_year
        )
    except Exception as err:
        sys.stderr.write(f"Fehler: {err}\n")
        return 1

    if parsed.json:
        data = {
            "country": country,
            "currency": cfg["currency"],
            "currency_symbol": sym,
            "gross_amount": res.gross_amount,
            "skonto_rate_pct": res.skonto_rate_pct,
            "skonto_amount": res.skonto_amount,
            "payment_with_skonto": res.payment_with_skonto,
            "credit_period_days": res.credit_period_days,
            "effective_interest_rate_pa": res.effective_interest_rate_pa,
            "bank_interest_rate_pa": res.bank_interest_rate_pa,
            "bank_financing_cost": res.bank_financing_cost,
            "net_benefit_vs_bank": res.net_benefit_vs_bank,
            "breakeven_bank_rate_pa": res.breakeven_bank_rate_pa,
            "recommendation": res.recommendation,
            "tax_correction": {
                "tax_rate_pct": res.tax_correction.tax_rate_pct,
                "skonto_gross": res.tax_correction.skonto_gross,
                "skonto_netto": res.tax_correction.skonto_netto,
                "tax_correction_amount": res.tax_correction.tax_correction_amount,
                "legal_basis": cfg["tax_legal_basis"]
            }
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0

    # Human readable formatted output
    print("=" * 68)
    print(f" DACH SKONTO- & EFFEKTIVZINS-RECHNER 2026 [{cfg['name']}]")
    print("=" * 68)
    print(f" Rechnungsbetrag (Brutto):     {format_currency(res.gross_amount, sym)}")
    print(f" Skontobedingung:             {res.skonto_rate_pct:.1f} % innerhalb {parsed.skonto_days} Tagen ({parsed.netto_days} Tage netto)")
    print(f" Skonto-Betrag (Ersparnis):   {format_currency(res.skonto_amount, sym)}")
    print(f" Ueberweisungsbetrag (Skonto): {format_currency(res.payment_with_skonto, sym)}")
    print(f" Kreditperiode:               {res.credit_period_days} Tage ({parsed.netto_days} - {parsed.skonto_days})")
    print("-" * 68)
    print(f" EFFEKTIVER JAHRESZINS (p.a.): {res.effective_interest_rate_pa:.2f} % p.a.")
    print(f" Sollzins Banklinie (p.a.):    {res.bank_interest_rate_pa:.2f} % p.a.")
    print(f" Zinskosten Kontokorrent:      {format_currency(res.bank_financing_cost, sym)}")
    print(f" Reingewinn bei Bankkredit:    {'+' if res.net_benefit_vs_bank >= 0 else ''}{format_currency(res.net_benefit_vs_bank, sym)}")
    print(f" Break-Even Bankzinssatz:      {res.breakeven_bank_rate_pa:.2f} % p.a.")
    print("-" * 68)
    print(f" Vorsteuerkorrektur ({cfg['tax_legal_basis'].split('(')[0].strip()}):")
    print(f"  • Skonto Netto:              {format_currency(res.tax_correction.skonto_netto, sym)}")
    print(f"  • Vorsteuer-Korrektur ({res.tax_correction.tax_rate_pct:.1f}%): {format_currency(res.tax_correction.tax_correction_amount, sym)}")
    print("=" * 68)
    print(f" Empfehlung: {res.recommendation}")
    print("=" * 68)
    return 0


def main():
    sys.exit(run_cli())


if __name__ == "__main__":
    main()
