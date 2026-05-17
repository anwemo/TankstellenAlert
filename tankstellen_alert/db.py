from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from tankstellen_alert.config import engine
from tankstellen_alert.models import Base, Station, PriceHistory
import logging

log = logging.getLogger(__name__)

Base.metadata.create_all(engine)


def upsert_station(station_id, data):
    log.debug("Upserting station %s", station_id)
    with Session(engine) as session:
        station = session.get(Station, station_id)
        is_new = not station
        if is_new:
            station = Station(id=station_id)
            session.add(station)
        station.name = data.get("name") or station.name
        station.brand = data.get("brand") or station.brand
        station.street = data.get("street") or station.street
        station.house_number = data.get("houseNumber") or station.house_number
        station.post_code = (
            str(data.get("postCode")).zfill(5)
            if data.get("postCode")
            else station.post_code
        )
        station.city = data.get("place") or station.city
        station.lat = data.get("lat") or station.lat
        station.lng = data.get("lng") or station.lng
        station.last_updated = datetime.now()
        session.commit()
        if is_new:
            log.info("Added new station: %s", station)
        else:
            log.info("Updated station: %s", station)


def add_price_history(station_ids: list, all_stations_prices):
    new_prices = []
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
            log.debug("Added new PriceHistory: %r", new_price)
            session.add(new_price)
            new_prices.append(new_price)
        session.commit()
    return new_prices


def get_last_price(station_id: str, gas_type: str) -> Optional[Decimal]:
    log.debug("Searching previous %s price for station %s", gas_type, station_id)
    with Session(engine) as session:
        entry = (
            session.query(PriceHistory)
            .filter(PriceHistory.station_id == station_id)
            .order_by(PriceHistory.timestamp.desc())
            .offset(1)
            .first()
        )
        if entry is None:
            log.debug("No previous %s price in db", gas_type)
            return None
        log.debug("Returning previous %s price from db", gas_type)
        return getattr(entry, gas_type)


def station_update_needed(station_id):
    log.debug("Checking if station %s needs update", station_id)
    with Session(engine) as session:
        station = session.get(Station, station_id)
        if (
            not station
            or not station.last_updated
            or datetime.today() - station.last_updated > timedelta(days=7)
        ):
            log.info("Station %s needs update", station_id)
            return True
        log.debug("Needs update: False")
        return False


# noinspection PyTypeChecker
def get_station(station_id: str) -> Optional[Station]:
    log.debug("Fetching station %s from db", station_id)
    with Session(engine) as session:
        station = session.get(Station, station_id)
        if station:
            session.expunge(station)
        return station


def update_last_alert_info(station_id, price):
    log.debug(
        "Updating last_alert_time and last_alert_price for station %s: %s€/l",
        station_id,
        price,
    )
    with Session(engine) as session:
        station = session.get(Station, station_id)
        if not station:
            log.warning(
                "Station %s not found in db, skipping last_alert update", station_id
            )
            return
        station.last_alert_price = price
        station.last_alert_time = datetime.now()
        session.commit()
