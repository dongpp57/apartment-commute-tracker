from pathlib import Path
from scripts.report import compute_report_data


def test_compute_report_data_groups_by_apartment_and_slot():
    log_path = Path("tests/fixtures/sample_commute_log.csv")
    apartments_path = Path("tests/fixtures/sample_apartments.json")
    data = compute_report_data(log_path=log_path, apartments_path=apartments_path)

    a_700 = data["per_apartment_slot"]["test-cluster-a"]["0700"]
    assert a_700["samples"] == 3
    assert a_700["mean"] is not None

    b_700 = data["per_apartment_slot"]["test-cluster-b"]["0700"]
    assert b_700["samples"] == 2  # 3 rows but 1 is ERROR

    assert "ranking_0700" in data
    assert data["ranking_0700"][0]["apartment_id"] == "test-cluster-a"
