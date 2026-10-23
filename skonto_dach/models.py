# -*- coding: utf-8 -*-
"""
Data models for DACH Skonto & Effektivzins-Rechner 2026.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SkontoInvoice:
    """Represents an invoice with payment terms."""
    gross_amount: float
    skonto_rate_pct: float
    skonto_days: int
    netto_days: int
    bank_interest_rate_pct: float = 11.5
    country: str = "DE"
    tax_rate_pct: float = 19.0
    days_in_year: int = 360  # Kaufmännische Zinsmethode (30/360)


@dataclass
class TaxCorrection:
    """Tax and Vorsteuer correction details according to § 17 UStG / Art. 41 MWSTG."""
    country: str
    tax_rate_pct: float
    skonto_gross: float
    skonto_netto: float
    tax_correction_amount: float


@dataclass
class SkontoResult:
    """Complete financial calculation result."""
    gross_amount: float
    skonto_rate_pct: float
    skonto_amount: float
    payment_with_skonto: float
    credit_period_days: int
    effective_interest_rate_pa: float
    bank_interest_rate_pa: float
    bank_financing_cost: float
    net_benefit_vs_bank: float
    breakeven_bank_rate_pa: float
    recommendation: str
    tax_correction: TaxCorrection
