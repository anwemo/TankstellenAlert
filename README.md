# TankstellenAlert 🚨⛽

A Python package that monitors fuel prices at selected German gas stations and sends a Discord notification when prices drop below a defined threshold. Alerts are only sent when a price newly drops below the threshold — no repeated notifications for prices that are already low.

> **Note:** This project uses the [Tankerkönig API](https://creativecommons.tankerkoenig.de/), which provides real-time fuel price data for Germany only.

---

## Features

- Monitors up to 10 gas stations simultaneously
- Stores price history in a local SQLite database
- Automatically refreshes station metadata weekly
- Sends Discord webhook notifications when prices drop below your threshold
- Alerts only on new threshold crossings — no spam
- Configurable fuel type and threshold via environment variables
- Daily log rotation with 30-day retention

---

## Requirements

- Python 3.12+
- A [Tankerkönig API key](https://creativecommons.tankerkoenig.de/)
- A Discord webhook URL

---

## Project Structure

```
TankstellenAlert/
├── tankstellen_alert/
│   ├── __init__.py
│   ├── config.py       # Environment variables, logging setup, DB engine
│   ├── models.py       # SQLAlchemy models and AlertStation dataclass
│   ├── db.py           # Database operations
│   ├── api.py          # Tankerkönig API calls
│   ├── alert.py        # Price check and alert logic
│   └── notifier.py     # Discord webhook
├── main.py             # Entry point
├── setup_stations.py   # Helper to find station IDs
└── requirements.txt
```

---

## Setup

### 1. Clone the repository

```
git clone https://github.com/anwemo/TankstellenAlert.git
cd TankstellenAlert
```

### 2. Install dependencies

Create a virtual environment (recommended):

```
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

Then install dependencies:

```
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the root directory:

```
# Required
API_KEY=your-tankerkoenig-api-key
DISCORD_WEBHOOK=your-discord-webhook-url
STATION_IDS=            # comma-separated station IDs, e.g. id1,id2,id3
LAT=your-latitude       # used by setup_stations.py
LNG=your-longitude      # used by setup_stations.py

# Optional (defaults shown)
GAS_TYPE=e10            # Options: e5, e10, diesel
THRESHOLD=1.80          # Alert when price drops below this value in €
DB_PATH=                # Defaults to data/tankstellen-alert.db
LOG_PATH=               # Defaults to data/tankstellen-alert.log
DEBUG=false             # Set to true for verbose logging
```

### 4. Find your station IDs

Run the setup script to find gas stations near your location:

```
python setup_stations.py
```

Copy the IDs of the stations you want to monitor and add them to `STATION_IDS` in your `.env` file.

### 5. Run the script

```
python main.py
```

### 6. Automate with cron

To run the script every 15 minutes (minimum interval per Tankerkönig ToS):

```
*/15 * * * * /path/to/.venv/bin/python /path/to/main.py
```

---

## License

MIT
