import json
from datetime import datetime

def extract_unique_dates(data):
    unique_dates = set()
    for record in data:
        if record.get("groda", "").lower() == "höstvete" or "havre" or "vårvete" or "rågvete":
            events = record.get("graderingstillfalleList", [])
            for event in events:
                date = event.get("graderingsdatum")
                if date and date > "2015-01-01":
                    # Check if the pest "bladfläcksvampar" is present in any measurement.
                    for measurement in event.get("graderingList", []):
                        if measurement.get("skadegorare", "").lower() == "bladfläcksvampar":
                            unique_dates.add(date)
                            break  # Stop after finding the matching pest in the current event.
    return sorted(unique_dates)

def main():
    input_file = "../jordbruksverket_data/jordbruksverket_data.json"
    output_file = "result/unique_dates3_WITH_MORE.json"
    
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    unique_dates = extract_unique_dates(data)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(unique_dates, f, indent=2, ensure_ascii=False)
    
    print(f"Unique dates saved to {output_file}")

if __name__ == "__main__":
    main()
