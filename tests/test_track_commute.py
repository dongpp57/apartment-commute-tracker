import json
import csv
from unittest.mock import patch
from pathlib import Path
from scripts.track_commute import run_tracking
from scripts.lib.maps_client import MapsAPIError


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
