import json
import re 
from statistics import mean
from collections import Counter
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

#Extracts and averages pest data (Hägg, Havrebladlus, Bladlus) by year, region, and method (2012–2017), saves to JSON, and plots normalized trends.

def is_valid_year(year, start, end):
    return start <= year <= end

def get_hagg_data(lan="", from_year=None):
    with open("../jordbruksverket_data/jordbruksverket_data.json", "r", encoding="utf-8") as infile:
        data = json.load(infile)

    if from_year is None:
        from_year = 1900 

    start_year = from_year
    end_year = from_year + 5

    target_methods = {"% ang blad 1–3", "antal/strå"}

    year_data = {}
    measuring_method_counts = Counter()

    for entry in data:
        entry_lan = entry.get("lan")
        if lan and entry_lan != lan:
            continue

        groda = entry.get("groda", "").strip().lower()

        for grading_event in entry.get("graderingstillfalleList", []):
            datum = grading_event.get("graderingsdatum")
            year_match = re.search(r"\d{4}", str(datum))
            if not year_match:
                continue
            year = int(year_match.group())

            for grading in grading_event.get("graderingList", []):
                matmetod = grading.get("matmetod", "Unknown Method")
                
                if not is_valid_year(year, start_year, end_year):
                    continue

                skadegorare = grading.get("skadegorare", "").strip().lower()

                if skadegorare in ("havrebladlus", "bladlus"):
                    data_type = skadegorare.title() 
                    
                    if data_type == "Havrebladlus":
                        if matmetod not in target_methods:
                            continue
                        measuring_method_counts[matmetod] += 1
                    
                    key = (entry_lan, matmetod, year, data_type)
                    year_data.setdefault(key, []).append(grading.get("varde", 0.0))
                    continue

                if groda == "hägg" or not skadegorare:
                    data_type = "Hägg"
                    key = (entry_lan, matmetod, year, data_type)
                    year_data.setdefault(key, []).append(grading.get("varde", 0.0))
                    continue

    combined_mean_data = []
    for (lan_val, matmetod_val, year_val, data_type), values in year_data.items():
        combined_mean_data.append({
            "lan": lan_val,
            "matmetod": matmetod_val,
            "year": year_val,
            "type": data_type,
            "mean_varde": round(mean(values), 2) if values else 0.0,
        })

    hagg_data = [record for record in combined_mean_data if record["type"] == "Hägg"]
    havrebladlus_data = [record for record in combined_mean_data if record["type"] == "Havrebladlus"]
    bladlus_data = [record for record in combined_mean_data if record["type"] == "Bladlus"]

    with open("result/hagg_data.json", "w", encoding="utf-8") as outfile:
        json.dump(hagg_data, outfile, ensure_ascii=False, indent=2)
    with open("result/havrebladlus_data.json", "w", encoding="utf-8") as outfile:
        json.dump(havrebladlus_data, outfile, ensure_ascii=False, indent=2)
    with open("result/bladlus_data.json", "w", encoding="utf-8") as outfile:
        json.dump(bladlus_data, outfile, ensure_ascii=False, indent=2)

    return combined_mean_data

def plot_normalized_mean_varde_from_json(json_data):
    df = pd.DataFrame(json_data)
    if df.empty:
        return

    df_pivot = df.pivot_table(
        index="year",
        columns=["type", "matmetod"],
        values="mean_varde",
        aggfunc="mean"
    )

    if df_pivot.empty:
        return

    if df_pivot.max().max() == df_pivot.min().min():
        return

    df_normalized = (df_pivot - df_pivot.min()) / (df_pivot.max() - df_pivot.min())

    ax = df_normalized.plot(kind="bar", figsize=(12, 6))
    ax.set_title("Normalized Mean Varde Over Years")
    ax.set_xlabel("Year")
    ax.set_ylabel("Normalized Mean Varde (0-1)")
    plt.legend(title="Type & Matmetod", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.xticks(rotation=45)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    combined_data = get_hagg_data("Östergötlands län", from_year=2012)
    plot_normalized_mean_varde_from_json(combined_data)