import requests
import json
import time

base_url = "https://api.jordbruksverket.se/rest/povapi/graderingar"
all_data = []

# Set up the headers with the provided authorization token.
headers = {
    "Authorization": "Basic YWlxdTluZWlnaGVpZ2FlYmVlUDhub2hoNGtpZW5nZWk6Sm9yZGJydWtzdmVya2V0"
}

# Loop over years from 1980 through 2024 (inclusive)
for year in range(1980, 2025):
    params = {
        "fran": f"{year}-01-01",
        "till": f"{year}-12-31"
    }
    print(f"Fetching data for {year}...")

    # Try up to 5 times
    for attempt in range(5):
        try:
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()  # Raise exception for HTTP errors
            data = response.json()

            # Append the data (assumes the response is a list)
            all_data.extend(data)
            print(f"  Retrieved {len(data)} records for {year}.")
            break  # Exit the retry loop on success

        except requests.RequestException as e:
            print(f"  Attempt {attempt + 1} failed for {year}: {e}")
            if attempt < 4:
                time.sleep(1)
            else:
                raise Exception(f"Failed to fetch data for {year} after 5 attempts.") from e

    # Optional: Pause before next year's request
    time.sleep(0.5)

# Write the aggregated data to a JSON file
with open("../aggregated_data.json", "w", encoding="utf-8") as outfile:
    json.dump(all_data, outfile, ensure_ascii=False, indent=2)

print("Data fetching complete. Aggregated data saved to aggregated_data.json")
