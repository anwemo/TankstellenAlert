import logging
from decimal import Decimal
from datetime import datetime, timedelta

from tankstellen_alert.api import get_prices
from tankstellen_alert.config import STATION_IDS, THRESHOLD, GAS_TYPE
from tankstellen_alert.db import (
    add_price_history,
    get_station_objects,
    update_last_alert_info,
)
from tankstellen_alert.models import AlertStation, Station

log = logging.getLogger(__name__)


def price_check(threshold=THRESHOLD, gas_type=GAS_TYPE, station_ids=None):
    if station_ids is None:
        station_ids = STATION_IDS
    stations = get_station_objects(station_ids)
    log.info("Starting price check for %s station(s)", len(stations))
    prices = get_prices(list(stations.keys())).get("prices", {})
    new_prices = add_price_history(prices)
    if not new_prices:
        log.warning("No prices returned")
        return None
    alert_stations = []
    for new_price in new_prices:
        station = stations.get(new_price.station_id)
        if not station:
            log.warning("Station %s not found in stations dict, skipping", new_price.station_id)
            continue
        alert = _process_station(new_price, gas_type, threshold, station)
        if alert:
            alert_stations.append(alert)
    if alert_stations:
        log.info("%s alert(s) triggered", len(alert_stations))
        return alert_stations
    return None


# noinspection PyTypeChecker
def _build_alert_station(
    new_price, gas_type: str, threshold: Decimal, station: Station
) -> AlertStation:
    log.debug("Building AlertStation for station %r", station)
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
        log.info(
            "%s: %s€/l, skipping", station, price
        )
        return False
    if station.last_alert_price is None or station.last_alert_time is None:
        return True
    if station.last_alert_price - price >= Decimal("0.02"):
        return True
    if (
        price != station.last_alert_price
        and datetime.now() - station.last_alert_time >= timedelta(hours=2)
    ):
        return True
    return False


def _process_station(new_price, gas_type, threshold, station) -> AlertStation | None:
    price = getattr(new_price, gas_type)
    if not price:
        log.debug("%s has no price (closed?), skipping", station)
        return None
    price = Decimal(str(price))
    if not _should_alert(price, station, threshold):
        log.debug(
            "Station %r cooldown active or above threshold, skipping",
            station,
        )
        return None
    update_last_alert_info(station.id, price)
    log.info("Alert triggered for %s: %s %s€/l", station, gas_type, price)
    return _build_alert_station(new_price, gas_type, threshold, station)
