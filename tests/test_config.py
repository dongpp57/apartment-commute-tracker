from scripts.lib import config


def test_destination_coords_are_hanoi():
    assert 21.0 < config.DESTINATION_LAT < 21.1
    assert 105.7 < config.DESTINATION_LNG < 105.9


def test_moto_factor_default():
    assert 0.80 <= config.MOTO_FACTOR <= 0.95


def test_slots_defined():
    assert config.SLOTS == ("0700", "0730")
