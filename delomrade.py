import json
import matplotlib.pyplot as plt

# Load the aggregated data
with open("aggregated_data.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

# Create a dictionary to count records per "delomrade"
delomrade_counts = {}
for record in data:
    # Use the value of "delomrade" if it exists
    delomrade = record.get("delomrade")
    if delomrade:
        delomrade_counts[delomrade] = delomrade_counts.get(delomrade, 0) + 1

# Save the counts to a JSON file
with open("delomrade_counts.json", "w", encoding="utf-8") as outfile:
    json.dump(delomrade_counts, outfile, ensure_ascii=False, indent=2)

print("Unique 'delomrade' counts saved to delomrade_counts.json.")

# Optionally sort the dictionary by count (largest first)
sorted_counts = dict(sorted(delomrade_counts.items(), key=lambda x: x[1], reverse=True))
delomrade_names = list(sorted_counts.keys())
counts = list(sorted_counts.values())

# Plot a bar chart
plt.figure(figsize=(10, 6))
plt.bar(delomrade_names, counts, color='salmon')
plt.xlabel("Delomrade")
plt.ylabel("Number of Records")
plt.title("Record Counts by Delomrade")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
