import logging
from decimal import Decimal

from tankstellen_alert.api import get_station_info, get_prices
from tankstellen_alert.config import STATION_IDS, THRESHOLD, GAS_TYPE
from tankstellen_alert.db import (
    upsert_station,
    add_price_history,
    get_last_price,
    station_update_needed,
    get_station,
)
from tankstellen_alert.models import AlertStation

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
    update_stations(station_ids)
    prices = get_prices(station_ids).get("prices", {})
    new_prices = add_price_history(station_ids, prices)
    if not new_prices:
        log.warning("No prices returned")
        return None
    return check_alerts(new_prices, gas_type, threshold)


# noinspection PyTypeChecker
def build_alert_station(new_price, gas_type: str, threshold: Decimal):
    log.debug("Building AlertStation for station %s", new_price.station_id)
    station = get_station(new_price.station_id)
    if not station:
        log.warning("Station %s not found in db, skipping alert", new_price.station_id)
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


def check_alerts(new_prices, gas_type, threshold):
    log.info("Checking prices against threshold %s", threshold)
    alert_stations = []
    for new_price in new_prices:
        price = getattr(new_price, gas_type)
        if not price:
            log.debug(
                "Station %s has no price (closed?), skipping", new_price.station_id
            )
            continue
        else:
            price = Decimal(str(price))
        if price >= threshold:
            log.debug("Station %s above threshold, skipping", new_price.station_id)
            continue
        last_price = get_last_price(new_price.station_id, gas_type)
        if last_price is not None and last_price == price:
            log.debug("Station %s price unchanged, skipping", new_price.station_id)
            continue
        alert = build_alert_station(new_price, gas_type, threshold)
        if alert:
            log.info("Alert triggered for %s: %s %s€/l", alert.name, gas_type, price)
            alert_stations.append(alert)
    log.info("%s alert(s) triggered", len(alert_stations))
    return alert_stations
