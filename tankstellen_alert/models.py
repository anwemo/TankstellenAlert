from typing import List, Optional
from sqlalchemy import ForeignKey, String, Float, Boolean, Numeric, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass


class Base(DeclarativeBase):
    pass


# noinspection PyTypeChecker
class Station(Base):
    __tablename__ = "station"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    brand: Mapped[str] = mapped_column(String(50))
    street: Mapped[str] = mapped_column(String(100))
    house_number: Mapped[str] = mapped_column(String(10))
    post_code: Mapped[str] = mapped_column(String(5))
    city: Mapped[str] = mapped_column(String(100))
    lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lng: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_history: Mapped[List["PriceHistory"]] = relationship(back_populates="station")
    last_updated: Mapped[datetime] = mapped_column(DateTime)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"Station(id={self.id!r}, name={self.name!r}, brand={self.brand!r}, street={self.street!r})"


# noinspection PyTypeChecker
class PriceHistory(Base):
    __tablename__ = "price_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    e5: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=3))
    e10: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=3))
    diesel: Mapped[Optional[Decimal]] = mapped_column(Numeric(precision=5, scale=3))
    is_open: Mapped[bool] = mapped_column(Boolean)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    station_id: Mapped[str] = mapped_column(String(36), ForeignKey("station.id"))
    station: Mapped["Station"] = relationship(back_populates="price_history")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return (
            f"PriceHistory(id={self.id!r}, station_id={self.station_id!r}, is_open={self.is_open!r},"
            f"e5={self.e5!r}, e10={self.e10!r}, diesel={self.diesel!r}, timestamp={self.timestamp!r})"
        )


@dataclass
class AlertStation:
    station_id: str
    gas_type: str
    price: Decimal
    threshold: Decimal
    name: str
    brand: str
    street: str
