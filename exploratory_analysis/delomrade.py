import json
import matplotlib.pyplot as plt

#Loads JSON data, counts occurrences of each "delomrade", saves results, and plots them as a bar chart.

with open("../jordbruksverket_data/jordbruksverket_data.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

delomrade_counts = {}
for record in data:
    delomrade = record.get("delomrade")
    if delomrade:
        delomrade_counts[delomrade] = delomrade_counts.get(delomrade, 0) + 1

with open("result/delomrade_counts.json", "w", encoding="utf-8") as outfile:
    json.dump(delomrade_counts, outfile, ensure_ascii=False, indent=2)

print("Unique 'delomrade' counts saved to delomrade_counts.json.")

sorted_counts = dict(sorted(delomrade_counts.items(), key=lambda x: x[1], reverse=True))
delomrade_names = list(sorted_counts.keys())
counts = list(sorted_counts.values())

plt.figure(figsize=(10, 6))
plt.bar(delomrade_names, counts, color='salmon')
plt.xlabel("Delomrade")
plt.ylabel("Number of Records")
plt.title("Record Counts by Delomrade")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
