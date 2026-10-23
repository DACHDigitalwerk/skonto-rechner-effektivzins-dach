# -*- coding: utf-8 -*-
"""
DACH Skonto-, Zahlungsziel- & Lieferantenkredit-Rechner 2026.
"""

from .models import SkontoInvoice, SkontoResult, TaxCorrection
from .rates import COUNTRY_CONFIGS, get_country_config
from .calculator import calculate_skonto
from .validator import validate_invoice

__version__ = "1.0.0"
__author__ = "DACH Digitalwerk"
__all__ = [
    "SkontoInvoice",
    "SkontoResult",
    "TaxCorrection",
    "COUNTRY_CONFIGS",
    "get_country_config",
    "calculate_skonto",
    "validate_invoice"
]
