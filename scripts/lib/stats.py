"""Pure stats helpers — no I/O."""

import statistics


def summarize_durations(durations):
    """Calculate summary statistics for a list of duration values.

    Args:
        durations: List of floats (may include None values)

    Returns:
        Dict with keys: mean, p50, p90, min, max, std, samples
        - Filters out None values
        - If empty after filter: all stats None except samples=0
        - p50/p90 use linear interpolation (numpy default)
        - All floats rounded to 2 decimals
        - std uses population stdev. If samples=1, std=0.0
    """
    durations = [d for d in durations if d is not None]
    n = len(durations)
    if n == 0:
        return {
            "mean": None, "p50": None, "p90": None,
            "min": None, "max": None, "std": None, "samples": 0,
        }
    sorted_d = sorted(durations)
    return {
        "mean": round(sum(sorted_d) / n, 2),
        "p50": _percentile(sorted_d, 50),
        "p90": _percentile(sorted_d, 90),
        "min": min(sorted_d),
        "max": max(sorted_d),
        "std": round(statistics.pstdev(sorted_d), 2) if n > 1 else 0.0,
        "samples": n,
    }


def _percentile(sorted_values, p):
    """Linear interpolation percentile (matches numpy default)."""
    if not sorted_values:
        return None
    n = len(sorted_values)
    rank = (p / 100) * (n - 1)
    low = int(rank)
    high = min(low + 1, n - 1)
    weight = rank - low
    return round(sorted_values[low] * (1 - weight) + sorted_values[high] * weight, 2)


def rank_apartments(summaries):
    """Sort apartments by mean ascending; exclude entries with no data.

    Args:
        summaries: Dict mapping apartment_id to stats dict with 'mean' and other keys

    Returns:
        List of dicts sorted ascending by mean, each with:
        - apartment_id: original key
        - all original stats keys
        - rank: 1-indexed position in sorted list
    """
    valid = [
        {"apartment_id": aid, **s}
        for aid, s in summaries.items()
        if s.get("mean") is not None
    ]
    valid.sort(key=lambda x: x["mean"])
    for i, entry in enumerate(valid, start=1):
        entry["rank"] = i
    return valid
