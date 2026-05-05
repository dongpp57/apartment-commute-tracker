# Apartment Commute Tracker

Tracks motorbike commute time from 10 candidate apartment clusters in Hanoi to Vincom Nguyễn Chí Thanh, measured daily at 7:00, 7:30 (home → work) and 17:30, 18:00 (work → home) ICT.

**Live dashboard:** https://dongpp57.github.io/apartment-commute-tracker/

## Data files

- [`data/apartments.json`](data/apartments.json) — 10 clusters in active tracking
- [`data/considered_clusters.md`](data/considered_clusters.md) — research log of all clusters considered, with rejection reasons
- [`data/commute_log.csv`](data/commute_log.csv) — append-only log from cron runs

## Setup

See [docs/SETUP.md](docs/SETUP.md) for step-by-step instructions (Mapbox token, GitHub Secrets, Pages).

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export MAPBOX_TOKEN=your_pk_token_here
python scripts/track_commute.py --slot 0700
python scripts/report.py
```
