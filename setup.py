# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="skonto-dach",
    version="1.0.0",
    description="DACH Skonto-, Zahlungsziel- & Lieferantenkredit-Rechner 2026: Exakte Effektivzinsformel, Kontokorrent-Vergleich & Vorsteuerkorrektur (§ 17 UStG / Art. 41 MWSTG).",
    author="DACH Digitalwerk",
    packages=find_packages(),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "dach-skonto=skonto_dach.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Intended Audience :: Financial and Insurance Industry",
    ],
)
