import requests
from tankstellen_alert.config import DISCORD_URL, DEBUG
from tankstellen_alert.models import AlertStation


def _generate_alert_message(alert_stations: list[AlertStation], debug):
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
    if not alert_stations:
        return
    message = _generate_alert_message(alert_stations, DEBUG)
    requests.post(DISCORD_URL, json={"content": message}, timeout=10)
