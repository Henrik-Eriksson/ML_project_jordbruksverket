import json
import matplotlib.pyplot as plt

groda = "Höstvete"

# Load aggregated data
with open("../aggregated_data.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

# Create a dictionary to count unique "skadegorare" for groda "Höstvete" (only if varde != 0.0)
skadegorare_counts_hostvete = {}

for record in data:
    # Only consider records with groda "Höstvete"
    if record.get("groda") == groda:
        # Make sure the record has grading information
        if "graderingstillfalleList" in record:
            for grading_case in record["graderingstillfalleList"]:
                if "graderingList" in grading_case:
                    for grading in grading_case["graderingList"]:
                        skadegorare = grading.get("skadegorare")
                        varde = grading.get("varde", 0.0)
                        # Only count if varde is not 0.0
                        if skadegorare and varde != 0.0:
                            skadegorare_counts_hostvete[skadegorare] = skadegorare_counts_hostvete.get(skadegorare, 0) + 1

# Save the counts to a JSON file
with open("result/skadegorare_hostvete_counts.json", "w", encoding="utf-8") as outfile:
    json.dump(skadegorare_counts_hostvete, outfile, ensure_ascii=False, indent=2)

print(f"Unique 'skadegorare' counts for groda {groda} (varde != 0.0) saved to skadegorare_{groda}_counts.json.")

# Optionally sort the counts (largest first)
sorted_counts = dict(sorted(skadegorare_counts_hostvete.items(), key=lambda x: x[1], reverse=True))
names = list(sorted_counts.keys())
counts = list(sorted_counts.values())

# Plot a bar chart
plt.figure(figsize=(12, 8))
plt.bar(names, counts, color='green')
plt.xlabel("Skadegorare")
plt.ylabel("Count (non-zero varde)")
plt.title(f"Unique Skadegorare Counts for groda {groda} (varde != 0.0)")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
