# Design Decisions and Trade-offs

## Data Source
Frankfurter API was selected for the following reasons:
- Backed by the European Central Bank — authoritative and reliable
- Completely free with no API key or registration required
- Supports full date range queries in a single API call (efficient)
- Covers all 7 required currencies natively

Trade-off: ECB rates are published once daily at ~16:00 CET, so this
pipeline reflects end-of-day reference rates, not intraday prices.

## Historical Window
Data loaded from 2023-01-01 to the current date (dynamic).
This provides 2+ years of history, enabling meaningful YTD comparisons
across multiple calendar years without excessive data volume.

## Cross Pair Generation
All 42 cross pairs are derived mathematically from EUR-based rates:
  NOK/SEK = EUR→SEK rate / EUR→NOK rate
This avoids 42 separate API calls and guarantees internal consistency
(no rounding discrepancies between pairs).

## Output Format
CSV was chosen for maximum Power BI compatibility.
The file can be loaded directly with no transformations needed on import.

## Schema Design
The output is a flat, denormalized table — one row per pair per day.
This is the optimal structure for BI tools, avoiding the need for
complex joins or relationships in Power BI.

## YTD Definition
YTD base = the first available trading day of each calendar year per pair.
January 1st is never a trading day, so the first ECB publication of the
year (typically January 2nd or 3rd) is used as the starting point.

## Metrics Calculated in the Pipeline
- daily_change: absolute rate difference from previous trading day
- daily_change_pct: percentage change from previous trading day
- ytd_start_rate: rate on first trading day of the year
- ytd_change_pct: percentage change since start of the year
