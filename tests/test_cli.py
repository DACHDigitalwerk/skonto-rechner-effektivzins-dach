# -*- coding: utf-8 -*-
"""
Unit tests for skonto_dach.cli (dach-skonto command).
"""

import io
import json
import contextlib
import pytest
from skonto_dach.cli import run_cli


def test_cli_help():
    """Test CLI help screen returns 0."""
    buf_out = io.StringIO()
    buf_err = io.StringIO()
    with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
        code = run_cli(["--help"])
    assert code == 0
    assert "dach-skonto" in buf_out.getvalue()


def test_cli_standard_run():
    """Test standard CLI execution with formatted text output."""
    buf_out = io.StringIO()
    buf_err = io.StringIO()
    with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
        code = run_cli([
            "--amount", "10000.0",
            "--skonto-rate", "2.0",
            "--skonto-days", "10",
            "--netto-days", "30",
            "--bank-rate", "11.5",
            "--country", "DE"
        ])
    assert code == 0
    out = buf_out.getvalue()
    assert "EFFEKTIVER JAHRESZINS (p.a.): 36.73 % p.a." in out
    assert "Reingewinn bei Bankkredit:    +137,39 €" in out
    assert "Skonto ziehen" in out


def test_cli_json_output():
    """Test CLI with --json flag."""
    buf_out = io.StringIO()
    buf_err = io.StringIO()
    with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
        code = run_cli([
            "--amount", "10000.0",
            "--skonto-rate", "2.0",
            "--skonto-days", "10",
            "--netto-days", "30",
            "--json"
        ])
    assert code == 0
    data = json.loads(buf_out.getvalue())
    assert data["gross_amount"] == 10000.0
    assert data["skonto_amount"] == 200.0
    assert data["effective_interest_rate_pa"] == 36.73
    assert data["credit_period_days"] == 20
    assert "tax_correction" in data


def test_cli_austria_flag():
    """Test CLI with Austrian country flag."""
    buf_out = io.StringIO()
    buf_err = io.StringIO()
    with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
        code = run_cli([
            "--amount", "12000.0",
            "--skonto-rate", "2.0",
            "--skonto-days", "10",
            "--netto-days", "30",
            "--country", "AT",
            "--json"
        ])
    assert code == 0
    data = json.loads(buf_out.getvalue())
    assert data["country"] == "AT"
    assert data["tax_correction"]["tax_rate_pct"] == 20.0
    assert data["tax_correction"]["tax_correction_amount"] == 40.0


def test_cli_switzerland_flag():
    """Test CLI with Swiss country flag."""
    buf_out = io.StringIO()
    buf_err = io.StringIO()
    with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
        code = run_cli([
            "--amount", "10810.0",
            "--skonto-rate", "2.0",
            "--skonto-days", "10",
            "--netto-days", "30",
            "--country", "CH",
            "--json"
        ])
    assert code == 0
    data = json.loads(buf_out.getvalue())
    assert data["country"] == "CH"
    assert data["currency"] == "CHF"
    assert data["tax_correction"]["tax_rate_pct"] == 8.1
    assert data["tax_correction"]["tax_correction_amount"] == 16.20


def test_cli_validation_failure():
    """Test CLI returns 1 on invalid argument values."""
    buf_out = io.StringIO()
    buf_err = io.StringIO()
    with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
        code = run_cli([
            "--amount", "-500.0",
            "--skonto-rate", "2.0",
            "--skonto-days", "10",
            "--netto-days", "30"
        ])
    assert code == 1
    assert "Fehler" in buf_err.getvalue()


def test_cli_custom_bank_rate():
    """Test CLI custom bank rate."""
    buf_out = io.StringIO()
    buf_err = io.StringIO()
    with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
        code = run_cli([
            "--amount", "5000.0",
            "--skonto-rate", "3.0",
            "--skonto-days", "14",
            "--netto-days", "30",
            "--bank-rate", "14.5"
        ])
    assert code == 0
    assert "Sollzins Banklinie (p.a.):    14.50 % p.a." in buf_out.getvalue()


def test_cli_days_in_year_365():
    """Test CLI act/365 option."""
    buf_out = io.StringIO()
    buf_err = io.StringIO()
    with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
        code = run_cli([
            "--amount", "10000.0",
            "--skonto-rate", "2.0",
            "--skonto-days", "10",
            "--netto-days", "30",
            "--days-in-year", "365",
            "--json"
        ])
    assert code == 0
    data = json.loads(buf_out.getvalue())
    assert data["effective_interest_rate_pa"] == 37.24
