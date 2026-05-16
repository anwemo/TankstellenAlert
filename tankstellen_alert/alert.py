import logging
from decimal import Decimal
from datetime import datetime, timedelta

from tankstellen_alert.api import get_station_info, get_prices
from tankstellen_alert.config import STATION_IDS, THRESHOLD, GAS_TYPE
from tankstellen_alert.db import (
    upsert_station,
    add_price_history,
    station_update_needed,
    get_station, update_last_alert_info,
)
from tankstellen_alert.models import AlertStation, Station

log = logging.getLogger(__name__)


def update_stations(station_ids):
    log.info("Checking %s station(s) for updates", len(station_ids))
    for sid in station_ids:
        if station_update_needed(sid):
            data = get_station_info(sid).get("station", {})
            if not data:
                log.warning("No data returned for station %s, skipping", sid)
                continue
            upsert_station(sid, data)
    log.info("Station update check complete")


def price_check(threshold=THRESHOLD, gas_type=GAS_TYPE, station_ids=None):
    if station_ids is None:
        station_ids = STATION_IDS
    log.info("Starting price check for %s station(s)", len(station_ids))
    prices = get_prices(station_ids).get("prices", {})
    new_prices = add_price_history(station_ids, prices)
    if not new_prices:
        log.warning("No prices returned")
        return None
    alert_stations = []
    for new_price in new_prices:
        alert = _process_station(new_price, gas_type, threshold)
        if alert:
            alert_stations.append(alert)
    if alert_stations:
        log.info("%s alert(s) triggered", len(alert_stations))
        return alert_stations
    return None


# noinspection PyTypeChecker
def _build_alert_station(new_price, gas_type: str, threshold: Decimal, station: Station) -> AlertStation:
    log.debug("Building AlertStation for station %s", station.id)
    return AlertStation(
        gas_type=gas_type,
        station_id=station.id,
        price=getattr(new_price, gas_type),
        threshold=threshold,
        name=station.name,
        brand=station.brand,
        street=f"{station.street} {station.house_number}",
    )


def _should_alert(price: Decimal, station: Station, threshold: Decimal) -> bool:
    if price >= threshold:
        log.debug("Station %s above threshold, skipping", station.id)
        return False
    if station.last_alert_price is None or station.last_alert_time is None:
        return True
    if station.last_alert_price - price >= Decimal("0.02"):
        return True
    if price != station.last_alert_price and datetime.now() - station.last_alert_time >= timedelta(hours=2):
        return True
    return False


def _process_station(new_price, gas_type, threshold) -> AlertStation | None:
    price = getattr(new_price, gas_type)
    if not price:
        log.debug(
            "Station %s has no price (closed?), skipping", new_price.station_id
        )
        return None
    price = Decimal(str(price))
    station = get_station(new_price.station_id)
    if not station:
        log.warning("Station %s not found in db, skipping", new_price.station_id)
        return None
    if not _should_alert(price, station, threshold):
        log.debug("Station %s cooldown active or above threshold, skipping", new_price.station_id)
        return None
    update_last_alert_info(station.id, price)
    log.info("Alert triggered for %s: %s %s€/l", station.name, gas_type, price)
    return _build_alert_station(new_price, gas_type, threshold, station)
