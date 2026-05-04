# Apartment Commute Tracker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a 2-phase system that (1) shortlists 10 apartment clusters in Hanoi matching budget ~5B VND + 2BR + ≤30min motorbike commute to Vincom Nguyễn Chí Thanh, and (2) measures actual commute time daily at 7:00 and 7:30 ICT via GitHub Actions cron, accumulating data for statistical analysis.

**Architecture:** Two phases. Phase 1 is a one-shot research pass producing `data/apartments.json`. Phase 2 is a Python pipeline (track + report) triggered by GitHub Actions cron, calling Google Maps Distance Matrix API, appending to `data/commute_log.csv`, regenerating `reports/latest.html`, and auto-committing back to the repo. Reports are served via GitHub Pages.

**Tech Stack:** Python 3.11+, `requests`, `pandas`, `jinja2`, Chart.js (CDN), GitHub Actions, Google Maps Distance Matrix API, Git/GitHub Pages.

**Spec reference:** `docs/superpowers/specs/2026-05-04-apartment-commute-tracker-design.md`

---

## File Structure

```
apartment-commute-tracker/
├── .github/
│   └── workflows/
│       └── track-commute.yml          # GitHub Actions cron config
├── data/
│   ├── apartments.json                # Phase 1 output (10 clusters)
│   └── commute_log.csv                # Append-only log
├── scripts/
│   ├── track_commute.py               # Calls Google Maps API + appends log
│   ├── report.py                      # Generates HTML + CLI report
│   └── lib/
│       ├── __init__.py
│       ├── config.py                  # Constants (destination coords, MOTO_FACTOR)
│       ├── maps_client.py             # Thin wrapper over Distance Matrix API
│       ├── log_writer.py              # CSV append helper
│       └── stats.py                   # Pure stats functions (mean, p50, p90, etc.)
├── tests/
│   ├── __init__.py
│   ├── test_maps_client.py
│   ├── test_log_writer.py
│   ├── test_stats.py
│   └── fixtures/
│       ├── sample_apartments.json
│       └── sample_commute_log.csv
├── templates/
│   └── report.html.j2                 # Jinja2 template for dashboard
├── reports/
│   └── latest.html                    # Auto-generated dashboard
├── requirements.txt
├── .gitignore
└── README.md                          # Setup instructions for user
```

**Responsibility per file:**
- `lib/maps_client.py` — only knows how to call Google Maps API, returns parsed result or raises
- `lib/log_writer.py` — only knows how to append a row to CSV
- `lib/stats.py` — pure functions, no I/O, easy to unit test
- `lib/config.py` — single source of truth for constants
- `track_commute.py` — orchestrator: read apartments → loop → call API → write log
- `report.py` — orchestrator: read log → compute stats → render CLI table + HTML

---

## Phase 0: Repo Bootstrap

### Task 1: Initialize repo structure

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `README.md`
- Create: `scripts/lib/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create directory skeleton**

Run from project root:
```bash
mkdir -p .github/workflows data scripts/lib tests/fixtures templates reports
```

- [ ] **Step 2: Write `requirements.txt`**

```
requests==2.32.3
pandas==2.2.3
jinja2==3.1.4
pytest==8.3.3
```

- [ ] **Step 3: Write `.gitignore`**

```
__pycache__/
*.pyc
.pytest_cache/
.venv/
venv/
.env
.DS_Store
*.swp
```

- [ ] **Step 4: Write empty `__init__.py` files**

```bash
touch scripts/lib/__init__.py tests/__init__.py
```

- [ ] **Step 5: Write minimal `README.md`**

```markdown
# Apartment Commute Tracker

Tracks motorbike commute time from 10 candidate apartment clusters in Hanoi to Vincom Nguyễn Chí Thanh, measured daily at 7:00 and 7:30 ICT.

## Setup

See `docs/SETUP.md` (will be created in final task).

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export GOOGLE_MAPS_API_KEY=your_key_here
python scripts/track_commute.py --slot 0700
python scripts/report.py
```
```

