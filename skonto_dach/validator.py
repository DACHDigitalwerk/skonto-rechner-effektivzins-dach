# -*- coding: utf-8 -*-
"""
Input validation for Skonto and payment term parameters.
"""

from .models import SkontoInvoice


def validate_invoice(invoice: SkontoInvoice) -> None:
    """Validate parameters according to commercial arithmetic standards."""
    if invoice.gross_amount <= 0:
        raise ValueError("Rechnungsbetrag muss größer als 0 sein.")

    if invoice.skonto_rate_pct < 0 or invoice.skonto_rate_pct >= 100:
        raise ValueError("Skontosatz muss zwischen 0 und 100 Prozent liegen.")

    if invoice.skonto_days < 0:
        raise ValueError("Skontofrist darf nicht negativ sein.")

    if invoice.netto_days <= 0:
        raise ValueError("Nettozahlungsziel muss größer als 0 Tage sein.")

    if invoice.skonto_days >= invoice.netto_days and invoice.skonto_rate_pct > 0:
        raise ValueError(
            f"Skontofrist ({invoice.skonto_days} Tage) muss kleiner sein als das "
            f"Nettozahlungsziel ({invoice.netto_days} Tage), um eine Kreditperiode zu bilden."
        )

    if invoice.bank_interest_rate_pct < 0:
        raise ValueError("Bankzinssatz darf nicht negativ sein.")

    if invoice.tax_rate_pct < 0:
        raise ValueError("Umsatzsteuersatz darf nicht negativ sein.")

    if invoice.days_in_year not in (360, 365, 366):
        raise ValueError("Jahrestage-Methode muss 360 (kaufmännisch) oder 365/366 (Effektivtage) sein.")
