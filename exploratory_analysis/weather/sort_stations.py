import json
from datetime import datetime, timedelta, timezone

def convert_timestamp(ts):
    """Convert a Unix millisecond timestamp to a UTC datetime string safely."""
    epoch = datetime(1970, 1, 1, tzinfo=timezone.utc)
    return (epoch + timedelta(milliseconds=ts)).isoformat()

# Define the timestamp threshold for 2023-01-01 in Unix milliseconds (for the "to" field)
THRESHOLD_2023 = 1672531200000

# Define the threshold for the "from" timestamp:
# Only include stations that have a "from" timestamp on or before 1987-01-01.
THRESHOLD_FROM = int(datetime(1987, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)

# Load the JSON data from a file. Adjust the filename if needed.
with open('stations_lufttempratur_2.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Get the list of stations (assuming the key 'station' holds the station objects)
stations = data.get("station", [])

filtered_stations = []
for station in stations:
    try:
        # Explicitly convert the timestamps to integers
        to_ts = int(station.get("to", 0))
        from_ts = int(station.get("from", 0))
    except ValueError:
        continue  # Skip stations with non-numeric timestamps

    # Only include stations with "to" on or after 2023-01-01 and "from" on or before 1987-01-01.
    if to_ts >= THRESHOLD_2023 and from_ts <= THRESHOLD_FROM:
        station["to_int"] = to_ts
        station["from_int"] = from_ts
        station["to_date"] = convert_timestamp(to_ts)
        station["from_date"] = convert_timestamp(from_ts)
        filtered_stations.append(station)

# Sort the filtered stations by the "to" field (most recent first)
filtered_stations.sort(key=lambda s: s.get("to_int", 0), reverse=True)

# Print details along with the raw and converted timestamps
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