- [ ] **Step 6: Verify Python venv works and deps install**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -c "import requests, pandas, jinja2, pytest; print('OK')"
```
Expected output: `OK`

- [ ] **Step 7: Commit**

```bash
git add requirements.txt .gitignore README.md scripts/lib/__init__.py tests/__init__.py
git commit -m "chore: bootstrap project structure"
```

---

## Phase 1: Research apartment clusters

### Task 2: Research and write `data/apartments.json`

**Files:**
- Create: `data/apartments.json`

This is a research task, not code. The agent executing this plan must:
1. Use WebSearch / WebFetch to gather current listings from batdongsan.com.vn, nhatot.com, cafeland.vn, alonhadat.com.vn, meeyland.com.
2. Filter to clusters with at least one 2BR unit at 4.5–5.2 billion VND.
3. Confirm geographic spread (Cầu Giấy, Nam Từ Liêm, Thanh Xuân, Hà Đông, Hoàng Mai, Tây Hồ, Long Biên).
4. Confirm category mix (cao_cap / trung_cap / moi_ban_giao).
5. Look up exact lat/lng for each cluster via Google Maps web search or known coordinates.
6. Pre-research target seed list (refine during research):
   - Cầu Giấy / Nam Từ Liêm: HD Mon City, Mandarin Garden, Discovery Complex, Vinhomes Smart City, The Matrix One, Sunshine City, Mỹ Đình Pearl
   - Thanh Xuân / Hà Đông: Royal City, The Manor Central Park, Anland Premium, Mipec Rubik 360
   - Hoàng Mai: Times City, Imperia Sky Garden, Hồ Gươm Plaza
   - Tây Hồ / Long Biên: Sunshine Riverside, Mipec Riverside, D'. El Dorado

- [ ] **Step 1: Run web research for each candidate cluster**

For each cluster in the seed list, run a search query similar to:
```
batdongsan.com.vn "<cluster name>" 2 phòng ngủ 4.8 tỉ
```
Capture: address, sample 2BR price, area, status (đã bàn giao / sắp bàn giao), source URL.

Discard clusters where no 2BR unit exists in the 4.5–5.2 billion range.

- [ ] **Step 2: Confirm coordinates via Google Maps**

For each surviving cluster, look up the cluster's primary entrance on Google Maps. Record `lat` and `lng` to 4 decimal places.

Also confirm destination coordinates: search "Vincom Nguyễn Chí Thanh" → record exact lat/lng (will be hardcoded in `lib/config.py`).

- [ ] **Step 3: Estimate baseline commute (Google Maps directions, peak hour)**

For each cluster, get a baseline `estimated_commute_min` by checking Google Maps directions to Vincom NCT during peak hour (set departure to next weekday 07:00). This is just a sanity check — the real measurement is Phase 2's job.

Drop any cluster whose baseline already exceeds 35 minutes.

- [ ] **Step 4: Pick final 10 clusters with diversity check**

Final list MUST include:
- At least 2 clusters in Cầu Giấy or Nam Từ Liêm
- At least 1 cluster from each of: Thanh Xuân/Hà Đông, Hoàng Mai, Tây Hồ/Long Biên
- At least 2 of category `cao_cap`, 2 of `trung_cap`, 2 of `moi_ban_giao`

- [ ] **Step 5: Write `data/apartments.json`**

Schema (one entry per cluster, exactly 10 entries):

```json
[
  {
    "id": "vinhomes-smart-city",
    "cluster_name": "Vinhomes Smart City",
    "district": "Nam Từ Liêm",
    "representative_address": "Tây Mỗ, Nam Từ Liêm, Hà Nội",
    "lat": 21.0145,
    "lng": 105.7423,
    "category": "cao_cap",
    "sample_units": [
      {
        "tower": "Sapphire 1",
        "area_m2": 68,
        "bedrooms": 2,
        "price_billion_vnd": 4.8,
        "status": "đã bàn giao",
        "source_url": "https://batdongsan.com.vn/..."
      }
    ],
    "pros": ["Tiện ích nội khu đầy đủ", "Cộng đồng trẻ", "Tuyến Metro số 5 tương lai"],
    "cons": ["Xa trung tâm", "Mật độ cao"],
    "estimated_commute_min": 28,
    "investment_potential": "Cao - hạ tầng phía Tây phát triển mạnh",
    "data_collected_date": "2026-05-04"
  }
]
```

Field constraints:
- `id`: kebab-case, lowercase, ASCII only (used as filename-safe key in CSV)
- `category`: one of `"cao_cap"`, `"trung_cap"`, `"moi_ban_giao"`
- `lat`, `lng`: 4 decimal places
- `sample_units`: at least 1 unit, max 3
- `pros` / `cons`: 2-4 items each
- `data_collected_date`: ISO date

- [ ] **Step 6: Validate JSON**

Run:
```bash
python -c "import json; data = json.load(open('data/apartments.json')); assert len(data) == 10, f'Expected 10, got {len(data)}'; ids = [a['id'] for a in data]; assert len(ids) == len(set(ids)), 'Duplicate IDs'; print('OK', len(data), 'clusters')"
```
Expected: `OK 10 clusters`

- [ ] **Step 7: User review checkpoint**

Present the list to Anh (cluster names + districts + sample prices). Wait for explicit approval. If Anh requests add/remove/edit, apply changes and re-run validation.

- [ ] **Step 8: Commit**

```bash
git add data/apartments.json
git commit -m "feat: add 10 candidate apartment clusters (Phase 1 output)"
```

---

## Phase 2: Build the tracking pipeline (TDD)

### Task 3: Implement `lib/config.py`

**Files:**
- Create: `scripts/lib/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

`tests/test_config.py`:
```python
from scripts.lib import config


def test_destination_coords_are_hanoi():
    assert 21.0 < config.DESTINATION_LAT < 21.1
    assert 105.7 < config.DESTINATION_LNG < 105.9


def test_moto_factor_default():
    assert 0.80 <= config.MOTO_FACTOR <= 0.95


def test_slots_defined():
    assert config.SLOTS == ("0700", "0730")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError` or `AttributeError`.

- [ ] **Step 3: Write `lib/config.py`**

```python
"""Single source of truth for tracker constants."""

DESTINATION_LAT = 21.0245
DESTINATION_LNG = 105.8095
DESTINATION_NAME = "Vincom Nguyễn Chí Thanh"

MOTO_FACTOR = 0.88

SLOTS = ("0700", "0730")

CSV_COLUMNS = (
    "timestamp_ict",
    "apartment_id",
    "slot",
    "duration_min",
    "duration_in_traffic_min",
    "duration_motorcycle_min",
    "distance_km",
    "status",
)
```

Note: Destination coordinates above are placeholders to make the test pass. **The agent must verify the exact lat/lng of Vincom Nguyễn Chí Thanh during Task 2 Step 2 and update these constants here before Task 4.**

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add scripts/lib/config.py tests/test_config.py
git commit -m "feat(lib): add config constants"
```

---

### Task 4: Implement `lib/maps_client.py`

**Files:**
- Create: `scripts/lib/maps_client.py`
- Test: `tests/test_maps_client.py`

- [ ] **Step 1: Write the failing test (success path)**

`tests/test_maps_client.py`:
```python
from unittest.mock import patch, MagicMock
import pytest
from scripts.lib.maps_client import fetch_commute, MapsAPIError


def _ok_response():
    return {
        "status": "OK",
        "rows": [{
            "elements": [{
                "status": "OK",
                "duration": {"value": 1080},                # 18 min
                "duration_in_traffic": {"value": 1320},     # 22 min
                "distance": {"value": 9400},                # 9.4 km
            }]
        }]
    }


@patch("scripts.lib.maps_client.requests.get")
def test_fetch_commute_success(mock_get):
    mock_get.return_value = MagicMock(
        status_code=200, json=lambda: _ok_response()
    )
    result = fetch_commute(
        origin_lat=21.0145, origin_lng=105.7423,
        dest_lat=21.0245, dest_lng=105.8095,
        api_key="fake-key",
    )
    assert result["duration_min"] == 18.0
    assert result["duration_in_traffic_min"] == 22.0
    assert result["distance_km"] == 9.4
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_maps_client.py::test_fetch_commute_success -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write minimal `lib/maps_client.py`**

