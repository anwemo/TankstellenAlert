import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
API_KEY = os.environ.get("API_KEY")
DB_PATH = os.environ.get(
    "DB_PATH", str(Path(__file__).parent.parent / "tankstellen-alert.db")
)
URL = "https://creativecommons.tankerkoenig.de/json"
DISCORD_URL = os.environ.get("DISCORD_WEBHOOK")
STATION_IDS = [s for s in os.environ.get("STATION_IDS", "").split(",") if s]
GAS_TYPE = os.environ.get("GAS_TYPE", "e10")
THRESHOLD = float(os.environ.get("THRESHOLD", "1.80"))
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}")
