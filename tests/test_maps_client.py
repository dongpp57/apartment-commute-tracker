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


@patch("scripts.lib.maps_client.requests.get")
def test_fetch_commute_http_error(mock_get):
    mock_get.return_value = MagicMock(status_code=500, text="Server Error")
    with pytest.raises(MapsAPIError, match="HTTP 500"):
        fetch_commute(
            origin_lat=21.0, origin_lng=105.8,
            dest_lat=21.0, dest_lng=105.8,
            api_key="x",
        )


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
