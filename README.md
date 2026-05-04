# Apartment Commute Tracker

Tracks motorbike commute time from 10 candidate apartment clusters in Hanoi to Vincom Nguyễn Chí Thanh, measured daily at 7:00 and 7:30 ICT.

## Setup

See [docs/SETUP.md](docs/SETUP.md) for step-by-step instructions (Google Cloud, GitHub Secrets, Pages).

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export GOOGLE_MAPS_API_KEY=your_key_here
python scripts/track_commute.py --slot 0700
python scripts/report.py
```
