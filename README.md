# FX Rates Pipeline

## Overview
A Python pipeline that fetches daily foreign exchange rates for 7 currencies
(NOK, EUR, SEK, PLN, RON, DKK, CZK), generates all 42 cross pairs, and outputs
an analytics-ready CSV file for Power BI reporting.

## Requirements
- Python 3.x
- Libraries: requests, pandas

## Installation
Open a terminal and run:
pip install requests pandas

## How to Run
python fx_pipeline.py

## Expected Output
A file called fx_rates.csv will be created in the same folder.
Expected: ~42 pairs × ~800+ trading days = 33,000+ rows

## Validate the Output
Check the terminal output for:
- "42" unique pairs
- 800+ dates
- No error messages

## Data Source
Frankfurter API (https://api.frankfurter.dev)
- Backed by the European Central Bank (ECB)
- Free, no API key required
- Historical window loaded: 2023-01-01 to today (dynamic)