```python
"""Thin wrapper around Google Maps Distance Matrix API."""

import time
import requests


class MapsAPIError(Exception):
    pass


_BASE_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"


def fetch_commute(*, origin_lat, origin_lng, dest_lat, dest_lng, api_key, timeout=15):
    params = {
        "origins": f"{origin_lat},{origin_lng}",
        "destinations": f"{dest_lat},{dest_lng}",
        "mode": "driving",
        "departure_time": str(int(time.time())),
        "traffic_model": "best_guess",
        "key": api_key,
    }
    resp = requests.get(_BASE_URL, params=params, timeout=timeout)
    if resp.status_code != 200:
        raise MapsAPIError(f"HTTP {resp.status_code}: {resp.text[:200]}")
    payload = resp.json()
    if payload.get("status") != "OK":
        raise MapsAPIError(f"top-level status={payload.get('status')}")
    element = payload["rows"][0]["elements"][0]
    if element.get("status") != "OK":
        raise MapsAPIError(f"element status={element.get('status')}")
    return {
        "duration_min": element["duration"]["value"] / 60.0,
        "duration_in_traffic_min": element["duration_in_traffic"]["value"] / 60.0,
        "distance_km": element["distance"]["value"] / 1000.0,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_maps_client.py::test_fetch_commute_success -v`
Expected: 1 passed.

- [ ] **Step 5: Add failing test for HTTP error**

Append to `tests/test_maps_client.py`:
```python
@patch("scripts.lib.maps_client.requests.get")
def test_fetch_commute_http_error(mock_get):
    mock_get.return_value = MagicMock(status_code=500, text="Server Error")
    with pytest.raises(MapsAPIError, match="HTTP 500"):
        fetch_commute(
            origin_lat=21.0, origin_lng=105.8,
            dest_lat=21.0, dest_lng=105.8,
            api_key="x",
        )
```

- [ ] **Step 6: Run new test to verify it passes**

Run: `pytest tests/test_maps_client.py -v`
Expected: 2 passed (no new code needed — already handled).

- [ ] **Step 7: Add failing test for top-level API error**

Append:
```python
@patch("scripts.lib.maps_client.requests.get")
def test_fetch_commute_quota_error(mock_get):
    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: {"status": "OVER_QUERY_LIMIT"}
    )
    with pytest.raises(MapsAPIError, match="OVER_QUERY_LIMIT"):
        fetch_commute(
            origin_lat=21.0, origin_lng=105.8,
            dest_lat=21.0, dest_lng=105.8,
            api_key="x",
        )
```

- [ ] **Step 8: Run new test**

Run: `pytest tests/test_maps_client.py -v`
Expected: 3 passed.

- [ ] **Step 9: Add failing test for element-level error (e.g., ZERO_RESULTS)**

Append:
```python
@patch("scripts.lib.maps_client.requests.get")
def test_fetch_commute_element_error(mock_get):
    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: {
            "status": "OK",
            "rows": [{"elements": [{"status": "ZERO_RESULTS"}]}],
        }
    )
    with pytest.raises(MapsAPIError, match="element status=ZERO_RESULTS"):
        fetch_commute(
            origin_lat=21.0, origin_lng=105.8,
            dest_lat=21.0, dest_lng=105.8,
            api_key="x",
        )
```

- [ ] **Step 10: Run all tests**

Run: `pytest tests/test_maps_client.py -v`
Expected: 4 passed.

- [ ] **Step 11: Commit**

```bash
git add scripts/lib/maps_client.py tests/test_maps_client.py
git commit -m "feat(lib): add Google Maps Distance Matrix client with error handling"
```

---

### Task 5: Implement `lib/log_writer.py`

**Files:**
- Create: `scripts/lib/log_writer.py`
- Test: `tests/test_log_writer.py`

- [ ] **Step 1: Write failing test for header creation on first write**

`tests/test_log_writer.py`:
```python
from pathlib import Path
import csv
from scripts.lib.log_writer import append_row
from scripts.lib.config import CSV_COLUMNS


def test_append_creates_header_if_missing(tmp_path):
    log_path = tmp_path / "commute_log.csv"
    row = {
        "timestamp_ict": "2026-05-05T07:00:00+07:00",
        "apartment_id": "vinhomes-smart-city",
        "slot": "0700",
        "duration_min": 18.5,
        "duration_in_traffic_min": 22.1,
        "duration_motorcycle_min": 19.4,
        "distance_km": 9.4,
        "status": "OK",
    }
    append_row(log_path, row)

    with open(log_path) as f:
        reader = csv.reader(f)
        header = next(reader)
        data = next(reader)

    assert tuple(header) == CSV_COLUMNS
    assert data[0] == "2026-05-05T07:00:00+07:00"
    assert data[1] == "vinhomes-smart-city"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_log_writer.py::test_append_creates_header_if_missing -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write `lib/log_writer.py`**

```python
"""Append-only CSV writer for commute log."""

import csv
from pathlib import Path
from .config import CSV_COLUMNS


def append_row(path, row):
    path = Path(path)
    write_header = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow({col: row.get(col, "") for col in CSV_COLUMNS})
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_log_writer.py -v`
Expected: 1 passed.

- [ ] **Step 5: Add failing test for second write skipping header**

Append:
```python
def test_append_skips_header_on_second_write(tmp_path):
    log_path = tmp_path / "commute_log.csv"
    row1 = {
        "timestamp_ict": "2026-05-05T07:00:00+07:00",
        "apartment_id": "a", "slot": "0700",
        "duration_min": 10, "duration_in_traffic_min": 12,
        "duration_motorcycle_min": 10.5, "distance_km": 5, "status": "OK",
    }
    row2 = dict(row1, apartment_id="b")
    append_row(log_path, row1)
    append_row(log_path, row2)

    with open(log_path) as f:
        lines = f.readlines()
    assert len(lines) == 3  # 1 header + 2 data rows
```

- [ ] **Step 6: Run test to verify it passes**

Run: `pytest tests/test_log_writer.py -v`
Expected: 2 passed.

- [ ] **Step 7: Add failing test for error row (missing numeric fields)**

Append:
```python
def test_append_error_row_with_blank_metrics(tmp_path):
    log_path = tmp_path / "commute_log.csv"
    row = {
        "timestamp_ict": "2026-05-05T07:00:00+07:00",
        "apartment_id": "royal-city",
        "slot": "0700",
        "status": "ERROR_quota_exceeded",
    }
    append_row(log_path, row)

    with open(log_path) as f:
        lines = f.readlines()
    # header + 1 data row, with blanks for missing numeric columns
    assert len(lines) == 2
    assert "ERROR_quota_exceeded" in lines[1]
    assert lines[1].count(",") == 7  # 8 columns = 7 commas
