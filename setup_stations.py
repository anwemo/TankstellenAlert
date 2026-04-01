import os
import requests
from dotenv import load_dotenv
from prettytable import PrettyTable

load_dotenv()

API_KEY = os.environ.get("API_KEY")
URL = "https://creativecommons.tankerkoenig.de/json"
LAT = os.environ.get("LAT")
LNG = os.environ.get("LNG")
RADIUS = 2.0

params = {
    "lat": float(LAT),
    "lng": float(LNG),
    "rad": RADIUS,
    "type": "all",
    "apikey": API_KEY,
}

r = requests.get(URL + "/list.php", params=params)
r.raise_for_status()
stations = r.json().get("stations", [])

table = PrettyTable()
table.field_names = ["ID", "Name", "Brand", "Address", "Postcode", "City"]
for station in stations:
    table.add_row([station.get("id"),
                   station.get("name"),
                   station.get("brand"),
                   f"{station.get('street')} {station.get('houseNumber')}",
                   station.get("postCode"),
                   station.get("place")]
                  )

print(table)
