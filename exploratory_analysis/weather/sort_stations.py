import json
from datetime import datetime, timedelta, timezone
#Filters weather stations active between 1987 and 2023, converts timestamps to UTC dates, sorts them by end date, and prints basic station info. 

def convert_timestamp(ts):
    """Convert a Unix millisecond timestamp to a UTC datetime string safely."""
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    return (epoch + timedelta(milliseconds=ts)).isoformat()

THRESHOLD_2023 = 1672531200000


THRESHOLD_FROM = int(datetime(1987, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)

with open('stations_lufttempratur_2.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

stations = data.get("station", [])

filtered_stations = []
for station in stations:
    try:
        to_ts = int(station.get("to", 0))
        from_ts = int(station.get("from", 0))
    except ValueError:
        continue  

    if to_ts >= THRESHOLD_2023 and from_ts <= THRESHOLD_FROM:
        station["to_int"] = to_ts
        station["from_int"] = from_ts
        station["to_date"] = convert_timestamp(to_ts)
        station["from_date"] = convert_timestamp(from_ts)
        filtered_stations.append(station)

filtered_stations.sort(key=lambda s: s.get("to_int", 0), reverse=True)

for station in filtered_stations:
    name = station.get("name", "Unknown")
    station_id = station.get("id", "N/A")
    latitude = station.get("latitude", "N/A")
    longitude = station.get("longitude", "N/A")
    to_int = station.get("to_int", 0)
    from_int = station.get("from_int", 0)
    to_date = station.get("to_date", "N/A")
    from_date = station.get("from_date", "N/A")
    
    print(f"Station Name: {name}, Station ID: {station_id}, Latitude: {latitude}, Longitude: {longitude}")