# TankstellenAlert 🚨⛽

A basic Python script that monitors fuel prices at selected German gas stations and sends a Discord notification when prices drop below a defined threshold.

> **Note:** This project uses the [Tankerkönig API](https://creativecommons.tankerkoenig.de/), which provides real-time fuel price data for Germany only.

---

## Features

- Monitors up to 10 gas stations simultaneously
- Stores price history in a local SQLite database
- Automatically refreshes station metadata weekly
- Sends Discord webhook notifications when prices drop below your threshold

---

## Requirements

- Tested for Python 3.12+
- A [Tankerkönig API key](https://creativecommons.tankerkoenig.de/)
- A Discord webhook URL

---

## Setup

### 1. Clone the repository
```bash
git clone https://github.com/anwemo/TankstellenAlert.git
cd TankstellenAlert
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the root directory:
```
API_KEY=your-tankerkoenig-api-key
DISCORD_WEBHOOK=your-discord-webhook-url
STATION_IDS= # keep empty for now
LAT=your-latitude
LNG=your-longitude
```

### 4. Find your station IDs

Run the setup script to find gas stations near your location using the LAT and LNG variables you specified in the .env file:
```bash
python setup_stations.py
```

Copy the IDs of the stations you want to monitor and add them to `STATION_IDS` in your `.env` file. Should look like "STATION_IDS=id1,id2,id3"

### 5. Configure threshold and fuel type

In `main.py`, adjust these constants to your preference:
```python
GAS_TYPE = "e10"   # Options: "e5", "e10", "diesel"
THRESHOLD = 1.80   # Alert when price drops below this float value in €
```

### 6. Run the script
```bash
python main.py
```

## License

MIT
