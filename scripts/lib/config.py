"""Single source of truth for tracker constants."""

DESTINATION_LAT = 21.0263
DESTINATION_LNG = 105.8094
DESTINATION_NAME = "Vincom Nguyễn Chí Thanh"

MOTO_FACTOR = 0.67
# Mapbox driving-traffic profile already includes real-time traffic.
# Calibrated against Google Maps motorbike directions on 2026-05-05:
#   HD Mon City → NCT: Google 16 min, Mapbox raw 24 min → real factor 16/24 ≈ 0.67
# Hanoi motorbikes navigate aggressively (lane filtering, sidewalk hopping) —
# claw back ~33% vs cars during traffic.

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
