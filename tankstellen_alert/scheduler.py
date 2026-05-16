import logging
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from tankstellen_alert.alert import price_check
from tankstellen_alert.maintenance import station_maintenance
from tankstellen_alert.notifier import send_alert, send_error_alert

log = logging.getLogger(__name__)

SCHEDULED_MINUTES = [14, 29, 44, 59]


def job():
    log.info("Starting TankstellenAlert")
    try:
        alert_stations = price_check()
    except Exception as e:
        log.error("Unexpected error during price check: %s", e, exc_info=True)
        send_error_alert(e)
        return

    if not alert_stations:
        log.info("No alerts triggered, exiting")
        return

    try:
        send_alert(alert_stations)
    except Exception as e:
        log.error("Failed to send alert: %s", e, exc_info=True)

    log.info("TankstellenAlert finished")


def _minutes_until_next_run() -> int:
    now = datetime.now()
    current_minute = now.minute
    future = [m for m in SCHEDULED_MINUTES if m > current_minute]
    if future:
        return min(future) - current_minute
    # Nach 59: nächster Lauf ist :14 der nächsten Stunde
    return (60 - current_minute) + SCHEDULED_MINUTES[0]


def start():
    if _minutes_until_next_run() > 1:
        log.info("Running initial check on startup")
        job()

    scheduler = BlockingScheduler()
    scheduler.add_job(job, "cron", minute=",".join(map(str, SCHEDULED_MINUTES)))
    scheduler.add_job(station_maintenance, "cron", hour="3")
    log.info(
        "Scheduler started, running at :%s", ", :".join(map(str, SCHEDULED_MINUTES))
    )
    scheduler.start()
