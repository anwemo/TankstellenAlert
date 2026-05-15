import logging
from tankstellen_alert.alert import price_check
from tankstellen_alert.notifier import send_alert

log = logging.getLogger(__name__)


def main():
    log.info("Starting TankstellenAlert")
    try:
        alert_stations = price_check()
    except ValueError as e:
        log.error("Configuration error: {0}", e)
        return
    except Exception as e:
        log.error("Unexpected error during price check: {0}", e, exc_info=True)
        return

    if not alert_stations:
        log.info("No alerts triggered, exiting")
        return

    try:
        send_alert(alert_stations)
    except Exception as e:
        log.error("Failed to send alert: {0}", e, exc_info=True)

    log.info("TankstellenAlert finished")


if __name__ == "__main__":
    main()
