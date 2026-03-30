from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey, String, Float, Integer, Boolean, Numeric, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from decimal import Decimal


class Base(DeclarativeBase):
    pass


class Station(Base):
    __tablename__ = "station"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    brand: Mapped[str] = mapped_column(String(50))
    street: Mapped[str] = mapped_column(String(100))
    house_number: Mapped[str] = mapped_column(String(10))
    post_code: Mapped[int] = mapped_column(Integer)
    city: Mapped[str] = mapped_column(String(100))
    lat: Mapped[float] = mapped_column(Float)
    lng: Mapped[float] = mapped_column(Float)
    price_history: Mapped[List["PriceHistory"]] = relationship(back_populates="station")
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}



class PriceHistory(Base):
    __tablename__ = "price_history"
    id: Mapped[int] = mapped_column(primary_key=True)
    e5: Mapped[Decimal] = mapped_column(Numeric(precision=5, scale=3))
    e10: Mapped[Decimal] = mapped_column(Numeric(precision=5, scale=3))
    diesel: Mapped[Decimal] = mapped_column(Numeric(precision=5, scale=3))
    is_open: Mapped[bool] = mapped_column(Boolean)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    station_id: Mapped[str] = mapped_column(String(36), ForeignKey("station.id"))
    station: Mapped["Station"] = relationship(back_populates="price_history")
    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

