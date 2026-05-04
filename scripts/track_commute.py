"""Loop apartments, call Maps API, append to log."""

import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Support both `python scripts/track_commute.py` (CLI) and `import scripts.track_commute` (pytest).
# When run as a script, `scripts` is not a package on sys.path, so we insert the project root
# and use relative-style lib imports. When imported as a module, absolute `scripts.lib` imports work.
try:
    from scripts.lib.maps_client import fetch_commute, MapsAPIError
    from scripts.lib.log_writer import append_row
    from scripts.lib import config
except ModuleNotFoundError:
    # Running as `python scripts/track_commute.py` — project root not yet on path
    _project_root = str(Path(__file__).parent.parent)
    if _project_root not in sys.path:
        sys.path.insert(0, _project_root)
    from scripts.lib.maps_client import fetch_commute, MapsAPIError
    from scripts.lib.log_writer import append_row
    from scripts.lib import config


ICT = timezone(timedelta(hours=7))


def run_tracking(*, apartments_path, log_path, slot, api_key):
    with open(apartments_path, encoding="utf-8") as f:
        apartments = json.load(f)

    timestamp = datetime.now(tz=ICT).replace(microsecond=0).isoformat()

    for apt in apartments:
        row = {
            "timestamp_ict": timestamp,
            "apartment_id": apt["id"],
            "slot": slot,
        }
        try:
            result = fetch_commute(
                origin_lat=apt["lat"],
                origin_lng=apt["lng"],
                dest_lat=config.DESTINATION_LAT,
                dest_lng=config.DESTINATION_LNG,
                api_key=api_key,
            )
            row.update({
                "duration_min": round(result["duration_min"], 2),
                "duration_in_traffic_min": round(result["duration_in_traffic_min"], 2),
                "duration_motorcycle_min": round(
                    result["duration_in_traffic_min"] * config.MOTO_FACTOR, 2
                ),
                "distance_km": round(result["distance_km"], 2),
                "status": "OK",
            })
        except MapsAPIError as e:
            row["status"] = f"ERROR_{type(e).__name__}_{str(e)[:60]}"

        append_row(log_path, row)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--slot", required=True, choices=config.SLOTS)
    parser.add_argument("--apartments", default="data/apartments.json")
    parser.add_argument("--log", default="data/commute_log.csv")
    args = parser.parse_args()

    api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_MAPS_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    run_tracking(
        apartments_path=Path(args.apartments),
        log_path=Path(args.log),
        slot=args.slot,
        api_key=api_key,
    )


if __name__ == "__main__":
    main()
