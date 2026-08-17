from pydantic import BaseModel


class NominatimAddress(BaseModel):
    city: str | None = None
    town: str | None = None
    village: str | None = None
    municipality: str | None = None
    county: str | None = None
    country: str | None = None


class NominatimReverseResponse(BaseModel):
    lat: float
    lon: float
    display_name: str
    address: NominatimAddress
