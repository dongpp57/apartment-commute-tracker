"""Single source of truth for tracker constants."""

DESTINATION_LAT = 21.0263
DESTINATION_LNG = 105.8094
DESTINATION_NAME = "Vincom Nguyễn Chí Thanh"

MOTO_FACTOR = 1.0
# No motorbike correction applied. Calibration approach (per-cluster factor
# tuned to Google Maps motorbike) was non-stable: factor varied with
# time-of-day (off-peak ~0.5, peak ~1.0). Logging raw Mapbox driving-traffic
# duration directly is more honest — user can interpret "actual motorbike
# time = X% of this number" based on personal experience when visiting
# clusters in person.

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
