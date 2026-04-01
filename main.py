import os
from dotenv import load_dotenv
import requests
from datetime import datetime
from typing import List
from sqlalchemy import (
    ForeignKey,
    String,
    Float,
    Integer,
    Boolean,
    Numeric,
    DateTime,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from decimal import Decimal

# TODO 3: feat: add setup_stations script for initial station discovery
# TODO 4: feat: implement station upsert logic
# TODO 5: feat: implement price history upsert logic
# TODO 6: feat: add notification trigger logic
# TODO 7: feat: add webhook dispatch logic

load_dotenv()
API_KEY = os.environ.get("API_KEY")
URL = "https://creativecommons.tankerkoenig.de/json"


engine = create_engine("sqlite:///tankstellen-alert.db")


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
    last_updated: Mapped[datetime] = mapped_column(DateTime)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f"Station(id={self.id!r}, name={self.name!r}, brand={self.brand!r}, street={self.street!r})"


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

    def __repr__(self):
        return f"PriceHistory(id={self.id!r}, station_id={self.station_id!r}, is_open={self.is_open!r}, e5={self.e5!r}, e10={self.e10!r}, diesel={self.diesel!r}, timestamp={self.timestamp!r})"


Base.metadata.create_all(engine)


def get_station_info(station_id):
    r = requests.get(URL+"/detail.php", params={"id": station_id, "apikey": API_KEY})
    r.raise_for_status()
    return r.json()


def get_prices(station_ids: list):
    r = requests.get(URL+"/prices.php", params={"ids": ",".join(station_ids), "apikey": API_KEY})
    r.raise_for_status()
    return r.json()
