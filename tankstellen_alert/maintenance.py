import logging
from tankstellen_alert.api import get_station_info
from tankstellen_alert.db import station_update_needed, upsert_station
from tankstellen_alert.config import STATION_IDS

log = logging.getLogger(__name__)


def station_maintenance(station_ids=None):
    if station_ids is None:
        station_ids = STATION_IDS
    log.info("Checking %s station(s) for updates", len(station_ids))
    for sid in station_ids:
        if station_update_needed(sid):
            data = get_station_info(sid).get("station", {})
            if not data:
                log.warning("No data returned for station %s, skipping", sid)
                continue
            upsert_station(sid, data)
    log.info("Station maintenance complete")
