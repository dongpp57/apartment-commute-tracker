from scripts.lib import config


def test_destination_coords_are_hanoi():
    assert 21.0 < config.DESTINATION_LAT < 21.1
    assert 105.7 < config.DESTINATION_LNG < 105.9


def test_moto_factor_default():
    # MOTO_FACTOR = 1.0 means raw Mapbox driving-traffic logged as-is
    # (no motorbike correction). Range allows 0.5-1.0 for flexibility.
    assert 0.50 <= config.MOTO_FACTOR <= 1.0


def test_slots_defined():
    assert config.SLOTS == ("0700", "0730", "1730", "1800")
    assert config.MORNING_SLOTS == ("0700", "0730")
    assert config.EVENING_SLOTS == ("1730", "1800")


def test_csv_has_direction_column():
    assert "direction" in config.CSV_COLUMNS
