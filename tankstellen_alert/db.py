from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from tankstellen_alert.config import engine
from tankstellen_alert.models import Base, Station, PriceHistory, AlertStation
import logging

log = logging.getLogger(__name__)

Base.metadata.create_all(engine)


def upsert_station(station_id, data):
    log.debug("Upserting station {0}", station_id)
    station_label = f"{data.get('name')}, {data.get('street')} {data.get('houseNumber')}"
    with Session(engine) as session:
        station = session.get(Station, station_id)
        if not station:
            station = Station(id=station_id)
            session.add(station)
            log.info("Station not found in db, adding: {0}", station_label)
        else:
            log.info("Station found in db, updating: {0}", station_label)
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
            log.debug("Added new PriceHistory: {0}", new_price)
            session.add(new_price)
            new_prices.append(new_price)
        session.commit()
    return new_prices


def get_last_price(station_id: str, gas_type: str) -> Optional[Decimal]:
    log.debug("Searching previous {0} price for station {1}", gas_type, station_id)
    with Session(engine) as session:
        entry = (
            session.query(PriceHistory)
            .filter(PriceHistory.station_id == station_id)
            .order_by(PriceHistory.timestamp.desc())
            .offset(1)
            .first()
        )
        if entry is None:
            log.debug("No previous {0} price in db", gas_type)
            return None
        log.debug("Returning previous {0} price from db", gas_type)
        return getattr(entry, gas_type)


def station_update_needed(station_id):
    log.debug("Checking if station {0} needs update", station_id)
    with Session(engine) as session:
        station = session.get(Station, station_id)
        if (
            not station
            or not station.last_updated
            or datetime.today() - station.last_updated > timedelta(days=7)
        ):
            log.info("Station {0} needs update", station_id)
            return True
        log.debug("Needs update: False")
        return False


# noinspection PyTypeChecker
def build_alert_station(new_price: PriceHistory, gas_type: str, threshold: Decimal):
    log.debug("Building AlertStation for station {0}", new_price.station_id)
    with Session(engine) as session:
        station = session.get(Station, new_price.station_id)
        if not station:
            log.warning("Station {0} not found in db, skipping alert", new_price.station_id)
            return None
        return AlertStation(
            gas_type=gas_type,
            station_id=station.id,
            price=getattr(new_price, gas_type),
            threshold=threshold,
            name=station.name,
            brand=station.brand,
            street=f"{station.street} {station.house_number}",
        )