```

- [ ] **Step 8: Run test to verify it passes**

Run: `pytest tests/test_log_writer.py -v`
Expected: 3 passed.

- [ ] **Step 9: Commit**

```bash
git add scripts/lib/log_writer.py tests/test_log_writer.py
git commit -m "feat(lib): add CSV append-only log writer"
```

---

### Task 6: Implement `lib/stats.py`

**Files:**
- Create: `scripts/lib/stats.py`
- Test: `tests/test_stats.py`

- [ ] **Step 1: Write failing test for `summarize_durations`**

`tests/test_stats.py`:
```python
from scripts.lib.stats import summarize_durations


def test_summarize_basic():
    durations = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28]
    result = summarize_durations(durations)
    assert result["mean"] == 19.0
    assert result["p50"] == 19.0
    assert result["p90"] == 26.2
    assert result["min"] == 10
    assert result["max"] == 28
    assert result["samples"] == 10


def test_summarize_empty():
    result = summarize_durations([])
    assert result["samples"] == 0
    assert result["mean"] is None
    assert result["p50"] is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_stats.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Write `lib/stats.py`**

```python
"""Pure stats helpers — no I/O."""

import statistics


def summarize_durations(durations):
    durations = [d for d in durations if d is not None]
    n = len(durations)
    if n == 0:
        return {
            "mean": None, "p50": None, "p90": None,
            "min": None, "max": None, "std": None, "samples": 0,
        }
    sorted_d = sorted(durations)
    return {
        "mean": round(sum(sorted_d) / n, 2),
        "p50": _percentile(sorted_d, 50),
        "p90": _percentile(sorted_d, 90),
        "min": min(sorted_d),
        "max": max(sorted_d),
        "std": round(statistics.pstdev(sorted_d), 2) if n > 1 else 0.0,
        "samples": n,
    }


def _percentile(sorted_values, p):
    """Linear interpolation percentile (matches numpy default)."""
    if not sorted_values:
        return None
    n = len(sorted_values)
    rank = (p / 100) * (n - 1)
    low = int(rank)
    high = min(low + 1, n - 1)
    weight = rank - low
    return round(sorted_values[low] * (1 - weight) + sorted_values[high] * weight, 2)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_stats.py -v`
Expected: 2 passed.

- [ ] **Step 5: Add failing test for ranking helper**

Append:
```python
from scripts.lib.stats import rank_apartments


def test_rank_by_mean_ascending():
    summaries = {
        "a": {"mean": 25.0, "samples": 10},
        "b": {"mean": 18.0, "samples": 10},
        "c": {"mean": 22.0, "samples": 10},
        "d": {"mean": None, "samples": 0},  # excluded
    }
    ranking = rank_apartments(summaries)
    assert [r["apartment_id"] for r in ranking] == ["b", "c", "a"]
    assert ranking[0]["rank"] == 1
```

- [ ] **Step 6: Run test to verify it fails**

Run: `pytest tests/test_stats.py::test_rank_by_mean_ascending -v`
Expected: FAIL with `ImportError`.

- [ ] **Step 7: Add `rank_apartments` to `lib/stats.py`**

Append to `lib/stats.py`:
```python
def rank_apartments(summaries):
    """Sort apartments by mean ascending; exclude entries with no data."""
    valid = [
        {"apartment_id": aid, **s}
        for aid, s in summaries.items()
        if s.get("mean") is not None
    ]
    valid.sort(key=lambda x: x["mean"])
    for i, entry in enumerate(valid, start=1):
        entry["rank"] = i
    return valid
```

- [ ] **Step 8: Run test to verify it passes**

Run: `pytest tests/test_stats.py -v`
Expected: 3 passed.

- [ ] **Step 9: Commit**

```bash
git add scripts/lib/stats.py tests/test_stats.py
git commit -m "feat(lib): add summarize_durations and rank_apartments"
```

---

### Task 7: Implement `track_commute.py` orchestrator

**Files:**
- Create: `scripts/track_commute.py`
- Test: `tests/test_track_commute.py`
- Create: `tests/fixtures/sample_apartments.json`

- [ ] **Step 1: Create test fixture**

`tests/fixtures/sample_apartments.json`:
```json
[
  {
    "id": "test-cluster-a",
    "cluster_name": "Test Cluster A",
    "lat": 21.0145,
    "lng": 105.7423
  },
  {
    "id": "test-cluster-b",
    "cluster_name": "Test Cluster B",
    "lat": 21.0500,
    "lng": 105.8500
  }
]
```

- [ ] **Step 2: Write failing test for orchestrator (mock API)**

