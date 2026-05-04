import csv
from unittest.mock import patch
from pathlib import Path
from scripts.track_commute import run_tracking
from scripts.lib.routing_client import RoutingAPIError
from scripts.lib import config


@patch("scripts.track_commute.fetch_commute")
def test_run_tracking_writes_one_row_per_apartment(mock_fetch, tmp_path):
    # ORS shape: duration_in_traffic_min mirrors duration_min (no traffic data)
    mock_fetch.return_value = {
        "duration_min": 18.0,
        "duration_in_traffic_min": 18.0,
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
    # in_traffic = duration * PEAK_HOUR_TRAFFIC_FACTOR
    expected_traffic = 18.0 * config.PEAK_HOUR_TRAFFIC_FACTOR
    assert abs(float(rows[0]["duration_in_traffic_min"]) - expected_traffic) < 0.01
    # motorbike = in_traffic * MOTO_FACTOR
    expected_moto = expected_traffic * config.MOTO_FACTOR
    assert abs(float(rows[0]["duration_motorcycle_min"]) - expected_moto) < 0.01


@patch("scripts.track_commute.fetch_commute")
def test_run_tracking_records_errors_and_continues(mock_fetch, tmp_path):
    mock_fetch.side_effect = [
        RoutingAPIError("HTTP 429: rate limit"),
        {"duration_min": 18.0, "duration_in_traffic_min": 18.0, "distance_km": 9.4},
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
    assert rows[0]["duration_min"] == ""
    assert rows[1]["status"] == "OK"
