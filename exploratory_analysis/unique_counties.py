import json
import matplotlib.pyplot as plt

# Load the aggregated data
with open("../aggregated_data.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

# Create a dictionary to count records per "lan"
lan_counts = {}
for record in data:
    # Adjust the key if needed (e.g., record["lan"])
    lan = record.get("lan")
    if lan:
        lan_counts[lan] = lan_counts.get(lan, 0) + 1

# Save the counts to a JSON file
with open("result/lan_counts.json", "w", encoding="utf-8") as outfile:
    json.dump(lan_counts, outfile, ensure_ascii=False, indent=2)

print("Unique 'lan' counts saved to lan_counts.json.")

# Optionally sort the dictionary by count (largest first)
sorted_counts = dict(sorted(lan_counts.items(), key=lambda x: x[1], reverse=True))
lan_names = list(sorted_counts.keys())
counts = list(sorted_counts.values())

# Plot a bar chart
plt.figure(figsize=(10, 6))
bars = plt.bar(lan_names, counts, color='skyblue')
plt.xlabel("Lan")
plt.ylabel("Number of Records")
plt.title("Record Counts by Lan")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
