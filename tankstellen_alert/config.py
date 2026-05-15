import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
import logging
from logging.handlers import TimedRotatingFileHandler

# --- RAW inputs ---
load_dotenv()
API_KEY = os.environ.get("API_KEY")
DISCORD_URL = os.environ.get("DISCORD_WEBHOOK")
STATION_IDS_RAW = os.environ.get("STATION_IDS", "")
GAS_TYPE_RAW = os.environ.get("GAS_TYPE")
THRESHOLD_RAW = os.environ.get("THRESHOLD")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
URL = "https://creativecommons.tankerkoenig.de/json"
DB_PATH = os.environ.get(
    "DB_PATH", str(Path(__file__).parent.parent / "data" / "tankstellen-alert.db")
)
LOG_PATH = os.environ.get(
    "LOG_PATH", str(Path(__file__).parent.parent / "data" / "tankstellen-alert.log")
)

_GAS_TYPE_DEFAULT = "e10"
_THRESHOLD_DEFAULT = 1.80

# --- Directories ---
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
Path(LOG_PATH).parent.mkdir(parents=True, exist_ok=True)

# --- Logging ---
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
log = logging.getLogger(__name__)

# --- Data processing and validation
engine = create_engine(f"sqlite:///{DB_PATH}")

STATION_IDS = [s for s in STATION_IDS_RAW.split(",") if s]

GAS_TYPE = GAS_TYPE_RAW if GAS_TYPE_RAW else _GAS_TYPE_DEFAULT
THRESHOLD = float(THRESHOLD_RAW) if THRESHOLD_RAW else _THRESHOLD_DEFAULT

if not GAS_TYPE_RAW:
    log.warning("GAS_TYPE not set, using default: {0}", _GAS_TYPE_DEFAULT)
if not THRESHOLD_RAW:
    log.warning("THRESHOLD not set, using default: {0}", _THRESHOLD_DEFAULT)

_required = {
    "API_KEY": API_KEY,
    "DISCORD_WEBHOOK": DISCORD_URL,
    "STATION_IDS": STATION_IDS,
}
for name, value in _required.items():
    if not value:
        log.error("Missing required environment variable: {0}", name)
        raise ValueError(f"Missing required environment variable: {name}")

log.info("Config loaded. DB: {0}, GAS_TYPE: {1}, THRESHOLD: {2}, DEBUG: {3}", DB_PATH, GAS_TYPE, THRESHOLD, DEBUG)
