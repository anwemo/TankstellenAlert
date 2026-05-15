import requests
import logging
from tankstellen_alert.config import URL, API_KEY

log = logging.getLogger(__name__)


def get_station_info(station_id):
    log.debug("Fetching station info for {0}", station_id)
    r = requests.get(
        URL + "/detail.php", params={"id": station_id, "apikey": API_KEY}, timeout=10
    )
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        log.error("API request failed for station {0}: {1}", station_id, e)
        raise
    log.debug("Successfully fetched station info for {0}", station_id)
    return r.json()


def get_prices(station_ids: list):
    log.debug("Fetching prices for {0}", ", ".join(station_ids))
    r = requests.get(
        URL + "/prices.php",
        params={"ids": ",".join(station_ids), "apikey": API_KEY},
        timeout=10,
    )
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        log.error("API request failed for stations {0}: {1}", ", ".join(station_ids), e)
        raise
    log.debug("Successfully fetched prices for {0}", ", ".join(station_ids))
    return r.json()
