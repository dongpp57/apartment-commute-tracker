from scripts.lib.stats import summarize_durations, rank_apartments


def test_summarize_basic():
    durations = [10, 12, 14, 16, 18, 20, 22, 24, 26, 28]
    result = summarize_durations(durations)
    assert result["mean"] == 19.0
    assert result["p50"] == 19.0
    assert result["p90"] == 26.2
    assert result["min"] == 10
    assert result["max"] == 28
    assert result["samples"] == 10


def test_summarize_empty():
    result = summarize_durations([])
    assert result["samples"] == 0
    assert result["mean"] is None
    assert result["p50"] is None


def test_rank_by_mean_ascending():
    summaries = {
        "a": {"mean": 25.0, "samples": 10},
        "b": {"mean": 18.0, "samples": 10},
        "c": {"mean": 22.0, "samples": 10},
        "d": {"mean": None, "samples": 0},  # excluded
    }
    ranking = rank_apartments(summaries)
    assert [r["apartment_id"] for r in ranking] == ["b", "c", "a"]
    assert ranking[0]["rank"] == 1
