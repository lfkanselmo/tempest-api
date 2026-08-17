import pytest
from src.domain.value_objects import Coordinates


def test_creates_valid_coordinates() -> None:
    coordinates = Coordinates(latitude=4.7110, longitude=-74.0721)

    assert coordinates.latitude == 4.7110
    assert coordinates.longitude == -74.0721


@pytest.mark.parametrize("latitude", [90.1, -90.1])
def test_rejects_latitude_out_of_range(latitude: float) -> None:
    with pytest.raises(ValueError, match="Latitud fuera de rango"):
        Coordinates(latitude=latitude, longitude=0)


@pytest.mark.parametrize("longitude", [180.1, -180.1])
def test_rejects_longitude_out_of_range(longitude: float) -> None:
    with pytest.raises(ValueError, match="Longitud fuera de rango"):
        Coordinates(latitude=0, longitude=longitude)
