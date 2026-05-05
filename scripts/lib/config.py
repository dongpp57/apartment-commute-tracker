"""Single source of truth for tracker constants."""

DESTINATION_LAT = 21.0263
DESTINATION_LNG = 105.8094
DESTINATION_NAME = "Vincom Nguyễn Chí Thanh"

MOTO_FACTOR = 0.88
# OpenRouteService returns car duration without real-time traffic.
# Calibrated against Google Maps peak-hour motorbike on 2026-05-05:
#   HD Mon City: ORS raw 10.16 min, Google motorbike 17 min → real factor ≈ 1.67
# motorbike_peak ≈ ors_duration × PEAK_HOUR_TRAFFIC_FACTOR × MOTO_FACTOR
# 1.90 × 0.88 = 1.67
PEAK_HOUR_TRAFFIC_FACTOR = 1.90

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
