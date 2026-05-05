from unittest.mock import patch, MagicMock
import pytest
from scripts.lib.routing_client import fetch_commute, RoutingAPIError


def _ok_response():
    return {
        "code": "Ok",
        "durations": [[1080.0]],     # 18 min in seconds
        "distances": [[9400.0]],     # meters
    }


@patch("scripts.lib.routing_client.requests.get")
def test_fetch_commute_success(mock_get):
    mock_get.return_value = MagicMock(
        status_code=200, json=lambda: _ok_response()
    )
    result = fetch_commute(
        origin_lat=21.0145, origin_lng=105.7423,
        dest_lat=21.0263, dest_lng=105.8094,
        api_key="fake-key",
    )
    assert result["duration_min"] == 18.0
    # driving-traffic profile already includes traffic
    assert result["duration_in_traffic_min"] == 18.0
    assert result["distance_km"] == 9.4


@patch("scripts.lib.routing_client.requests.get")
def test_fetch_commute_sends_lng_lat_in_path(mock_get):
    """Mapbox requires lng,lat in URL path with semicolon separator."""
    mock_get.return_value = MagicMock(
        status_code=200, json=lambda: _ok_response()
    )
    fetch_commute(
        origin_lat=21.0145, origin_lng=105.7423,
        dest_lat=21.0263, dest_lng=105.8094,
        api_key="x",
    )
    called_url = mock_get.call_args.args[0]
    assert "105.7423,21.0145;105.8094,21.0263" in called_url
    assert "driving-traffic" in called_url


@patch("scripts.lib.routing_client.requests.get")
def test_fetch_commute_http_error(mock_get):
    mock_get.return_value = MagicMock(status_code=401, text="Unauthorized")
    with pytest.raises(RoutingAPIError, match="HTTP 401"):
        fetch_commute(
            origin_lat=21.0, origin_lng=105.8,
            dest_lat=21.0, dest_lng=105.8,
            api_key="x",
        )


@patch("scripts.lib.routing_client.requests.get")
def test_fetch_commute_rate_limit(mock_get):
    mock_get.return_value = MagicMock(status_code=429, text="Rate limit")
    with pytest.raises(RoutingAPIError, match="HTTP 429"):
        fetch_commute(
            origin_lat=21.0, origin_lng=105.8,
            dest_lat=21.0, dest_lng=105.8,
            api_key="x",
        )


@patch("scripts.lib.routing_client.requests.get")
def test_fetch_commute_no_route_null(mock_get):
    """Mapbox returns null in matrix when no route possible."""
    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: {"code": "Ok", "durations": [[None]], "distances": [[None]]},
    )
    with pytest.raises(RoutingAPIError, match="no route"):
        fetch_commute(
            origin_lat=21.0, origin_lng=105.8,
            dest_lat=21.0, dest_lng=105.8,
            api_key="x",
        )


@patch("scripts.lib.routing_client.requests.get")
def test_fetch_commute_api_error_code(mock_get):
    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: {"code": "InvalidInput", "message": "Bad coordinates"},
    )
    with pytest.raises(RoutingAPIError, match="code=InvalidInput"):
        fetch_commute(
            origin_lat=21.0, origin_lng=105.8,
            dest_lat=21.0, dest_lng=105.8,
            api_key="x",
        )


@patch("scripts.lib.routing_client.requests.get")
def test_fetch_commute_malformed_payload(mock_get):
    mock_get.return_value = MagicMock(
        status_code=200,
        json=lambda: {"code": "Ok"},  # missing durations/distances
    )
    with pytest.raises(RoutingAPIError, match="unexpected payload"):
        fetch_commute(
            origin_lat=21.0, origin_lng=105.8,
            dest_lat=21.0, dest_lng=105.8,
            api_key="x",
        )
