import requests
import logging
from tankstellen_alert.config import DISCORD_URL, DEBUG
from tankstellen_alert.models import AlertStation

log = logging.getLogger(__name__)


def _generate_alert_message(alert_stations: list[AlertStation], debug):
    log.debug("Generating message for {0} station(s)", len(alert_stations))
    message = (
        f"@everyone\n"
        f"Preis-Alarm:\n"
        f"Das Skript wurde für folgende Tankstelle(n) ausgelöst:\n"
    )
    for station in alert_stations:
        message = message + (
            f" - {station.gas_type} {station.price}€/l:"
            f"{station.name} - {station.brand} - {station.street}\n"
        )
    if debug:
        message = message + f"\nDEBUG\nThreshold: {alert_stations[0].threshold}\n"
        for station in alert_stations:
            message = message + f"{station.station_id}, "
    return message


def send_alert(alert_stations):
    if not DISCORD_URL:
        log.error("DISCORD_WEBHOOK is not set in .env")
        return
    log.debug("Preparing to send message for {0} stations", len(alert_stations))
    message = _generate_alert_message(alert_stations, DEBUG)
    try:
        r = requests.post(DISCORD_URL, json={"content": message}, timeout=10)
        r.raise_for_status()
        log.info("Alert sent successfully")
    except requests.HTTPError as e:
        log.error("Discord webhook failed: {0}", e)
        raise
