import requests
from tankstellen_alert.config import URL, API_KEY


def get_station_info(station_id):
    r = requests.get(
        URL + "/detail.php", params={"id": station_id, "apikey": API_KEY}, timeout=10
    )
    r.raise_for_status()
    return r.json()


def get_prices(station_ids: list):
    r = requests.get(
        URL + "/prices.php",
        params={"ids": ",".join(station_ids), "apikey": API_KEY},
        timeout=10,
    )
    r.raise_for_status()
    return r.json()
