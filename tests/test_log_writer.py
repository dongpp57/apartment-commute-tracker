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
    assert len(lines) == 2
    assert "ERROR_quota_exceeded" in lines[1]
    assert lines[1].count(",") == 7  # 8 columns = 7 commas
