from unittest.mock import patch, MagicMock
import pytest
from scripts.lib.routing_client import fetch_commute, RoutingAPIError


def _ok_response():
    return {
        "durations": [[1080.0]],   # 18 min in seconds
        "distances": [[9.4]],      # km (units=km in request)
    }


@patch("scripts.lib.routing_client.requests.post")
def test_fetch_commute_success(mock_post):
    mock_post.return_value = MagicMock(
        status_code=200, json=lambda: _ok_response()
    )
    result = fetch_commute(
        origin_lat=21.0145, origin_lng=105.7423,
        dest_lat=21.0263, dest_lng=105.8094,
        api_key="fake-key",
    )
    assert result["duration_min"] == 18.0
    assert result["duration_in_traffic_min"] == 18.0  # ORS has no traffic, mirrors duration
    assert result["distance_km"] == 9.4


@patch("scripts.lib.routing_client.requests.post")
def test_fetch_commute_sends_lng_lat_order(mock_post):
    """ORS requires [lng, lat] coords — verify we don't accidentally swap."""
    mock_post.return_value = MagicMock(
        status_code=200, json=lambda: _ok_response()
    )
    fetch_commute(
        origin_lat=21.0145, origin_lng=105.7423,
        dest_lat=21.0263, dest_lng=105.8094,
        api_key="x",
    )
    sent_body = mock_post.call_args.kwargs["json"]
    assert sent_body["locations"] == [
        [105.7423, 21.0145],
        [105.8094, 21.0263],
    ]


@patch("scripts.lib.routing_client.requests.post")
def test_fetch_commute_http_error(mock_post):
    mock_post.return_value = MagicMock(status_code=403, text="Forbidden")
    with pytest.raises(RoutingAPIError, match="HTTP 403"):
        fetch_commute(
            origin_lat=21.0, origin_lng=105.8,
            dest_lat=21.0, dest_lng=105.8,
            api_key="x",
        )


@patch("scripts.lib.routing_client.requests.post")
def test_fetch_commute_quota_error(mock_post):
    mock_post.return_value = MagicMock(status_code=429, text="Rate limit exceeded")
    with pytest.raises(RoutingAPIError, match="HTTP 429"):
        fetch_commute(
            origin_lat=21.0, origin_lng=105.8,
            dest_lat=21.0, dest_lng=105.8,
            api_key="x",
        )


@patch("scripts.lib.routing_client.requests.post")
def test_fetch_commute_no_route_null(mock_post):
    """ORS returns null in matrix when no route possible."""
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"durations": [[None]], "distances": [[None]]},
    )
    with pytest.raises(RoutingAPIError, match="no route"):
        fetch_commute(
            origin_lat=21.0, origin_lng=105.8,
            dest_lat=21.0, dest_lng=105.8,
            api_key="x",
        )


@patch("scripts.lib.routing_client.requests.post")
def test_fetch_commute_malformed_payload(mock_post):
    mock_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"error": "Something broke"},
    )
    with pytest.raises(RoutingAPIError, match="unexpected payload"):
        fetch_commute(
            origin_lat=21.0, origin_lng=105.8,
            dest_lat=21.0, dest_lng=105.8,
            api_key="x",
        )
