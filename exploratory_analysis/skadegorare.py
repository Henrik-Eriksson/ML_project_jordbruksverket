import json
import matplotlib.pyplot as plt

# Load the aggregated data
with open("../aggregated_data.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

# Create a dictionary to count unique "skadegorare" when "varde" is not 0.0
skadegorare_counts = {}

for record in data:
    # Check if the record has a "graderingstillfalleList"
    if "graderingstillfalleList" in record:
        for grading_case in record["graderingstillfalleList"]:
            if "graderingList" in grading_case:
                for grading in grading_case["graderingList"]:
                    skadegorare = grading.get("skadegorare")
                    varde = grading.get("varde", 0.0)
                    # Only count if varde isn't 0.0 and skadegorare is present
                    if skadegorare is not None and varde != 0.0:
                        skadegorare_counts[skadegorare] = skadegorare_counts.get(skadegorare, 0) + 1

# Save the counts to a JSON file
with open("result/skadegorare_counts.json", "w", encoding="utf-8") as outfile:
    json.dump(skadegorare_counts, outfile, ensure_ascii=False, indent=2)

print("Unique 'skadegorare' counts (non-zero varde) saved to skadegorare_counts.json.")

# Optionally, sort the counts by value (largest first)
sorted_counts = dict(sorted(skadegorare_counts.items(), key=lambda x: x[1], reverse=True))
names = list(sorted_counts.keys())
counts = list(sorted_counts.values())

# Plot a bar chart with matplotlib
plt.figure(figsize=(12, 8))
plt.bar(names, counts, color='purple')
plt.xlabel("Skadegorare")
plt.ylabel("Count (non-zero varde)")
plt.title("Unique Skadegorare Counts (varde != 0.0)")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
