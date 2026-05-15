from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from tankstellen_alert.config import engine
from tankstellen_alert.models import Base, Station, PriceHistory, AlertStation

Base.metadata.create_all(engine)


def upsert_station(station_id, data):
    if not station_id:
        return
    if not data:
        return
    station_obj = Station(
        id=station_id,
        name=data.get("name") or "",
        brand=data.get("brand") or "",
        street=data.get("street") or "",
        house_number=data.get("houseNumber") or "",
        post_code=str(data.get("postCode") or "").zfill(5),
        city=data.get("place") or "",
        lat=data.get("lat"),
        lng=data.get("lng"),
        last_updated=datetime.now(),
    )
    with Session(engine) as session:
        session.merge(station_obj)
        session.commit()


def add_price_history(station_ids: list, all_stations_prices):
    if not station_ids:
        return
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
            session.add(new_price)
            new_prices.append(new_price)
        session.commit()
    return new_prices


def get_last_price(station_id: str, gas_type: str) -> Optional[Decimal]:
    with Session(engine) as session:
        entry = (
            session.query(PriceHistory)
            .filter(PriceHistory.station_id == station_id)
            .order_by(PriceHistory.timestamp.desc())
            .offset(1)
            .first()
        )
        if entry is None:
            return None
        return getattr(entry, gas_type)


def station_update_needed(station_id):
    with Session(engine) as session:
        station = session.get(Station, station_id)
        if (
            not station
            or not station.last_updated
            or datetime.today() - station.last_updated > timedelta(days=7)
        ):
            return True
        return False


def build_alert_station(new_price: PriceHistory, gas_type: str, threshold: Decimal):
    with Session(engine) as session:
        station = session.get(Station, new_price.station_id)
        if not station:
            return None
        return AlertStation(
            station_id=station.id,
            gas_type=gas_type,
            price=getattr(new_price, gas_type),
            threshold=threshold,
            name=station.name,
            brand=station.brand,
            street=f"{station.street} {station.house_number}",
        )
