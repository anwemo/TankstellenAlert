from tankstellen_alert.alert import price_check
from tankstellen_alert.notifier import send_alert


def main():
    alert_stations = price_check()
    if alert_stations:
        send_alert(alert_stations)


if __name__ == "__main__":
    main()
