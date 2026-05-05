"""Loop apartments, call routing API, append to log.

Morning slots (0700, 0730): measure home → work commute.
Evening slots (1730, 1800): measure work → home commute (reversed direction).
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Support both `python scripts/track_commute.py` (CLI) and `import scripts.track_commute` (pytest).
try:
    from scripts.lib.routing_client import fetch_commute, RoutingAPIError
    from scripts.lib.log_writer import append_row
    from scripts.lib import config
except ModuleNotFoundError:
    _project_root = str(Path(__file__).parent.parent)
    if _project_root not in sys.path:
        sys.path.insert(0, _project_root)
    from scripts.lib.routing_client import fetch_commute, RoutingAPIError
    from scripts.lib.log_writer import append_row
    from scripts.lib import config


ICT = timezone(timedelta(hours=7))


def run_tracking(*, apartments_path, log_path, slot, api_key):
    with open(apartments_path, encoding="utf-8") as f:
        apartments = json.load(f)

    timestamp = datetime.now(tz=ICT).replace(microsecond=0).isoformat()

    is_evening = slot in config.EVENING_SLOTS
    direction = "work_to_home" if is_evening else "home_to_work"

    for apt in apartments:
        row = {
            "timestamp_ict": timestamp,
            "apartment_id": apt["id"],
            "slot": slot,
            "direction": direction,
        }
        try:
            if is_evening:
                # Work → Home: origin = NCT, destination = apartment
                origin_lat, origin_lng = config.DESTINATION_LAT, config.DESTINATION_LNG
                dest_lat, dest_lng = apt["lat"], apt["lng"]
            else:
                # Home → Work: origin = apartment, destination = NCT
                origin_lat, origin_lng = apt["lat"], apt["lng"]
                dest_lat, dest_lng = config.DESTINATION_LAT, config.DESTINATION_LNG

            result = fetch_commute(
                origin_lat=origin_lat, origin_lng=origin_lng,
                dest_lat=dest_lat, dest_lng=dest_lng,
                api_key=api_key,
            )
            # Mapbox driving-traffic profile: duration already factors live + historical traffic.
            duration_in_traffic = result["duration_min"]
            duration_motorcycle = duration_in_traffic * config.MOTO_FACTOR
            row.update({
                "duration_min": round(duration_in_traffic, 2),
                "duration_in_traffic_min": round(duration_in_traffic, 2),
                "duration_motorcycle_min": round(duration_motorcycle, 2),
                "distance_km": round(result["distance_km"], 2),
                "status": "OK",
            })
        except RoutingAPIError as e:
            row["status"] = f"ERROR_{type(e).__name__}_{str(e)[:60]}"

        append_row(log_path, row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", required=True, choices=config.SLOTS)
    parser.add_argument("--apartments", default="data/apartments.json")
    parser.add_argument("--log", default="data/commute_log.csv")
    args = parser.parse_args()

    api_key = os.environ.get("MAPBOX_TOKEN")
    if not api_key:
        print("ERROR: MAPBOX_TOKEN env var not set", file=sys.stderr)
        sys.exit(1)

    run_tracking(
        apartments_path=Path(args.apartments),
        log_path=Path(args.log),
        slot=args.slot,
        api_key=api_key,
    )


if __name__ == "__main__":
    main()
