import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
import logging
from logging.handlers import TimedRotatingFileHandler

load_dotenv()
API_KEY = os.environ.get("API_KEY")
DB_PATH = os.environ.get(
    "DB_PATH", str(Path(__file__).parent.parent / "data" / "tankstellen-alert.db")
)
LOG_PATH = os.environ.get(
    "LOG_PATH", str(Path(__file__).parent.parent / "data" / "tankstellen-alert.log")
)
URL = "https://creativecommons.tankerkoenig.de/json"
DISCORD_URL = os.environ.get("DISCORD_WEBHOOK")
STATION_IDS = [s for s in os.environ.get("STATION_IDS", "").split(",") if s]
GAS_TYPE = os.environ.get("GAS_TYPE", "e10")
THRESHOLD = float(os.environ.get("THRESHOLD", "1.80"))
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
Path(LOG_PATH).parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG if DEBUG else logging.INFO,
    format="{asctime} [{levelname}] {name}.{funcName}: {message}",
    style="{",
    handlers=[
        TimedRotatingFileHandler(
            LOG_PATH,
            when="midnight",
            backupCount=30,
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)

engine = create_engine(f"sqlite:///{DB_PATH}")

log = logging.getLogger(__name__)
log.info("Config loaded. DB: {0}, GAS_TYPE: {1}, THRESHOLD: {2}, DEBUG: {3}", DB_PATH, GAS_TYPE, THRESHOLD, DEBUG)