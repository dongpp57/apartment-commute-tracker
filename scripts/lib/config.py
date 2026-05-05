"""Single source of truth for tracker constants."""

DESTINATION_LAT = 21.0263
DESTINATION_LNG = 105.8094
DESTINATION_NAME = "Vincom Nguyễn Chí Thanh"

MOTO_FACTOR = 0.615
# Default fallback factor: Mapbox car duration → Hanoi motorbike duration.
# Mean of 4 Google-Maps-calibrated clusters on 2026-05-05 (HD Mon, Smart City,
# Mỹ Đình Pearl, Hồ Gươm Plaza). Per-cluster overrides live in
# data/apartments.json under "calibration_factor" — the orchestrator prefers
# that value when present.

# Morning slots = home → work; Evening slots = work → home (reverse direction).
SLOTS = ("0700", "0730", "1730", "1800")
MORNING_SLOTS = ("0700", "0730")
EVENING_SLOTS = ("1730", "1800")

CSV_COLUMNS = (
    "timestamp_ict",
    "apartment_id",
    "slot",
    "direction",
    "duration_min",
    "duration_in_traffic_min",
    "duration_motorcycle_min",
    "distance_km",
    "status",
)
