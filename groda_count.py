import json
import matplotlib.pyplot as plt

# Load the aggregated data
with open("aggregated_data.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

# Create a dictionary to count records per "groda"
groda_counts = {}
for record in data:
    groda = record.get("groda")
    if groda:
        groda_counts[groda] = groda_counts.get(groda, 0) + 1

# Save the counts to a JSON file
with open("groda_counts.json", "w", encoding="utf-8") as outfile:
    json.dump(groda_counts, outfile, ensure_ascii=False, indent=2)

print("Unique 'groda' counts saved to groda_counts.json.")

# Optionally, sort the counts (largest first) for better visualization
sorted_counts = dict(sorted(groda_counts.items(), key=lambda x: x[1], reverse=True))
groda_names = list(sorted_counts.keys())
counts = list(sorted_counts.values())

# Plot a bar chart using matplotlib
plt.figure(figsize=(10, 6))
bars = plt.bar(groda_names, counts, color='lightgreen')
plt.xlabel("Groda")
plt.ylabel("Number of Records")
plt.title("Record Counts by Groda")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
