import logging
from tankstellen_alert.db import (
    upsert_station,
    add_price_history,
    get_last_price,
    station_update_needed,
    build_alert_station,
)
from tankstellen_alert.api import get_station_info, get_prices
from tankstellen_alert.config import STATION_IDS, THRESHOLD, GAS_TYPE

log = logging.getLogger(__name__)


def update_stations(station_ids):
    log.info("Checking {0} station(s) for updates", len(station_ids))
    for sid in station_ids:
        if station_update_needed(sid):
            data = get_station_info(sid).get("station", {})
            if not data:
                log.warning("No data returned for station {0}, skipping", sid)
                continue
            upsert_station(sid, data)
    log.info("Station update check complete")


def price_check(threshold=THRESHOLD, gas_type=GAS_TYPE, station_ids=None):
    if station_ids is None:
        station_ids = STATION_IDS
    if not station_ids:
        log.error("STATION_IDS is empty")
        raise ValueError("STATION_IDS is empty. Please check your .env file")
    log.info("Starting price check for {0} station(s)", len(station_ids))
    update_stations(station_ids)
    prices = get_prices(station_ids).get("prices", {})
    new_prices = add_price_history(station_ids, prices)
    if not new_prices:
        log.warning("No prices returned")
        return None
    return check_alerts(new_prices, gas_type, threshold)


def check_alerts(new_prices, gas_type, threshold):
    log.info("Checking prices against threshold {0}", threshold)
    alert_stations = []
    for new_price in new_prices:
        price = getattr(new_price, gas_type)
        if not price:
            log.debug("Station {0} has no price (closed?), skipping", new_price.station_id)
            continue
        if price >= threshold:
            log.debug("Station {0} above threshold, skipping", new_price.station_id)
            continue
        last_price = get_last_price(new_price.station_id, gas_type)
        if last_price is not None and last_price < threshold:
            log.debug("Station {0} already below threshold, skipping", new_price.station_id)
            continue
        alert = build_alert_station(new_price, gas_type, threshold)
        if alert:
            log.info("Alert triggered for {0}: {1} {2}€/l", alert.name, gas_type, price)
            alert_stations.append(alert)
    log.info("{0} alert(s) triggered", len(alert_stations))
    return alert_stations
