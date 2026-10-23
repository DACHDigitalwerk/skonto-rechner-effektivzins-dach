# -*- coding: utf-8 -*-
"""
Unit tests for skonto_dach.calculator and models.
"""

import pytest
from skonto_dach.models import SkontoInvoice, SkontoResult
from skonto_dach.calculator import calculate_skonto
from skonto_dach.rates import get_country_config


def test_standard_skonto_2_percent():
    """Test standard 2% within 10 days, 30 days net in Germany."""
    res = calculate_skonto(
        gross_amount=10000.0,
        skonto_rate_pct=2.0,
        skonto_days=10,
        netto_days=30,
        bank_interest_rate_pct=11.5,
        country="DE",
        tax_rate_pct=19.0,
        days_in_year=360
    )
    assert res.gross_amount == 10000.0
    assert res.skonto_amount == 200.0
    assert res.payment_with_skonto == 9800.0
    assert res.credit_period_days == 20
    assert res.effective_interest_rate_pa == 36.73
    assert res.bank_interest_rate_pa == 11.5
    assert res.bank_financing_cost == 62.61
    assert res.net_benefit_vs_bank == 137.39
    assert res.breakeven_bank_rate_pa == 36.73
    assert "Skonto ziehen" in res.recommendation


def test_skonto_3_percent_14_days():
    """Test 3% within 14 days, 30 days net."""
    res = calculate_skonto(
        gross_amount=10000.0,
        skonto_rate_pct=3.0,
        skonto_days=14,
        netto_days=30,
        bank_interest_rate_pct=12.0,
        country="DE"
    )
    assert res.skonto_amount == 300.0
    assert res.credit_period_days == 16
    assert res.effective_interest_rate_pa == 69.59
    assert res.net_benefit_vs_bank > 200.0


def test_365_days_method():
    """Test act/365 day count convention."""
    res = calculate_skonto(
        gross_amount=10000.0,
        skonto_rate_pct=2.0,
        skonto_days=10,
        netto_days=30,
        days_in_year=365
    )
    assert res.effective_interest_rate_pa == 37.24


def test_austria_tax_correction_20_percent():
    """Test Austrian standard VAT (20%) tax correction."""
    res = calculate_skonto(
        gross_amount=12000.0,
        skonto_rate_pct=2.0,
        skonto_days=10,
        netto_days=30,
        country="AT",
        tax_rate_pct=20.0
    )
    assert res.skonto_amount == 240.0
    assert res.tax_correction.country == "AT"
    assert res.tax_correction.skonto_netto == 200.0
    assert res.tax_correction.tax_correction_amount == 40.0


def test_switzerland_tax_correction_8_1_percent():
    """Test Swiss MWST (8.1%) tax correction."""
    res = calculate_skonto(
        gross_amount=10810.0,
        skonto_rate_pct=2.0,
        skonto_days=10,
        netto_days=30,
        country="CH",
        tax_rate_pct=8.1
    )
    assert res.skonto_amount == 216.20
    assert res.tax_correction.country == "CH"
    assert res.tax_correction.skonto_netto == 200.0
    assert res.tax_correction.tax_correction_amount == 16.20


def test_reduced_tax_rate_germany():
    """Test reduced 7% VAT rate in Germany."""
    res = calculate_skonto(
        gross_amount=10700.0,
        skonto_rate_pct=2.0,
        skonto_days=10,
        netto_days=30,
        country="DE",
        tax_rate_pct=7.0
    )
    assert res.skonto_amount == 214.0
    assert res.tax_correction.skonto_netto == 200.0
    assert res.tax_correction.tax_correction_amount == 14.0


def test_zero_tax_rate():
    """Test tax-exempt invoice."""
    res = calculate_skonto(
        gross_amount=5000.0,
        skonto_rate_pct=2.0,
        skonto_days=10,
        netto_days=30,
        tax_rate_pct=0.0
    )
    assert res.tax_correction.skonto_netto == 100.0
    assert res.tax_correction.tax_correction_amount == 0.0


def test_zero_skonto_rate():
    """Test invoice without cash discount."""
    res = calculate_skonto(
        gross_amount=5000.0,
        skonto_rate_pct=0.0,
        skonto_days=0,
        netto_days=30
    )
    assert res.skonto_amount == 0.0
    assert res.effective_interest_rate_pa == 0.0
    assert res.net_benefit_vs_bank == 0.0
    assert "Kein Skonto" in res.recommendation


