# -*- coding: utf-8 -*-
"""
Core calculation engine for DACH Skonto, effective interest rates and tax correction.
"""

from typing import Union
from .models import SkontoInvoice, SkontoResult, TaxCorrection
from .validator import validate_invoice
from .rates import get_country_config


def calculate_skonto(
    invoice: Union[SkontoInvoice, dict] = None,
    gross_amount: float = None,
    skonto_rate_pct: float = None,
    skonto_days: int = None,
    netto_days: int = None,
    bank_interest_rate_pct: float = None,
    country: str = "DE",
    tax_rate_pct: float = None,
    days_in_year: int = 360
) -> SkontoResult:
    """
    Calculate cash discount (Skonto), effective interest rate p.a. and compare against bank credit.

    Can be invoked with a SkontoInvoice instance or with individual keyword arguments.
    """
    if isinstance(invoice, SkontoInvoice):
        inv = invoice
    elif isinstance(invoice, dict):
        inv = SkontoInvoice(**invoice)
    else:
        cfg = get_country_config(country)
        if bank_interest_rate_pct is None:
            bank_interest_rate_pct = cfg["default_bank_rate"]
        if tax_rate_pct is None:
            tax_rate_pct = cfg["default_standard_vat"]

        inv = SkontoInvoice(
            gross_amount=float(gross_amount or 0.0),
            skonto_rate_pct=float(skonto_rate_pct or 0.0),
            skonto_days=int(skonto_days or 0),
            netto_days=int(netto_days or 0),
            bank_interest_rate_pct=float(bank_interest_rate_pct),
            country=country.upper(),
            tax_rate_pct=float(tax_rate_pct),
            days_in_year=int(days_in_year)
        )

    validate_invoice(inv)

    credit_period_days = inv.netto_days - inv.skonto_days
    skonto_amount = round(inv.gross_amount * (inv.skonto_rate_pct / 100.0), 2)
    payment_with_skonto = round(inv.gross_amount - skonto_amount, 2)

    if inv.skonto_rate_pct > 0 and credit_period_days > 0:
        # Exakte finanzmathematische Effektivzinsformel
        effektiv_zins = (
            (inv.skonto_rate_pct / (100.0 - inv.skonto_rate_pct))
            * (inv.days_in_year / credit_period_days)
            * 100.0
        )
    else:
        effektiv_zins = 0.0

    if inv.skonto_rate_pct > 0 and payment_with_skonto > 0 and credit_period_days > 0 and inv.bank_interest_rate_pct > 0:
        bank_financing_cost = round(
            (payment_with_skonto * (inv.bank_interest_rate_pct / 100.0) * credit_period_days) / inv.days_in_year,
            2
        )
    else:
        bank_financing_cost = 0.0

    net_benefit = round(skonto_amount - bank_financing_cost, 2)
    breakeven_bank_rate = round(effektiv_zins, 2)

    # Tax & Vorsteuerkorrektur (§ 17 UStG / § 16 öst. UStG / Art. 41 MWSTG)
    if inv.tax_rate_pct > 0:
        factor = 1.0 + (inv.tax_rate_pct / 100.0)
        skonto_netto = round(skonto_amount / factor, 2)
        tax_correction_amount = round(skonto_amount - skonto_netto, 2)
    else:
        skonto_netto = skonto_amount
        tax_correction_amount = 0.0

    tax_corr = TaxCorrection(
        country=inv.country,
        tax_rate_pct=inv.tax_rate_pct,
        skonto_gross=skonto_amount,
        skonto_netto=skonto_netto,
        tax_correction_amount=tax_correction_amount
    )

    if inv.skonto_rate_pct <= 0:
        rec = "Kein Skonto gewährt: Reguläre Zahlung bei Fälligkeit am Nettoziel."
    elif effektiv_zins > inv.bank_interest_rate_pct:
        ratio = (effektiv_zins / (inv.bank_interest_rate_pct or 1.0))
        rec = (
            f"Skonto ziehen! Der Skonto-Effektivzins ({effektiv_zins:.2f}% p.a.) ist "
            f"{ratio:.1f}-mal höher als der Kontokorrentzins ({inv.bank_interest_rate_pct:.2f}% p.a.). "
            f"Netto-Finanzgewinn: +{net_benefit:.2f} {get_country_config(inv.country)['currency_symbol']}."
        )
    else:
        rec = (
            f"Zahlungsziel voll ausnutzen. Der Bankkredit ({inv.bank_interest_rate_pct:.2f}% p.a.) "
            f"ist ausnahmsweise teurer als der Skonto-Effektivzins ({effektiv_zins:.2f}% p.a.)."
        )

    return SkontoResult(
        gross_amount=round(inv.gross_amount, 2),
        skonto_rate_pct=round(inv.skonto_rate_pct, 2),
        skonto_amount=skonto_amount,
        payment_with_skonto=payment_with_skonto,
        credit_period_days=credit_period_days,
        effective_interest_rate_pa=round(effektiv_zins, 2),
        bank_interest_rate_pa=round(inv.bank_interest_rate_pct, 2),
        bank_financing_cost=bank_financing_cost,
        net_benefit_vs_bank=net_benefit,
        breakeven_bank_rate_pa=breakeven_bank_rate,
        recommendation=rec,
        tax_correction=tax_corr
    )
