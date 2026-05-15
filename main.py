import logging
from tankstellen_alert.alert import price_check
from tankstellen_alert.notifier import send_alert

log = logging.getLogger(__name__)


def main():
    log.info("Starting TankstellenAlert")
    try:
        alert_stations = price_check()
    except ValueError as e:
        log.error("Configuration error: %s", e)
        return
    except Exception as e:
        log.error("Unexpected error during price check: %s", e, exc_info=True)
        return

    if not alert_stations:
        log.info("No alerts triggered, exiting")
        return

    try:
        send_alert(alert_stations)
    except Exception as e:
        log.error("Failed to send alert: %s", e, exc_info=True)

    log.info("TankstellenAlert finished")


if __name__ == "__main__":
    main()