def test_unfavorable_skonto_scenario():
    """Test rare scenario where bank interest exceeds skonto effective rate."""
    res = calculate_skonto(
        gross_amount=10000.0,
        skonto_rate_pct=1.0,
        skonto_days=10,
        netto_days=90,  # 80 days credit period -> eff rate ~4.55%
        bank_interest_rate_pct=12.0
    )
    assert res.effective_interest_rate_pa == 4.55
    assert res.bank_financing_cost > res.skonto_amount
    assert res.net_benefit_vs_bank < 0
    assert "Zahlungsziel voll ausnutzen" in res.recommendation


def test_breakeven_bank_rate():
    """Test that at break-even rate, net benefit is zero."""
    res = calculate_skonto(
        gross_amount=10000.0,
        skonto_rate_pct=2.0,
        skonto_days=10,
        netto_days=30,
        bank_interest_rate_pct=36.7347  # exactly equal to effective rate
    )
    assert abs(res.net_benefit_vs_bank) <= 0.05


def test_invoice_as_dataclass_input():
    """Test passing SkontoInvoice instance."""
    inv = SkontoInvoice(
        gross_amount=25000.0,
        skonto_rate_pct=2.5,
        skonto_days=7,
        netto_days=21,
        bank_interest_rate_pct=10.0,
        country="DE"
    )
    res = calculate_skonto(inv)
    assert res.gross_amount == 25000.0
    assert res.credit_period_days == 14
    assert res.effective_interest_rate_pa > 65.0


def test_invoice_as_dict_input():
    """Test passing dictionary input."""
    d = {
        "gross_amount": 5000.0,
        "skonto_rate_pct": 2.0,
        "skonto_days": 10,
        "netto_days": 30
    }
    res = calculate_skonto(d)
    assert res.gross_amount == 5000.0
    assert res.skonto_amount == 100.0


def test_validation_gross_amount_zero_or_negative():
    """Ensure gross amount <= 0 is rejected."""
    with pytest.raises(ValueError, match="Rechnungsbetrag"):
        calculate_skonto(gross_amount=0.0, skonto_rate_pct=2.0, skonto_days=10, netto_days=30)
    with pytest.raises(ValueError, match="Rechnungsbetrag"):
        calculate_skonto(gross_amount=-100.0, skonto_rate_pct=2.0, skonto_days=10, netto_days=30)


def test_validation_skonto_rate_out_of_bounds():
    """Ensure invalid skonto rate is rejected."""
    with pytest.raises(ValueError, match="Skontosatz"):
        calculate_skonto(gross_amount=1000.0, skonto_rate_pct=-1.0, skonto_days=10, netto_days=30)
    with pytest.raises(ValueError, match="Skontosatz"):
        calculate_skonto(gross_amount=1000.0, skonto_rate_pct=100.0, skonto_days=10, netto_days=30)


def test_validation_skonto_days_negative():
    """Ensure negative skonto days are rejected."""
    with pytest.raises(ValueError, match="Skontofrist"):
        calculate_skonto(gross_amount=1000.0, skonto_rate_pct=2.0, skonto_days=-5, netto_days=30)


def test_validation_netto_days_zero_or_negative():
    """Ensure non-positive netto days are rejected."""
    with pytest.raises(ValueError, match="Nettozahlungsziel"):
        calculate_skonto(gross_amount=1000.0, skonto_rate_pct=2.0, skonto_days=10, netto_days=0)


def test_validation_skonto_days_greater_than_netto_days():
    """Ensure skonto days >= netto days is rejected when skonto > 0."""
    with pytest.raises(ValueError, match="muss kleiner sein als das Nettozahlungsziel"):
        calculate_skonto(gross_amount=1000.0, skonto_rate_pct=2.0, skonto_days=30, netto_days=30)
    with pytest.raises(ValueError, match="muss kleiner sein als das Nettozahlungsziel"):
        calculate_skonto(gross_amount=1000.0, skonto_rate_pct=2.0, skonto_days=40, netto_days=30)


def test_validation_invalid_days_in_year():
    """Ensure invalid days in year are rejected."""
    with pytest.raises(ValueError, match="Jahrestage-Methode"):
        calculate_skonto(gross_amount=1000.0, skonto_rate_pct=2.0, skonto_days=10, netto_days=30, days_in_year=350)


def test_validation_negative_bank_rate():
    """Ensure negative bank interest rate is rejected."""
    with pytest.raises(ValueError, match="Bankzinssatz"):
        calculate_skonto(gross_amount=1000.0, skonto_rate_pct=2.0, skonto_days=10, netto_days=30, bank_interest_rate_pct=-2.0)
