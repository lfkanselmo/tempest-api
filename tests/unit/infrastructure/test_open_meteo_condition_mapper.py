import pytest
from src.domain.value_objects import WeatherCondition
from src.infrastructure.providers.open_meteo_condition_mapper import map_wmo_code

KNOWN_WMO_CODES = [
    0,
    1,
    2,
    3,
    45,
    48,
    51,
    53,
    55,
    56,
    57,
    61,
    63,
    65,
    66,
    67,
    71,
    73,
    75,
    77,
    80,
    81,
    82,
    85,
    86,
    95,
    96,
    99,
]


@pytest.mark.parametrize("code", KNOWN_WMO_CODES)
def test_maps_every_known_wmo_code_to_a_condition(code: int) -> None:
    assert isinstance(map_wmo_code(code), WeatherCondition)


def test_rejects_unknown_wmo_code() -> None:
    with pytest.raises(ValueError, match="Codigo WMO desconocido"):
        map_wmo_code(-1)
