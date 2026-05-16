# TankstellenAlert 🚨⛽

A Python package that monitors fuel prices at selected German gas stations and sends a Discord notification when prices drop below a defined threshold.

> **Note:** This project uses the [Tankerkönig API](https://creativecommons.tankerkoenig.de/), which provides real-time fuel price data for Germany only.

---

## Features

- Monitors up to 10 gas stations simultaneously
- Stores price history in a local SQLite database
- Automatically refreshes station metadata daily
- Sends Discord webhook notifications when prices drop below your threshold
- Smart alert logic — alerts only when:
  - Price drops by at least 2 cents, or
  - Price has changed and at least 2 hours have passed since the last alert
- Built-in scheduler via APScheduler — no cron needed
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
│   ├── config.py        # Environment variables, logging setup, DB engine
│   ├── models.py        # SQLAlchemy models and AlertStation dataclass
│   ├── db.py            # Database operations
│   ├── api.py           # Tankerkönig API calls
│   ├── alert.py         # Price check and alert logic
│   ├── maintenance.py   # Station metadata maintenance
│   ├── notifier.py      # Discord webhook
│   └── scheduler.py     # APScheduler setup and job definitions
├── main.py              # Entry point
├── setup_stations.py    # Helper to find station IDs
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

# Used by setup_stations.py only
LAT=your-latitude
LNG=your-longitude

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

The scheduler runs automatically at :14, :29, :44, and :59 every hour. Station metadata is refreshed daily at 3:00 AM.

---

## License

MIT