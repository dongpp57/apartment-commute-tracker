import csv
from unittest.mock import patch
from pathlib import Path
from scripts.track_commute import run_tracking
from scripts.lib.routing_client import RoutingAPIError
from scripts.lib import config


@patch("scripts.track_commute.fetch_commute")
def test_run_tracking_morning_slot_home_to_work(mock_fetch, tmp_path):
    mock_fetch.return_value = {
        "duration_min": 18.0,
        "duration_in_traffic_min": 18.0,
        "distance_km": 9.4,
    }
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
    assert rows[0]["direction"] == "home_to_work"
    assert rows[0]["status"] == "OK"

    # Morning: origin = apartment, dest = NCT
    first_call_kwargs = mock_fetch.call_args_list[0].kwargs
    assert first_call_kwargs["origin_lat"] == 21.0145  # apartment a
    assert first_call_kwargs["origin_lng"] == 105.7423
    assert first_call_kwargs["dest_lat"] == config.DESTINATION_LAT
    assert first_call_kwargs["dest_lng"] == config.DESTINATION_LNG


@patch("scripts.track_commute.fetch_commute")
def test_run_tracking_evening_slot_reverses_direction(mock_fetch, tmp_path):
    mock_fetch.return_value = {
        "duration_min": 20.0,
        "duration_in_traffic_min": 20.0,
        "distance_km": 9.4,
    }
    log_path = tmp_path / "commute_log.csv"

    run_tracking(
        apartments_path=Path("tests/fixtures/sample_apartments.json"),
        log_path=log_path,
        slot="1730",
        api_key="fake-key",
    )

    with open(log_path) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert rows[0]["direction"] == "work_to_home"

    # Evening: origin = NCT, dest = apartment
    first_call_kwargs = mock_fetch.call_args_list[0].kwargs
    assert first_call_kwargs["origin_lat"] == config.DESTINATION_LAT
    assert first_call_kwargs["origin_lng"] == config.DESTINATION_LNG
    assert first_call_kwargs["dest_lat"] == 21.0145
    assert first_call_kwargs["dest_lng"] == 105.7423


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
