import json
import matplotlib.pyplot as plt

#Filters records for "Höstvete", counts non-zero pest ("skadegorare") occurrences, saves the results to JSON, and plots them in a bar chart.

groda = "Höstvete"

with open("../jordbruksverket_data/jordbruksverket_data.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

skadegorare_counts_hostvete = {}

for record in data:
    if record.get("groda") == groda:
        if "graderingstillfalleList" in record:
            for grading_case in record["graderingstillfalleList"]:
                if "graderingList" in grading_case:
                    for grading in grading_case["graderingList"]:
                        skadegorare = grading.get("skadegorare")
                        varde = grading.get("varde", 0.0)
                        if skadegorare and varde != 0.0:
                            skadegorare_counts_hostvete[skadegorare] = skadegorare_counts_hostvete.get(skadegorare, 0) + 1

with open("result/skadegorare_hostvete_counts.json", "w", encoding="utf-8") as outfile:
    json.dump(skadegorare_counts_hostvete, outfile, ensure_ascii=False, indent=2)

print(f"Unique 'skadegorare' counts for groda {groda} (varde != 0.0) saved to skadegorare_{groda}_counts.json.")

sorted_counts = dict(sorted(skadegorare_counts_hostvete.items(), key=lambda x: x[1], reverse=True))
names = list(sorted_counts.keys())
counts = list(sorted_counts.values())

plt.figure(figsize=(12, 8))
plt.bar(names, counts, color='green')
plt.xlabel("Skadegorare")
plt.ylabel("Count (non-zero varde)")
plt.title(f"Unique Skadegorare Counts for groda {groda} (varde != 0.0)")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
