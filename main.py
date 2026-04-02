import os
import time

from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta
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

load_dotenv()
API_KEY = os.environ.get("API_KEY")
URL = "https://creativecommons.tankerkoenig.de/json"
DISCORD_URL = os.environ.get("DISCORD_WEBHOOK")
STATION_IDS = os.environ.get("STATION_IDS", "").split(",")
GAS_TYPE = "e10"
THRESHOLD = 2.0


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
        return (
            f"PriceHistory(id={self.id!r}, station_id={self.station_id!r}, is_open={self.is_open!r},"
            f"e5={self.e5!r}, e10={self.e10!r}, diesel={self.diesel!r}, timestamp={self.timestamp!r})"
        )


Base.metadata.create_all(engine)


def get_station_info(station_id):
    r = requests.get(URL + "/detail.php", params={"id": station_id, "apikey": API_KEY})
    r.raise_for_status()
    return r.json()


def get_prices(station_ids: list):
    r = requests.get(
        URL + "/prices.php", params={"ids": ",".join(station_ids), "apikey": API_KEY}
    )
    r.raise_for_status()
    return r.json()


def upsert_station(station_id):
    if not station_id:
        return
    data = get_station_info(station_id).get("station", {})
    if not data:
        return
    station_obj = Station(
        id=station_id,
        name=data.get("name"),
        brand=data.get("brand"),
        street=data.get("street"),
        house_number=data.get("houseNumber"),
        post_code=str(data.get("postCode")).zfill(5),
        city=data.get("place"),
        lat=data.get("lat"),
        lng=data.get("lng"),
        last_updated=datetime.today(),
    )
    with Session(engine) as session:
        session.merge(station_obj)
        session.commit()


def add_price_history(station_ids: list):
    if not station_ids:
        return
    new_prices = []
    all_stations_prices = get_prices(station_ids).get("prices", {})
    with Session(engine, expire_on_commit=False) as session:
        for station_id, prices in all_stations_prices.items():
            new_price = PriceHistory(
                e5=prices.get("e5"),
                e10=prices.get("e10"),
                diesel=prices.get("diesel"),
                is_open=prices.get("status") == "open",
                timestamp=datetime.today(),
                station_id=station_id,
            )
            session.add(new_price)
            new_prices.append(new_price)
        session.commit()
    return new_prices


def check_and_update_station(station_id):
    with Session(engine) as session:
        station = session.get(Station, station_id)
        if not station or not station.last_updated or datetime.today() - station.last_updated > timedelta(days=7):
            upsert_station(station_id)


def price_check(threshold=THRESHOLD, gas_type=GAS_TYPE, station_ids=None):
    if station_ids is None:
        station_ids = STATION_IDS
    if not station_ids:
        return "Error! No station ids defined."
    for station_id in station_ids:
        check_and_update_station(station_id)
    new_prices = add_price_history(station_ids)
    if not new_prices:
        return None
    alert_stations = []
    with Session(engine) as session:
        for new_price in new_prices:
            price = getattr(new_price, gas_type)
            if price and price < threshold:
                station = session.get(Station, new_price.station_id)
                alert_stations.append(
                    {
                        "gas_type": gas_type,
                        "price": price,
                        "threshold": threshold,
                        "name": station.name,
                        "brand": station.brand,
                        "street": f"{station.street} {station.house_number}",
                    }
                )
    return alert_stations


def generate_alert_message(alert_stations: list):
    message = (f"@everyone\n"
               f"Preis-Alarm:\n"
               f"Das Skript wurde für folgende Tankstellen ausgelöst:\n")
    for station in alert_stations:
        message = message + (f" - {station["gas_type"]} {station["price"]}€/l:"
                             f"{station["name"]} - {station["brand"]} - {station["street"]}\n")
    return message


def main():
    alert_stations = price_check()
    if alert_stations:
        message = generate_alert_message(alert_stations)
        requests.post(DISCORD_URL, json={"content": message})


if __name__ == "__main__":
    main()