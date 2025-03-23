import json
import matplotlib.pyplot as plt

#Counts non-zero occurrences of each pest ("skadegorare") across all records, saves the results to JSON, and visualizes them in a bar chart.

with open("../jordbruksverket_data/jordbruksverket_data.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

skadegorare_counts = {}
for record in data:
    if "graderingstillfalleList" in record:
        for grading_case in record["graderingstillfalleList"]:
            if "graderingList" in grading_case:
                for grading in grading_case["graderingList"]:
                    skadegorare = grading.get("skadegorare")
                    varde = grading.get("varde", 0.0)
                    if skadegorare is not None and varde != 0.0:
                        skadegorare_counts[skadegorare] = skadegorare_counts.get(skadegorare, 0) + 1

with open("result/skadegorare_counts.json", "w", encoding="utf-8") as outfile:
    json.dump(skadegorare_counts, outfile, ensure_ascii=False, indent=2)

print("Unique 'skadegorare' counts (non-zero varde) saved to skadegorare_counts.json.")

sorted_counts = dict(sorted(skadegorare_counts.items(), key=lambda x: x[1], reverse=True))
names = list(sorted_counts.keys())
counts = list(sorted_counts.values())

plt.figure(figsize=(12, 8))
plt.bar(names, counts, color='purple')
plt.xlabel("Skadegorare")
plt.ylabel("Count (non-zero varde)")
plt.title("Unique Skadegorare Counts (varde != 0.0)")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
