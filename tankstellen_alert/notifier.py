import requests
import logging
from tankstellen_alert.config import DISCORD_URL, DEBUG
from tankstellen_alert.models import AlertStation

log = logging.getLogger(__name__)


def _generate_alert_message(alert_stations: list[AlertStation], debug):
    log.debug("Generating message for %s station(s)", len(alert_stations))
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


def _send_to_discord(message: str):
    r = requests.post(DISCORD_URL, json={"content": message}, timeout=10)
    r.raise_for_status()


def send_alert(alert_stations):
    log.debug("Preparing to send message for %s stations", len(alert_stations))
    message = _generate_alert_message(alert_stations, DEBUG)
    _send_to_discord(message)
    log.info("Alert sent successfully")


def send_error_alert(error: Exception):
    log.debug("Sending error alert to Discord")
    message = f"⚠️ TankstellenAlert Fehler:\n```{type(error).__name__}: {error}```"
    try:
        _send_to_discord(message)
        log.info("Error alert sent successfully")
    except requests.HTTPError as e:
        log.error("Failed to send error alert to Discord: %s", e)
