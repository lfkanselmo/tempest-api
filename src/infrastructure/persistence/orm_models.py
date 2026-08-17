import uuid
from datetime import datetime

from sqlalchemy import Float, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class FavoriteORM(Base):
    __tablename__ = "favorites"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    country: Mapped[str] = mapped_column(String)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime]


class PreferencesORM(Base):
    __tablename__ = "preferences"

    id: Mapped[str] = mapped_column(primary_key=True)
    unit_system: Mapped[str] = mapped_column(String)
