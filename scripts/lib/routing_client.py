"""Thin wrapper around Mapbox Directions Matrix API.

Uses the `driving-traffic` profile which factors real-time and historical
traffic into the route duration. The motorbike correction is applied
downstream via config.MOTO_FACTOR.
"""

import requests


class RoutingAPIError(Exception):
    pass


_BASE_URL = "https://api.mapbox.com/directions-matrix/v1/mapbox/driving-traffic"


def fetch_commute(*, origin_lat, origin_lng, dest_lat, dest_lng, api_key, timeout=15):
    # Mapbox uses lng,lat order; coordinates separated by semicolon.
    coords = f"{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
    url = f"{_BASE_URL}/{coords}"
    params = {
        "sources": "0",
        "destinations": "1",
        "annotations": "duration,distance",
        "access_token": api_key,
    }
    resp = requests.get(url, params=params, timeout=timeout)
    if resp.status_code != 200:
        raise RoutingAPIError(f"HTTP {resp.status_code}: {resp.text[:200]}")
    payload = resp.json()
    if payload.get("code") != "Ok":
        raise RoutingAPIError(f"code={payload.get('code')}: {payload.get('message', '')}")
    try:
        duration_s = payload["durations"][0][0]
        distance_m = payload["distances"][0][0]
    except (KeyError, IndexError, TypeError) as e:
        raise RoutingAPIError(f"unexpected payload: {payload}") from e
    if duration_s is None or distance_m is None:
        raise RoutingAPIError("no route found (null in matrix)")
    duration_min = duration_s / 60.0
    return {
        "duration_min": duration_min,
        "duration_in_traffic_min": duration_min,
        "distance_km": distance_m / 1000.0,
    }
