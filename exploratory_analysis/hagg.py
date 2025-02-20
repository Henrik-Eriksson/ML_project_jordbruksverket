import json
import re  # For extracting year from date strings
from statistics import mean
from collections import Counter

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_hagg_data(lan="", from_year=None):
    """
    Extracts Hägg, Havrebladlus, and Bladlus data from aggregated_data.json.

    - Hägg data is extracted from (from_year - 1) to (from_year - 1 + 5).
    - Both Havrebladlus and Bladlus data are extracted from from_year to (from_year + 5).

    Only the two measurement methods in target_methods are considered.
    Saves the separate data to:
      - result/hagg_data.json
      - result/havrebladlus_data.json
      - result/bladlus_data.json
    """
    with open("../aggregated_data.json", "r", encoding="utf-8") as infile:
        data = json.load(infile)

    if from_year is None:
        from_year = 1900  # default fallback

    # Define year ranges:
    # Hägg: from (from_year - 1) to (from_year - 1 + 5)
    hagg_start_year = from_year - 1
    hagg_end_year   = hagg_start_year + 5

    # Havrebladlus & Bladlus: from from_year to (from_year + 5)
    bladlus_start_year = from_year
    bladlus_end_year   = bladlus_start_year + 5

    # Define the two measuring methods to filter
    target_methods = {"% ang blad 1–3", "antal/strå"}

    # Dictionary to store data: key = (lan, matmetod, year, type), value = list of varde
    year_data = {}
    measuring_method_counts = Counter()

    # Debug: Count total grading events processed
    total_events = 0
    total_gradings = 0

    for entry in data:
        entry_lan = entry.get("lan")
        # Filter by lan if provided
        if lan and entry_lan != lan:
            continue

        # If available, check "groda" field to help classify Hägg records
        groda = entry.get("groda", "")

        for grading_event in entry.get("graderingstillfalleList", []):
            datum = grading_event.get("graderingsdatum")
            year_match = re.search(r"\d{4}", str(datum))
            if not year_match:
                # Skip events with no valid year
                continue
            year = int(year_match.group())
            total_events += 1

            for grading in grading_event.get("graderingList", []):
                total_gradings += 1
                matmetod = grading.get("matmetod", "Unknown Method")
                # Skip if not a target measuring method
                if matmetod not in target_methods:
                    continue

                # Determine type:
                # If 'skadegorare' exists and is either "Havrebladlus" or "Bladlus", use that.
                # Otherwise, if not present or empty, and if the "groda" field equals "Hägg", then it's Hägg.
                skadegorare = grading.get("skadegorare", "").strip()
                if skadegorare in ("Havrebladlus", "Bladlus"):
                    data_type = skadegorare
                    # Use bladlus range for both
                    if bladlus_start_year <= year <= bladlus_end_year:
                        measuring_method_counts[matmetod] += 1
                        key = (entry_lan, matmetod, year, data_type)
                        year_data.setdefault(key, []).append(grading.get("varde", 0.0))
                    else:
                        # Debug: Year outside bladlus range
                        # print(f"Skipped {data_type} record for year {year} (expected between {bladlus_start_year} and {bladlus_end_year}).")
                        pass
                else:
                    # Use "Hägg" if groda indicates so, or if skadegorare is empty.
                    if groda == "Hägg" or not skadegorare:
                        data_type = "Hägg"
                        if hagg_start_year <= year <= hagg_end_year:
                            measuring_method_counts[matmetod] += 1
                            key = (entry_lan, matmetod, year, data_type)
                            year_data.setdefault(key, []).append(grading.get("varde", 0.0))
                        else:
                            # Debug: Year outside Hägg range
                            # print(f"Skipped Hägg record for year {year} (expected between {hagg_start_year} and {hagg_end_year}).")
                            pass
                    else:
                        # If skadegorare exists but is not one of the target types, skip.
                        # print(f"Skipping record with unknown skadegorare: {skadegorare}")
                        continue

    print(f"Processed {total_events} grading events and {total_gradings} gradings.")
    print(f"Unique measuring methods found: {dict(measuring_method_counts)}")

    # Compute mean for each (lan, matmetod, year, type)
    combined_mean_data = []
    for (lan_val, matmetod_val, year_val, data_type), values in year_data.items():
        combined_mean_data.append({
            "lan": lan_val,
            "matmetod": matmetod_val,
            "year": year_val,
            "type": data_type,
            "mean_varde": round(mean(values), 2) if values else 0.0,
        })

    # Split data by type
    hagg_data = [record for record in combined_mean_data if record["type"] == "Hägg"]
    havrebladlus_data = [record for record in combined_mean_data if record["type"] == "Havrebladlus"]
    bladlus_data = [record for record in combined_mean_data if record["type"] == "Bladlus"]

    # Debug: print number of records for each type
    print(f"Hägg records: {len(hagg_data)}")
    print(f"Havrebladlus records: {len(havrebladlus_data)}")
    print(f"Bladlus records: {len(bladlus_data)}")

    # Save to separate files
    with open("result/hagg_data.json", "w", encoding="utf-8") as outfile:
        json.dump(hagg_data, outfile, ensure_ascii=False, indent=2)
    with open("result/havrebladlus_data.json", "w", encoding="utf-8") as outfile:
        json.dump(havrebladlus_data, outfile, ensure_ascii=False, indent=2)
    with open("result/bladlus_data.json", "w", encoding="utf-8") as outfile:
        json.dump(bladlus_data, outfile, ensure_ascii=False, indent=2)

    # Return combined data (if needed for further plotting)
    return combined_mean_data


def plot_normalized_mean_varde_from_json(json_data):
    """
    Generates a normalized bar chart from the provided JSON data.
    Normalization is done using Min-Max scaling on the pivoted data.
    """
    df = pd.DataFrame(json_data)
    if df.empty:
        print("No data found to plot.")
        return

    df_pivot = df.pivot_table(
        index="year",
        columns=["type", "matmetod"],
        values="mean_varde",
        aggfunc="mean"
    )

    if df_pivot.empty:
        print("Pivot table is empty.")
        return

    if df_pivot.max().max() == df_pivot.min().min():
        print("All values are the same or no valid data for normalization.")
        print(df_pivot)
        return

    df_normalized = (df_pivot - df_pivot.min()) / (df_pivot.max() - df_pivot.min())

    ax = df_normalized.plot(kind="bar", figsize=(12, 6))
    ax.set_title("Normalized Mean Varde Over Years (Hägg offset by 1 year)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Normalized Mean Varde (0-1)")
    plt.legend(title="Type & Matmetod", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()


# ------------------------
# Example usage
# ------------------------
if __name__ == "__main__":
    combined_data = get_hagg_data("Östergötlands län", from_year=2012)
    combined_data = get_hagg_data(from_year=2012)

    # Load one of the files if needed (here we use the combined data for plotting)
    # For instance, to plot all data:
    plot_normalized_mean_varde_from_json(combined_data)
