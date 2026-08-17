from pydantic import BaseModel


class OpenMeteoGeocodingResult(BaseModel):
    name: str
    country: str
    latitude: float
    longitude: float


class OpenMeteoGeocodingResponse(BaseModel):
    results: list[OpenMeteoGeocodingResult] = []
