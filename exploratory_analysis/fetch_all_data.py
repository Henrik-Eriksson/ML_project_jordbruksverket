import requests
import json
import time

#Fetches grading data year-by-year from Jordbruksverket's API (1980–2024), handles retries, and saves all records to a JSON file.

base_url = "https://api.jordbruksverket.se/rest/povapi/graderingar"
all_data = []

headers = {
    "Authorization": "Basic YWlxdTluZWlnaGVpZ2FlYmVlUDhub2hoNGtpZW5nZWk6Sm9yZGJydWtzdmVya2V0"
}

for year in range(1980, 2025):
    params = {
        "fran": f"{year}-01-01",
        "till": f"{year}-12-31"
    }
    print(f"Fetching data for {year}...")

    for attempt in range(5):
        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()  
            data = response.json()

            all_data.extend(data)
            print(f"  Retrieved {len(data)} records for {year}.")
            break  

        except requests.RequestException as e:
            print(f"  Attempt {attempt + 1} failed for {year}: {e}")
            if attempt < 4:
                time.sleep(1)
            else:
                raise Exception(f"Failed to fetch data for {year} after 5 attempts.") from e

    time.sleep(0.5)

with open("../jordbruksverket_data.json", "w", encoding="utf-8") as outfile:
    json.dump(all_data, outfile, ensure_ascii=False, indent=2)

print("Data fetching complete. Aggregated data saved to aggregated_data.json")
