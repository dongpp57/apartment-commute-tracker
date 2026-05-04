"""Thin wrapper around Google Maps Distance Matrix API."""

import time
import requests


class MapsAPIError(Exception):
    pass


_BASE_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"


def fetch_commute(*, origin_lat, origin_lng, dest_lat, dest_lng, api_key, timeout=15):
    params = {
        "origins": f"{origin_lat},{origin_lng}",
        "destinations": f"{dest_lat},{dest_lng}",
        "mode": "driving",
        "departure_time": str(int(time.time())),
        "traffic_model": "best_guess",
        "key": api_key,
    }
    resp = requests.get(_BASE_URL, params=params, timeout=timeout)
    if resp.status_code != 200:
        raise MapsAPIError(f"HTTP {resp.status_code}: {resp.text[:200]}")
    payload = resp.json()
    if payload.get("status") != "OK":
        raise MapsAPIError(f"top-level status={payload.get('status')}")
    element = payload["rows"][0]["elements"][0]
    if element.get("status") != "OK":
        raise MapsAPIError(f"element status={element.get('status')}")
    return {
        "duration_min": element["duration"]["value"] / 60.0,
        "duration_in_traffic_min": element["duration_in_traffic"]["value"] / 60.0,
        "distance_km": element["distance"]["value"] / 1000.0,
    }
