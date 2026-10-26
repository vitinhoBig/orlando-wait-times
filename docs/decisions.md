# Design decisions

## 001 — Raw payload storage (2026-10-26)

Measured with `scripts/spike_payload.py` (8 parks, one poll, measured at night):

| Metric | Per poll | Per day (288 polls) |
|---|---|---|
| Raw JSON | 229.2 KB | 64.5 MB |
| Gzip JSON | 29.4 KB | 8.3 MB |
| Attraction rows | 179 | 51,552 |

**Decision:** store raw responses as gzip files on disk (~3 GB/year), outside the
database and outside Git. Load only parsed rows into PostgreSQL (~19M rows/year).

**Why:** gzip shrinks the payload ~8x; raw data is kept to allow reprocessing
without calling the API again. Data is never committed, per ThemeParks.wiki terms.

**To revisit:** sizes were measured with parks closed; the collector logs response
size per poll, so this can be re-checked against a full day.
