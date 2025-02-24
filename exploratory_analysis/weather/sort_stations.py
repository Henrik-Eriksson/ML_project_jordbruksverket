import json

# Define the timestamp threshold for 2023-01-01 in Unix milliseconds
THRESHOLD_2023 = 1672531200000

# Load the JSON data from a file. Adjust the filename if needed.
with open('stations_lufttemperatur_19.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Get the list of stations (the key 'station' is assumed to hold the station objects)
stations = data.get("station", [])

# Filter stations with an "updated" timestamp greater than or equal to the threshold
filtered_stations = [
    station for station in stations
    if station.get("updated", 0) >= THRESHOLD_2023
]

# Sort the filtered stations by the "updated" field (most recent first)
filtered_stations.sort(key=lambda s: s.get("updated", 0), reverse=True)

# Print the desired details: station name, station id, latitude, and longitude
for station in filtered_stations:
    name = station.get("name", "Unknown")
    station_id = station.get("id", "N/A")
    latitude = station.get("latitude", "N/A")
    longitude = station.get("longitude", "N/A")
    print(f"Station Name: {name}, Station ID: {station_id}, Latitude: {latitude}, Longitude: {longitude}")
