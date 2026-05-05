"""Thin wrapper around OpenRouteService Matrix API.

ORS does not provide real-time traffic data — duration_in_traffic_min is set
equal to duration_min. The motorbike correction is applied downstream via
config.MOTO_FACTOR (a heuristic for Hanoi peak-hour motorbike vs car).
"""

import requests


class RoutingAPIError(Exception):
    pass


_BASE_URL = "https://api.openrouteservice.org/v2/matrix/driving-car"


def fetch_commute(*, origin_lat, origin_lng, dest_lat, dest_lng, api_key, timeout=15):
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
    }
    body = {
        "locations": [
            [origin_lng, origin_lat],
            [dest_lng, dest_lat],
        ],
        "sources": [0],
        "destinations": [1],
        "metrics": ["duration", "distance"],
        "units": "km",
    }
    resp = requests.post(_BASE_URL, headers=headers, json=body, timeout=timeout)
    if resp.status_code != 200:
        raise RoutingAPIError(f"HTTP {resp.status_code}: {resp.text[:200]}")
    payload = resp.json()
    try:
        duration_s = payload["durations"][0][0]
        distance_km = payload["distances"][0][0]
    except (KeyError, IndexError, TypeError) as e:
        raise RoutingAPIError(f"unexpected payload: {payload}") from e
    if duration_s is None or distance_km is None:
        raise RoutingAPIError("no route found (null in matrix)")
    duration_min = duration_s / 60.0
    return {
        "duration_min": duration_min,
        "duration_in_traffic_min": duration_min,
        "distance_km": distance_km,
    }
