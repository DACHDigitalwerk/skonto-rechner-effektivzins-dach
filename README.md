# DACH Skonto-, Zahlungsziel- & Lieferantenkredit-Rechner 2026 (Python & CLI `dach-skonto`)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-27%20passed-success.svg)](tests/)
[![Online Tool](https://img.shields.io/badge/Online%20Web--App-Live%20Rechner-teal.svg)](https://dach-digitalwerk.netlify.app/skonto-rechner-effektivzins/)

Offizielles Open-Source-Repository der browserbasierten Web-Applikation auf **[DACH Digitalwerk: Skonto- & Effektivzins-Rechner 2026](https://dach-digitalwerk.netlify.app/skonto-rechner-effektivzins/)**.

Berechnet finanzmathematisch exakt den **effektiven Jahreszins (p.a.)** von Skontovereinbarungen, vergleicht die Finanzierung über betriebliche **Kontokorrentkredite** und ermittelt die gesetzliche **Vorsteuer- und USt-Korrektur nach § 17 UStG** (Deutschland), **§ 16 UStG** (Österreich) und **Art. 41 MWSTG** (Schweiz).

---

## 💡 Warum Skontoverzicht der teuerste Kredit der Wirtschaft ist

Viele Unternehmen begleichen Rechnungen erst am Ende des Zahlungsziels (z. B. nach 30 Tagen), um scheinbar Liquidität zu schonen. Verzichtet ein Unternehmen jedoch beispielsweise auf **2 % Skonto bei 10 Tagen Skontofrist und 30 Tagen Zahlungsziel**, nimmt es für die verbleibenden 20 Tage faktisch einen Lieferantenkredit in Anspruch:

$$\text{Effektivzins p.a.} = \frac{\text{Skontosatz}}{100 - \text{Skontosatz}} \times \frac{360}{\text{Nettoziel} - \text{Skontofrist}} \times 100$$

$$\text{Effektivzins p.a.} = \frac{2}{98} \times \frac{360}{20} \times 100 = \mathbf{36{,}73\ \% \text{ p.a.}}$$

Selbst wenn das Geschäftskonto überzogen werden muss und die Hausbank **11,5 % bis 14,0 % Kontokorrentzins** verlangt, lohnt sich das Ziehen von Skonto fast ausnahmslos: Der Zinsgewinn aus der Skontoersparnis übersteigt die 20-tägigen Bankzinsen um das **3- bis 6-Fache**!

---

## 📊 Finanzierungsvergleich (Muster: 10.000 € Rechnung, 11,5 % Bankzins)

| Kondition | Kreditdauer | Skonto-Effektivzins | Bankzins (11,5 %) | Skontoertrag | Netto-Finanzgewinn |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **2 % in 10 Tagen, 30 Tage netto** | 20 Tage | **36,73 % p.a.** | 62,61 € | 200,00 € | **+137,39 €** |
| **3 % in 14 Tagen, 30 Tage netto** | 16 Tage | **70,10 % p.a.** | 50,09 € | 300,00 € | **+249,91 €** |
| **2 % in 8 Tagen, 14 Tage netto** | 6 Tage | **122,45 % p.a.** | 18,78 € | 200,00 € | **+181,22 €** |
| **1 % in 10 Tagen, 60 Tage netto** | 50 Tage | **7,27 % p.a.** | 158,04 € | 100,00 € | *-58,04 €* (Ausnahme) |

*Berechnung nach deutscher kaufmännischer Zinsmethode (30/360). Auch Zinsmethode act/365 konfigurierbar.*

---

## ⚖️ Vorsteuerkorrektur im DACH-Raum

Durch den Skontoabzug mindert sich nachträglich das vereinbarte Entgelt:
- **Deutschland (§ 17 Abs. 1 UStG):** Vorsteuerkorrektur im Besteuerungszeitraum der Zahlung. Buchung auf SKR03 Konto `3736` (19 %) / `3731` (7 %) bzw. SKR04 Konto `5736` / `5731`.
- **Österreich (§ 16 UStG 1994):** Berichtigung der Steuergrundlage (20 % / 10 %). Buchung im öst. Einheitskontenrahmen auf Konto `5880`.
- **Schweiz (Art. 41 MWSTG):** Nachträgliche Entgeltminderung bei effektiver MWST-Abrechnung (8,1 % / 2,6 %).

---

## 🚀 Installation & Schnellstart

```bash
# Aus dem Repository installieren
git clone https://github.com/DACHDigitalwerk/skonto-rechner-effektivzins-dach.git
cd skonto-rechner-effektivzins-dach
pip install -e .
```

### CLI Verwendung (`dach-skonto`)

```bash
# Standardrechnung: 10.000 € mit 2% Skonto binnen 10 Tagen, 30 Tage netto
dach-skonto --amount 10000 --skonto-rate 2.0 --skonto-days 10 --netto-days 30

# Österreichische Rechnung mit 3% Skonto und JSON-Ausgabe
dach-skonto --amount 15000 --skonto-rate 3.0 --skonto-days 14 --netto-days 30 --country AT --json

# Schweizer Rechnung (8.1% MWST, Kontokorrentlinie 9.5%)
dach-skonto --amount 25000 --skonto-rate 2.0 --skonto-days 10 --netto-days 30 --country CH
```

#### Beispiel CLI-Ausgabe:

```text
====================================================================
 DACH SKONTO- & EFFEKTIVZINS-RECHNER 2026 [Deutschland]
====================================================================
 Rechnungsbetrag (Brutto):     10.000,00 €
 Skontobedingung:             2.0 % innerhalb 10 Tagen (30 Tage netto)
 Skonto-Betrag (Ersparnis):   200,00 €
 Ueberweisungsbetrag (Skonto): 9.800,00 €
 Kreditperiode:               20 Tage (30 - 10)
--------------------------------------------------------------------
 EFFEKTIVER JAHRESZINS (p.a.): 36.73 % p.a.
 Sollzins Banklinie (p.a.):    11.50 % p.a.
 Zinskosten Kontokorrent:      62,61 €
 Reingewinn bei Bankkredit:    +137,39 €
 Break-Even Bankzinssatz:      36.73 % p.a.
--------------------------------------------------------------------
 Vorsteuerkorrektur (§ 17 Abs. 1 UStG):
  • Skonto Netto:              168,07 €
  • Vorsteuer-Korrektur (19.0%): 31,93 €
====================================================================
 Empfehlung: Skonto ziehen! Der Skonto-Effektivzins (36.73% p.a.) ist 3.2-mal höher als der Kontokorrentzins (11.50% p.a.). Netto-Finanzgewinn: +137.39 €.
====================================================================
```

---

## 🐍 Python Library API

```python
from skonto_dach import calculate_skonto, SkontoInvoice

# 1. Direkte Berechnung
res = calculate_skonto(
    gross_amount=20000.0,
    skonto_rate_pct=2.0,
    skonto_days=10,
    netto_days=30,
    bank_interest_rate_pct=11.5,
    country="DE",
    tax_rate_pct=19.0
)

print(f"Effektivzins: {res.effective_interest_rate_pa:.2f} % p.a.")
print(f"Netto-Gewinn nach Bankzinsen: {res.net_benefit_vs_bank:.2f} €")
print(f"Vorsteuerkorrektur (§ 17 UStG): {res.tax_correction.tax_correction_amount:.2f} €")

# 2. Typed Dataclass Workflow (z. B. für ERP-/FIBU-Pipelines)
inv = SkontoInvoice(
    gross_amount=50000.0,
    skonto_rate_pct=3.0,
    skonto_days=14,
    netto_days=30,
    bank_interest_rate_pct=9.5,
    country="CH"
)
result = calculate_skonto(inv)
print(result.recommendation)
```

---

## 🧪 Tests ausführen

Das Repository enthält eine vollständige Testsuite mit 27 automatisierten Unit-Tests:

```bash
pytest tests/ -v
```

---

## 🌐 Online-Werkzeuge & Ratgeber

Besuchen Sie unsere kostenlosen B2B-Online-Werkzeuge für den deutschsprachigen Wirtschaftsraum:
- **[Online Skonto- & Effektivzins-Rechner 2026](https://dach-digitalwerk.netlify.app/skonto-rechner-effektivzins/)**
- **[Ratgeber: Skonto berechnen Formel & Effektivzins](https://dach-digitalwerk.netlify.app/skonto-berechnen-formel-effektivzins.html)**
- **[Ratgeber: Lieferantenkredit vs. Kontokorrentkredit](https://dach-digitalwerk.netlify.app/lieferantenkredit-kontokorrentkredit-vergleich.html)**
- **[Ratgeber: Skonto buchen & Vorsteuerkorrektur (§ 17 UStG)](https://dach-digitalwerk.netlify.app/skonto-buchen-vorsteuerkorrektur-ustg.html)**
- **[DACH Digitalwerk Hub](https://dach-digitalwerk.netlify.app/)**

---

## 📄 Lizenz & Rechtlicher Hinweis

Dieses Projekt ist unter der **MIT License** lizenziert.

*Rechtlicher Hinweis:* Dieses Tool dient ausschließlich mathematischen Berechnungen und betriebswirtschaftlichen Simulationen gemäß § 2 RDG / § 5 StBerG. Es stellt keine Rechts- oder Steuerberatung dar.
