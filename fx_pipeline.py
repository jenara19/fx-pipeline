import requests
import pandas as pd
from itertools import permutations
from datetime import date

# ── CONFIGURATION ────────────────────────────────────────────────────────────
CURRENCIES  = ["NOK", "EUR", "SEK", "PLN", "RON", "DKK", "CZK"]
START_DATE  = "2023-01-01"
END_DATE    = date.today().isoformat()
OUTPUT_FILE = "fx_rates.csv"

# ── STEP 1: FETCH DATA FROM API ───────────────────────────────────────────────
non_eur = [c for c in CURRENCIES if c != "EUR"]

url = f"https://api.frankfurter.dev/v1/{START_DATE}..{END_DATE}"
params = {
    "base"    : "EUR",
    "symbols" : ",".join(non_eur)
}

print("Fetching FX data... this may take a few seconds")
response = requests.get(url, params=params)
response.raise_for_status()
raw = response.json()
print(f"Data received: {len(raw['rates'])} trading days found")

# ── STEP 2: PARSE INTO A FLAT TABLE ──────────────────────────────────────────
records = []
for date_str, rates in raw["rates"].items():
    rates["EUR"] = 1.0
    for currency, rate in rates.items():
        records.append({
            "date"     : date_str,
            "quote"    : currency,
            "eur_rate" : rate
        })

df_eur = pd.DataFrame(records)
df_eur["date"] = pd.to_datetime(df_eur["date"])
print(f"Step 2 done: {len(df_eur)} rows parsed")

# ── STEP 3: PIVOT TO WIDE TABLE ───────────────────────────────────────────────
pivot = df_eur.pivot(index="date", columns="quote", values="eur_rate").reset_index()
print(f"Step 3 done: pivot table has {len(pivot)} dates")

# ── STEP 4: GENERATE ALL 42 CROSS PAIRS ──────────────────────────────────────
cross_records = []
for base_cur, quote_cur in permutations(CURRENCIES, 2):
    temp = pd.DataFrame()
    temp["date"]           = pivot["date"]
    temp["base_currency"]  = base_cur
    temp["quote_currency"] = quote_cur
    temp["pair"]           = base_cur + "/" + quote_cur
    temp["rate"]           = pivot[quote_cur] / pivot[base_cur]
    cross_records.append(temp)

df = pd.concat(cross_records, ignore_index=True)
df = df.sort_values(["pair", "date"]).reset_index(drop=True)
print(f"Step 4 done: {len(df)} cross pair rows generated")

# ── STEP 5: DAILY CHANGE METRICS ─────────────────────────────────────────────
df["prev_rate"]        = df.groupby("pair")["rate"].shift(1)
df["daily_change"]     = df["rate"] - df["prev_rate"]
df["daily_change_pct"] = (df["daily_change"] / df["prev_rate"]) * 100
print("Step 5 done: daily change calculated")

# ── STEP 6: YEAR-TO-DATE CALCULATION ─────────────────────────────────────────
df["year"] = df["date"].dt.year

ytd_base = (
    df.groupby(["pair", "year"])["rate"]
    .first()
    .reset_index()
    .rename(columns={"rate": "ytd_start_rate"})
)

df = df.merge(ytd_base, on=["pair", "year"], how="left")
df["ytd_change_pct"] = ((df["rate"] - df["ytd_start_rate"]) / df["ytd_start_rate"]) * 100
print("Step 6 done: YTD calculation complete")

# ── STEP 7: EXPORT TO CSV ─────────────────────────────────────────────────────
df_final = df[[
    "date", "year", "base_currency", "quote_currency", "pair",
    "rate", "daily_change", "daily_change_pct",
    "ytd_start_rate", "ytd_change_pct"
]]

df_final.to_csv(OUTPUT_FILE, index=False)
print(f"\n✅ DONE! {len(df_final):,} rows written to '{OUTPUT_FILE}'")
print(f"   Pairs: {df_final['pair'].nunique()} | Dates: {df_final['date'].nunique()}")
