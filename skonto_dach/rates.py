# -*- coding: utf-8 -*-
"""
DACH Statutory tax rates, banking standards and defaults for 2026.
"""

from typing import Dict, Any

COUNTRY_CONFIGS: Dict[str, Dict[str, Any]] = {
    "DE": {
        "name": "Deutschland",
        "currency": "EUR",
        "currency_symbol": "€",
        "default_standard_vat": 19.0,
        "default_reduced_vat": 7.0,
        "default_bank_rate": 11.5,
        "tax_legal_basis": "§ 17 Abs. 1 UStG (Minderung der Bemessungsgrundlage)",
        "interest_legal_basis": "§ 288 Abs. 2 BGB (B2B-Verzugszinsen 9 Prozentpunkte über Basiszinssatz)",
        "default_days_in_year": 360,
    },
    "AT": {
        "name": "Österreich",
        "currency": "EUR",
        "currency_symbol": "€",
        "default_standard_vat": 20.0,
        "default_reduced_vat": 10.0,
        "default_bank_rate": 11.5,
        "tax_legal_basis": "§ 16 Abs. 1 öst. UStG 1994 (Änderung der Bemessungsgrundlage)",
        "interest_legal_basis": "§ 456 UGB (9,2 Prozentpunkte über Basiszinssatz im B2B-Geschäftsverkehr)",
        "default_days_in_year": 360,
    },
    "CH": {
        "name": "Schweiz",
        "currency": "CHF",
        "currency_symbol": "CHF",
        "default_standard_vat": 8.1,
        "default_reduced_vat": 2.6,
        "default_bank_rate": 9.5,
        "tax_legal_basis": "Art. 41 MWSTG (Nachträgliche Entgeltminderung)",
        "interest_legal_basis": "Art. 104 OR (Gesetzlicher Verzugszins 5 Prozent p.a.)",
        "default_days_in_year": 360,
    }
}


def get_country_config(country: str) -> Dict[str, Any]:
    """Return country configuration or default to DE."""
    c = country.upper()
    return COUNTRY_CONFIGS.get(c, COUNTRY_CONFIGS["DE"])