`tests/test_track_commute.py`:
```python
import json
import csv
from unittest.mock import patch
from pathlib import Path
from scripts.track_commute import run_tracking


@patch("scripts.track_commute.fetch_commute")
def test_run_tracking_writes_one_row_per_apartment(mock_fetch, tmp_path):
    mock_fetch.return_value = {
        "duration_min": 18.0,
        "duration_in_traffic_min": 22.0,
        "distance_km": 9.4,
    }
    apartments_path = Path("tests/fixtures/sample_apartments.json")
    log_path = tmp_path / "commute_log.csv"

    run_tracking(
        apartments_path=apartments_path,
        log_path=log_path,
        slot="0700",
        api_key="fake-key",
    )

    with open(log_path) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[0]["apartment_id"] == "test-cluster-a"
    assert rows[0]["slot"] == "0700"
    assert rows[0]["status"] == "OK"
    # motorcycle = traffic * MOTO_FACTOR (0.88)
    assert abs(float(rows[0]["duration_motorcycle_min"]) - 22.0 * 0.88) < 0.01
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_track_commute.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 4: Write `scripts/track_commute.py`**

```python
"""Loop apartments, call Maps API, append to log."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Allow `python scripts/track_commute.py` to find `lib`
sys.path.insert(0, str(Path(__file__).parent))

from lib.maps_client import fetch_commute, MapsAPIError
from lib.log_writer import append_row
from lib import config


ICT = timezone(timedelta(hours=7))


def run_tracking(*, apartments_path, log_path, slot, api_key):
    with open(apartments_path, encoding="utf-8") as f:
        apartments = json.load(f)

    timestamp = datetime.now(tz=ICT).replace(microsecond=0).isoformat()

    for apt in apartments:
        row = {
            "timestamp_ict": timestamp,
            "apartment_id": apt["id"],
            "slot": slot,
        }
        try:
            result = fetch_commute(
                origin_lat=apt["lat"],
                origin_lng=apt["lng"],
                dest_lat=config.DESTINATION_LAT,
                dest_lng=config.DESTINATION_LNG,
                api_key=api_key,
            )
            row.update({
                "duration_min": round(result["duration_min"], 2),
                "duration_in_traffic_min": round(result["duration_in_traffic_min"], 2),
                "duration_motorcycle_min": round(
                    result["duration_in_traffic_min"] * config.MOTO_FACTOR, 2
                ),
                "distance_km": round(result["distance_km"], 2),
                "status": "OK",
            })
        except MapsAPIError as e:
            row["status"] = f"ERROR_{type(e).__name__}_{str(e)[:60]}"

        append_row(log_path, row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", required=True, choices=config.SLOTS)
    parser.add_argument("--apartments", default="data/apartments.json")
    parser.add_argument("--log", default="data/commute_log.csv")
    args = parser.parse_args()

    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_MAPS_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    run_tracking(
        apartments_path=Path(args.apartments),
        log_path=Path(args.log),
        slot=args.slot,
        api_key=api_key,
    )


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_track_commute.py -v`
Expected: 1 passed.

- [ ] **Step 6: Add failing test for API error path**

Append to `tests/test_track_commute.py`:
```python
from scripts.lib.maps_client import MapsAPIError


@patch("scripts.track_commute.fetch_commute")
def test_run_tracking_records_errors_and_continues(mock_fetch, tmp_path):
    # First call fails, second succeeds
    mock_fetch.side_effect = [
        MapsAPIError("OVER_QUERY_LIMIT"),
        {"duration_min": 18.0, "duration_in_traffic_min": 22.0, "distance_km": 9.4},
    ]
    log_path = tmp_path / "commute_log.csv"

    run_tracking(
        apartments_path=Path("tests/fixtures/sample_apartments.json"),
        log_path=log_path,
        slot="0700",
        api_key="fake-key",
    )

    with open(log_path) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[0]["status"].startswith("ERROR_")
    assert rows[0]["duration_min"] == ""  # blank for failed call
    assert rows[1]["status"] == "OK"
```

- [ ] **Step 7: Run test to verify it passes**

Run: `pytest tests/test_track_commute.py -v`
Expected: 2 passed.

- [ ] **Step 8: Commit**

```bash
git add scripts/track_commute.py tests/test_track_commute.py tests/fixtures/sample_apartments.json
git commit -m "feat: add track_commute orchestrator with error tolerance"
```

---

### Task 8: Implement `report.py` (CLI report)

**Files:**
- Create: `scripts/report.py`
- Test: `tests/test_report.py`
- Create: `tests/fixtures/sample_commute_log.csv`

- [ ] **Step 1: Create test fixture**

`tests/fixtures/sample_commute_log.csv`:
```
timestamp_ict,apartment_id,slot,duration_min,duration_in_traffic_min,duration_motorcycle_min,distance_km,status
2026-05-05T07:00:00+07:00,test-cluster-a,0700,15,18,15.84,7.5,OK
2026-05-06T07:00:00+07:00,test-cluster-a,0700,16,20,17.6,7.5,OK
2026-05-07T07:00:00+07:00,test-cluster-a,0700,15,19,16.72,7.5,OK
2026-05-05T07:30:00+07:00,test-cluster-a,0730,17,22,19.36,7.5,OK
2026-05-06T07:30:00+07:00,test-cluster-a,0730,18,24,21.12,7.5,OK
2026-05-05T07:00:00+07:00,test-cluster-b,0700,25,32,28.16,12.0,OK
2026-05-06T07:00:00+07:00,test-cluster-b,0700,26,34,29.92,12.0,OK
2026-05-07T07:00:00+07:00,test-cluster-b,0700,,,,,ERROR_OVER_QUERY_LIMIT
```

- [ ] **Step 2: Write failing test for `compute_report_data`**

`tests/test_report.py`:
```python
from pathlib import Path
from scripts.report import compute_report_data


def test_compute_report_data_groups_by_apartment_and_slot():
    log_path = Path("tests/fixtures/sample_commute_log.csv")
    apartments_path = Path("tests/fixtures/sample_apartments.json")
    data = compute_report_data(log_path=log_path, apartments_path=apartments_path)

    # data["per_apartment_slot"][apt_id][slot] = stats dict
    a_700 = data["per_apartment_slot"]["test-cluster-a"]["0700"]
    assert a_700["samples"] == 3
    assert a_700["mean"] is not None

    # Errors excluded
    b_700 = data["per_apartment_slot"]["test-cluster-b"]["0700"]
    assert b_700["samples"] == 2  # 3 rows but 1 is ERROR

    # Ranking present
    assert "ranking_0700" in data
    # Cluster A is faster (mean ~16) than B (mean ~29)
    assert data["ranking_0700"][0]["apartment_id"] == "test-cluster-a"
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_report.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 4: Write `scripts/report.py`**

```python
"""Generate CLI summary + HTML dashboard from commute_log.csv."""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

from lib.stats import summarize_durations, rank_apartments
from lib import config


def compute_report_data(*, log_path, apartments_path):
    apartments = json.loads(Path(apartments_path).read_text(encoding="utf-8"))
    apt_by_id = {a["id"]: a for a in apartments}

    df = pd.read_csv(log_path)
    df = df[df["status"] == "OK"]
    df["duration_motorcycle_min"] = pd.to_numeric(
        df["duration_motorcycle_min"], errors="coerce"
    )

    per_apt_slot = defaultdict(dict)
    for apt_id in apt_by_id:
        for slot in config.SLOTS:
            durations = df[
                (df["apartment_id"] == apt_id) & (df["slot"] == slot)
            ]["duration_motorcycle_min"].tolist()
            per_apt_slot[apt_id][slot] = summarize_durations(durations)

    rankings = {}
    for slot in config.SLOTS:
        summaries = {aid: stats[slot] for aid, stats in per_apt_slot.items()}
        rankings[f"ranking_{slot}"] = rank_apartments(summaries)

    return {
        "per_apartment_slot": dict(per_apt_slot),
        "apartments": apt_by_id,
        **rankings,
    }


def print_cli_report(data):
    print(f"COMMUTE TIME REPORT — Destination: {config.DESTINATION_NAME}")
    print(f"Mode: motorcycle (driving x {config.MOTO_FACTOR})")
    print()

    for slot in config.SLOTS:
        print(f"=== SLOT {slot[:2]}:{slot[2:]} ===")
        print(f"{'Cluster':<28} {'Mean':>6} {'p50':>6} {'p90':>6} {'Samples':>8}  Flags")
        for entry in data[f"ranking_{slot}"]:
            apt = data["apartments"].get(entry["apartment_id"], {})
            name = apt.get("cluster_name", entry["apartment_id"])[:27]
            stats = data["per_apartment_slot"][entry["apartment_id"]][slot]
            flags = []
            if stats.get("p90") and stats["p90"] > 30:
                flags.append("⚠️p90>30")
            if stats.get("std") and stats["std"] > 8:
                flags.append("🎲unstable")
            print(
                f"{name:<28} "
                f"{stats['mean']:>6.1f} {stats['p50']:>6.1f} {stats['p90']:>6.1f} "
                f"{stats['samples']:>8}  {' '.join(flags)}"
            )
        print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default="data/commute_log.csv")
    parser.add_argument("--apartments", default="data/apartments.json")
    parser.add_argument("--html-out", default="reports/latest.html")
    parser.add_argument("--cli-only", action="store_true")
    args = parser.parse_args()

    data = compute_report_data(
        log_path=Path(args.log),
        apartments_path=Path(args.apartments),
    )
    print_cli_report(data)

    if not args.cli_only:
        # HTML rendering wired in Task 9
        pass


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_report.py -v`
Expected: 1 passed.

- [ ] **Step 6: Smoke-test CLI output**

Run:
```bash
python scripts/report.py \
    --log tests/fixtures/sample_commute_log.csv \
    --apartments tests/fixtures/sample_apartments.json \
    --cli-only
```
Expected: prints two slot sections (`07:00` and `07:30`) with cluster A ranked first.

- [ ] **Step 7: Commit**

```bash
git add scripts/report.py tests/test_report.py tests/fixtures/sample_commute_log.csv
git commit -m "feat: add CLI report computing per-cluster commute stats"
```

---

### Task 9: Implement HTML report generation

**Files:**
- Create: `templates/report.html.j2`
- Modify: `scripts/report.py` (wire HTML rendering)
- Test: `tests/test_report_html.py`

- [ ] **Step 1: Write failing test for HTML rendering**

`tests/test_report_html.py`:
```python
from pathlib import Path
from scripts.report import render_html


def test_render_html_contains_cluster_names_and_chart_libs(tmp_path):
    out = tmp_path / "out.html"
    render_html(
        log_path=Path("tests/fixtures/sample_commute_log.csv"),
        apartments_path=Path("tests/fixtures/sample_apartments.json"),
        template_path=Path("templates/report.html.j2"),
        output_path=out,
    )
    html = out.read_text(encoding="utf-8")
    assert "Test Cluster A" in html
    assert "Test Cluster B" in html
    assert "chart.js" in html.lower()  # CDN script tag
    assert "07:00" in html
    assert "07:30" in html
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_report_html.py -v`
Expected: FAIL — `render_html` doesn't exist.

- [ ] **Step 3: Write `templates/report.html.j2`**

```jinja
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Commute Tracker — {{ destination_name }}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  body { font-family: -apple-system, system-ui, sans-serif; max-width: 980px; margin: 24px auto; padding: 0 16px; }
  h1 { font-size: 22px; }
  table { border-collapse: collapse; width: 100%; margin: 12px 0 28px; font-size: 13px; }
  th, td { border: 1px solid #ddd; padding: 6px 10px; text-align: left; }
  th { background: #f4f4f4; }
  td.num { text-align: right; font-variant-numeric: tabular-nums; }
  .flag-warn { color: #c0392b; }
  .flag-unstable { color: #e67e22; }
  canvas { max-width: 100%; }
  .meta { color: #666; font-size: 12px; }
</style>
</head>
<body>
<h1>Commute Tracker — {{ destination_name }}</h1>
<p class="meta">Updated: {{ updated_at }} · Mode: motorcycle (driving × {{ moto_factor }})</p>

{% for slot in slots %}
<h2>Slot {{ slot[:2] }}:{{ slot[2:] }}</h2>
<table>
  <tr>
    <th>#</th><th>Cluster</th><th>District</th>
    <th>Mean</th><th>p50</th><th>p90</th><th>Std</th><th>Samples</th><th>Flags</th>
  </tr>
  {% for entry in rankings[slot] %}
    {% set apt = apartments[entry.apartment_id] %}
    {% set s = per_apartment_slot[entry.apartment_id][slot] %}
  <tr>
    <td>{{ entry.rank }}</td>
    <td>{{ apt.cluster_name }}</td>
    <td>{{ apt.get("district", "") }}</td>
    <td class="num">{{ "%.1f"|format(s.mean) }}</td>
    <td class="num">{{ "%.1f"|format(s.p50) }}</td>
    <td class="num">{{ "%.1f"|format(s.p90) }}</td>
    <td class="num">{{ "%.1f"|format(s.std) }}</td>
    <td class="num">{{ s.samples }}</td>
    <td>
      {% if s.p90 and s.p90 > 30 %}<span class="flag-warn">⚠️ p90&gt;30</span>{% endif %}
      {% if s.std and s.std > 8 %}<span class="flag-unstable">🎲 unstable</span>{% endif %}
    </td>
  </tr>
  {% endfor %}
</table>

<canvas id="chart-{{ slot }}" height="120"></canvas>
<script>
new Chart(document.getElementById('chart-{{ slot }}'), {
  type: 'bar',
  data: {
    labels: {{ rankings[slot] | map(attribute='apartment_id') | list | tojson }},
    datasets: [{
      label: 'Mean motorbike commute (min) — slot {{ slot }}',
      data: {{ rankings[slot] | map(attribute='mean') | list | tojson }},
    }]
  }
});
</script>
{% endfor %}

</body>
</html>
```

- [ ] **Step 4: Add `render_html` to `scripts/report.py`**

Append imports near top:
```python
from datetime import datetime
from jinja2 import Template
```

Append function before `main()`:
```python
def render_html(*, log_path, apartments_path, template_path, output_path):
    data = compute_report_data(log_path=log_path, apartments_path=apartments_path)
    template = Template(Path(template_path).read_text(encoding="utf-8"))

    rankings = {slot: data[f"ranking_{slot}"] for slot in config.SLOTS}

    html = template.render(
        destination_name=config.DESTINATION_NAME,
        moto_factor=config.MOTO_FACTOR,
        slots=config.SLOTS,
        apartments=data["apartments"],
        per_apartment_slot=data["per_apartment_slot"],
        rankings=rankings,
        updated_at=datetime.now().isoformat(timespec="minutes"),
    )
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(html, encoding="utf-8")
```

Update `main()` to call it:
```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default="data/commute_log.csv")
    parser.add_argument("--apartments", default="data/apartments.json")
    parser.add_argument("--html-out", default="reports/latest.html")
    parser.add_argument("--template", default="templates/report.html.j2")
    parser.add_argument("--cli-only", action="store_true")
    args = parser.parse_args()

    data = compute_report_data(
        log_path=Path(args.log),
        apartments_path=Path(args.apartments),
    )
    print_cli_report(data)

    if not args.cli_only:
        render_html(
            log_path=Path(args.log),
            apartments_path=Path(args.apartments),
            template_path=Path(args.template),
            output_path=Path(args.html_out),
        )
        print(f"\nHTML report: {args.html_out}")
```

- [ ] **Step 5: Run HTML test**

Run: `pytest tests/test_report_html.py -v`
Expected: 1 passed.

- [ ] **Step 6: Smoke-test full report generation**

Run:
```bash
python scripts/report.py \
    --log tests/fixtures/sample_commute_log.csv \
    --apartments tests/fixtures/sample_apartments.json \
    --html-out /tmp/report.html
open /tmp/report.html
```
Expected: HTML opens in browser, shows two slot sections with bar charts.

- [ ] **Step 7: Commit**

```bash
git add templates/report.html.j2 scripts/report.py tests/test_report_html.py
git commit -m "feat: render HTML dashboard with Chart.js bar charts"
```

---

### Task 10: Run full test suite

**Files:** none (verification step)

- [ ] **Step 1: Run all tests**

Run: `pytest tests/ -v`
Expected: all green (~14 tests).

- [ ] **Step 2: If anything fails, fix before proceeding**

Do not move to Task 11 if any test is red.

---

## Phase 3: Wire automation

### Task 11: Live API smoke test

**Files:** none (manual verification)

- [ ] **Step 1: Obtain Google Maps API key**

Anh creates Google Cloud project → enables Distance Matrix API → creates API key → sets quota limit (~$5/month max via Cloud Console quota page).

Detailed steps Anh follows in setup task (Task 14). For now the agent waits for Anh to provide the key.

- [ ] **Step 2: Live-call one apartment**

```bash
export GOOGLE_MAPS_API_KEY=<paste-key>
python scripts/track_commute.py --slot 0700 --apartments data/apartments.json --log /tmp/test_log.csv
cat /tmp/test_log.csv
```

Expected: 10 rows appended, all with `status=OK` (or sensible errors with explanation).

- [ ] **Step 3: Generate full report from live data**

```bash
python scripts/report.py --log /tmp/test_log.csv --html-out /tmp/test_report.html
open /tmp/test_report.html
```

Verify: durations look reasonable (15-35 minutes for motorcycle commute in Hanoi). If a cluster shows >40 min, double-check its lat/lng.

- [ ] **Step 4: Commit nothing yet — `/tmp` files are local-only**

This step does not touch the repo.

---

### Task 12: Write GitHub Actions workflow

**Files:**
- Create: `.github/workflows/track-commute.yml`

- [ ] **Step 1: Write the workflow**

```yaml
name: Track Commute

on:
  schedule:
    - cron: '0 0 * * *'      # 7:00 ICT (UTC+7)
    - cron: '30 0 * * *'     # 7:30 ICT
  workflow_dispatch:
    inputs:
      slot:
        description: 'Slot to run (0700 or 0730)'
        required: true
        default: '0700'

permissions:
  contents: write   # required for the auto-commit step

jobs:
  track:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install deps
        run: pip install -r requirements.txt

      - name: Determine slot
        id: slot
        run: |
          if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
            echo "slot=${{ github.event.inputs.slot }}" >> $GITHUB_OUTPUT
          elif [ "${{ github.event.schedule }}" = "0 0 * * *" ]; then
            echo "slot=0700" >> $GITHUB_OUTPUT
          else
            echo "slot=0730" >> $GITHUB_OUTPUT
          fi

      - name: Track commute
        env:
          GOOGLE_MAPS_API_KEY: ${{ secrets.GOOGLE_MAPS_API_KEY }}
        run: python scripts/track_commute.py --slot ${{ steps.slot.outputs.slot }}

      - name: Generate report
        run: python scripts/report.py --cli-only=false

      - name: Commit log + report
        run: |
          git config user.name "commute-bot"
          git config user.email "commute-bot@users.noreply.github.com"
          git add data/commute_log.csv reports/latest.html
          if git diff --cached --quiet; then
            echo "No changes to commit"
          else
            git commit -m "data: append slot ${{ steps.slot.outputs.slot }} log"
            git push
          fi
```

- [ ] **Step 2: Validate YAML**

Run:
```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/track-commute.yml')); print('YAML OK')"
```
Expected: `YAML OK`

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/track-commute.yml
git commit -m "ci: add GitHub Actions cron for 7:00 and 7:30 ICT"
```

---

### Task 13: Push to GitHub and verify CI

**Files:** none (manual)

- [ ] **Step 1: Anh creates a public GitHub repo**

Repo name suggestion: `apartment-commute-tracker`. Public visibility (data not sensitive — see Section 9 of spec for risk analysis).

- [ ] **Step 2: Anh adds the remote and pushes**

```bash
git remote add origin git@github.com:<username>/apartment-commute-tracker.git
git branch -M main
git push -u origin main
```

- [ ] **Step 3: Anh adds the API key to GitHub Secrets**

GitHub repo → Settings → Secrets and variables → Actions → New repository secret:
- Name: `GOOGLE_MAPS_API_KEY`
- Value: (paste key)

- [ ] **Step 4: Trigger workflow manually**

GitHub repo → Actions → "Track Commute" → Run workflow → choose slot `0700` → Run.

Wait ~1 minute. Verify:
- Job succeeds (green check)
- New commit on `main` from `commute-bot` updating `data/commute_log.csv` and `reports/latest.html`

- [ ] **Step 5: Verify cron is scheduled**

Actions tab should show "Track Commute" with both schedule entries listed under the workflow's "About" section. (GitHub may take a few hours before the first scheduled run actually fires for new repos — this is normal.)

---

### Task 14: Enable GitHub Pages

**Files:**
- Modify: `.github/workflows/track-commute.yml` (add Pages deployment)

GitHub Pages requires deploying via a workflow when source is "GitHub Actions" (preferred over the legacy `/reports` folder option, since the latter only updates when files change in that exact folder on push).

- [ ] **Step 1: Add Pages deployment job**

Append a second job to `.github/workflows/track-commute.yml`:

```yaml
  deploy-pages:
    needs: track
    runs-on: ubuntu-latest
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main           # ensure we read the just-committed log + report
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: reports
      - name: Deploy
        id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 2: Anh enables Pages in repo settings**

GitHub repo → Settings → Pages → "Build and deployment" source: **GitHub Actions**.

- [ ] **Step 3: Trigger workflow manually again**

Verify both jobs succeed (`track` then `deploy-pages`). Note the deployed URL printed in the `Deploy` step output (form: `https://<username>.github.io/apartment-commute-tracker/`).

- [ ] **Step 4: Open URL on phone**

Anh opens the URL on phone. Verify dashboard renders, charts load.

- [ ] **Step 5: Commit workflow update**

```bash
git add .github/workflows/track-commute.yml
git commit -m "ci: deploy report to GitHub Pages"
git push
```

---

### Task 15: Write user-facing setup doc

**Files:**
- Create: `docs/SETUP.md`
- Modify: `README.md` (link to SETUP.md)

- [ ] **Step 1: Write `docs/SETUP.md`**

```markdown
# Setup Guide

## 1. Tạo Google Cloud project + API key

1. Truy cập https://console.cloud.google.com
2. Tạo project mới (ví dụ: `commute-tracker`)
3. Vào "APIs & Services" → "Library" → tìm **Distance Matrix API** → Enable
4. Vào "APIs & Services" → "Credentials" → Create credentials → API key
5. Copy API key

## 2. Set quota limit (tránh charge bất ngờ)

1. Vào "APIs & Services" → "Distance Matrix API" → "Quotas"
2. Set "Requests per day" ≤ 1000 (đủ dư cho task này)
3. Cloud Console → Billing → "Budgets & alerts" → tạo budget $5/tháng với email alert

## 3. Add API key vào GitHub Secrets

GitHub repo → Settings → Secrets and variables → Actions → New repository secret
- Name: `GOOGLE_MAPS_API_KEY`
- Value: <paste key>

## 4. Bật GitHub Pages

GitHub repo → Settings → Pages → Build and deployment source: **GitHub Actions**

## 5. Trigger lần đầu

GitHub repo → Actions → "Track Commute" → Run workflow → Run.

Sau ~1 phút, mở URL Pages (ví dụ `https://<username>.github.io/apartment-commute-tracker/`) để xem dashboard.

## 6. Sau đó cron tự chạy

7:00 và 7:30 ICT mỗi ngày, GitHub Actions tự gọi API, log dữ liệu, regenerate report, deploy Pages.

## Sửa danh sách chung cư

Edit `data/apartments.json` trên máy hoặc qua GitHub web → commit + push. Lần cron tiếp theo sẽ dùng list mới.

## Xem log thô

`data/commute_log.csv` có toàn bộ history. Anh chạy `python scripts/report.py` local để in summary ra terminal.
```

- [ ] **Step 2: Update `README.md` to link**

Replace the "## Setup" stub with:
```markdown
## Setup

See [docs/SETUP.md](docs/SETUP.md) for step-by-step instructions (Google Cloud, GitHub Secrets, Pages).
```

- [ ] **Step 3: Commit**

```bash
git add docs/SETUP.md README.md
git commit -m "docs: add setup guide"
git push
```

---

### Task 16: Final acceptance check

**Files:** none (verification)

- [ ] **Step 1: Verify all acceptance criteria from spec Section 10**

Run through Section 10 of `docs/superpowers/specs/2026-05-04-apartment-commute-tracker-design.md`. For each criterion, confirm:

- `data/apartments.json` has 10 clusters, schema-valid, Anh approved
- `track_commute.py` runs successfully against live API (Task 11)
- `report.py` prints expected CLI output (Task 8 Step 6)
- `reports/latest.html` renders correctly (Task 9 Step 6 + Task 14 Step 4)
- After 3 days, GitHub Actions has 6 successful runs (verify in Actions tab)
- GitHub Pages URL accessible from phone
- After 7 days, every cluster has ≥14 data points (`grep -c <cluster_id>,0700 data/commute_log.csv` ≥ 7, same for 0730)

- [ ] **Step 2: Tag release**

```bash
git tag -a v1.0 -m "Initial release: commute tracker for 10 candidate clusters"
git push --tags
```

---

## Summary

Total tasks: **16**.

- Tasks 1-2: bootstrap + Phase 1 research
- Tasks 3-10: Phase 2 implementation (TDD, 4 lib modules + 2 orchestrators + HTML)
- Tasks 11-16: live wiring (API key, GitHub Actions, Pages, docs, acceptance)

Each task ends with a commit. Commits chronicle progress incrementally.
