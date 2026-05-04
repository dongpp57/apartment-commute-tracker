"""Generate CLI summary + HTML dashboard from commute_log.csv."""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

# Same dual-mode import as track_commute.py
try:
    from scripts.lib.stats import summarize_durations, rank_apartments
    from scripts.lib import config
except ModuleNotFoundError:
    _project_root = str(Path(__file__).parent.parent)
    if _project_root not in sys.path:
        sys.path.insert(0, _project_root)
    from scripts.lib.stats import summarize_durations, rank_apartments
    from scripts.lib import config


def compute_report_data(*, log_path, apartments_path):
    apartments = json.loads(Path(apartments_path).read_text(encoding="utf-8"))
    apt_by_id = {a["id"]: a for a in apartments}

    df = pd.read_csv(log_path, dtype={"slot": str})
    # Normalise slot values: "700" → "0700", already "0700" stays "0700"
    df["slot"] = df["slot"].str.zfill(4)
    df = df[df["status"] == "OK"]
    df["duration_motorcycle_min"] = pd.to_numeric(
        df["duration_motorcycle_min"], errors="coerce"
    )

    per_apt_slot = defaultdict(dict)
    for apt_id in apt_by_id:
        for slot in config.SLOTS:
            durations = df[
                (df["apartment_id"] == apt_id) & (df["slot"] == slot)
            ]["duration_motorcycle_min"].tolist()
            per_apt_slot[apt_id][slot] = summarize_durations(durations)

    rankings = {}
    for slot in config.SLOTS:
        summaries = {aid: stats[slot] for aid, stats in per_apt_slot.items()}
        rankings[f"ranking_{slot}"] = rank_apartments(summaries)

    return {
        "per_apartment_slot": dict(per_apt_slot),
        "apartments": apt_by_id,
        **rankings,
    }


def print_cli_report(data):
    print(f"COMMUTE TIME REPORT — Destination: {config.DESTINATION_NAME}")
    print(f"Mode: motorcycle (driving x {config.MOTO_FACTOR})")
    print()

    for slot in config.SLOTS:
        print(f"=== SLOT {slot[:2]}:{slot[2:]} ===")
        print(f"{'Cluster':<28} {'Mean':>6} {'p50':>6} {'p90':>6} {'Samples':>8}  Flags")
        for entry in data[f"ranking_{slot}"]:
            apt = data["apartments"].get(entry["apartment_id"], {})
            name = apt.get("cluster_name", entry["apartment_id"])[:27]
            stats = data["per_apartment_slot"][entry["apartment_id"]][slot]
            flags = []
            if stats.get("p90") and stats["p90"] > 30:
                flags.append("⚠️p90>30")
            if stats.get("std") and stats["std"] > 8:
                flags.append("🎲unstable")
            print(
                f"{name:<28} "
                f"{stats['mean']:>6.1f} {stats['p50']:>6.1f} {stats['p90']:>6.1f} "
                f"{stats['samples']:>8}  {' '.join(flags)}"
            )
        print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default="data/commute_log.csv")
    parser.add_argument("--apartments", default="data/apartments.json")
    parser.add_argument("--html-out", default="reports/latest.html")
    parser.add_argument("--cli-only", action="store_true")
    args = parser.parse_args()

    data = compute_report_data(
        log_path=Path(args.log),
        apartments_path=Path(args.apartments),
    )
    print_cli_report(data)

    if not args.cli_only:
        # HTML rendering wired in Task 9
        pass


if __name__ == "__main__":
    main()
