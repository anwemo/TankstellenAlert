from tankstellen_alert.db import (
    upsert_station,
    add_price_history,
    get_last_price,
    station_update_needed,
    build_alert_station,
)
from tankstellen_alert.api import get_station_info, get_prices
from tankstellen_alert.config import STATION_IDS, THRESHOLD, GAS_TYPE


def update_stations(station_ids):
    for sid in station_ids:
        if station_update_needed(sid):
            data = get_station_info(sid).get("station", {})
            upsert_station(sid, data)


def price_check(threshold=THRESHOLD, gas_type=GAS_TYPE, station_ids=None):
    if station_ids is None:
        station_ids = STATION_IDS
    if not station_ids:
        raise ValueError("STATION_IDS is empty. Please check your .env file")
    update_stations(station_ids)
    prices = get_prices(station_ids).get("prices", {})
    new_prices = add_price_history(station_ids, prices)
    if not new_prices:
        return None
    return check_alerts(new_prices, gas_type, threshold)


def check_alerts(new_prices, gas_type, threshold):
    alert_stations = []
    for new_price in new_prices:
        price = getattr(new_price, gas_type)
        if not price or price >= threshold:
            continue
        last_price = get_last_price(new_price.station_id, gas_type)
        if last_price is not None and last_price < threshold:
            continue
        alert = build_alert_station(new_price, gas_type, threshold)
        if alert:
            alert_stations.append(alert)
    return alert_stations
