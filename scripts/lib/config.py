"""Single source of truth for tracker constants."""

DESTINATION_LAT = 21.0263
DESTINATION_LNG = 105.8094
DESTINATION_NAME = "Vincom Nguyễn Chí Thanh"

MOTO_FACTOR = 0.88

SLOTS = ("0700", "0730")

CSV_COLUMNS = (
    "timestamp_ict",
    "apartment_id",
    "slot",
    "duration_min",
    "duration_in_traffic_min",
    "duration_motorcycle_min",
    "distance_km",
    "status",
)
