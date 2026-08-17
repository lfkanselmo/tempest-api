from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from src.domain.exceptions import FavoriteNotFoundException
from src.domain.models import Favorite, Location
from src.domain.value_objects import Coordinates
from src.infrastructure.persistence.orm_models import FavoriteORM


class SqliteFavoriteRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[Favorite]:
        rows = self._session.query(FavoriteORM).order_by(FavoriteORM.created_at).all()
        return [self._to_domain(row) for row in rows]

    def add(self, location: Location) -> Favorite:
        row = FavoriteORM(
            id=uuid4(),
            name=location.name,
            country=location.country,
            latitude=location.coordinates.latitude,
            longitude=location.coordinates.longitude,
            created_at=datetime.now(UTC),
        )
        self._session.add(row)
        self._session.commit()
        self._session.refresh(row)
        return self._to_domain(row)

    def remove(self, favorite_id: UUID) -> None:
        row = self._session.get(FavoriteORM, favorite_id)
        if row is None:
            raise FavoriteNotFoundException(str(favorite_id))
        self._session.delete(row)
        self._session.commit()

    @staticmethod
    def _to_domain(row: FavoriteORM) -> Favorite:
        return Favorite(
            id=row.id,
            location=Location(
                name=row.name,
                country=row.country,
                coordinates=Coordinates(latitude=row.latitude, longitude=row.longitude),
            ),
            created_at=row.created_at,
        )
