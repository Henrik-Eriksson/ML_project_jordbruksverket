import json
import math
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Load aggregated data
with open("../aggregated_data.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

# Compute counts of unique "skadegorare" for each "groda" (crop),
# only if "varde" != 0.0
groda_skadegorare_counts = {}
for record in data:
    groda = record.get("groda")
    if not groda:
        continue
    if groda not in groda_skadegorare_counts:
        groda_skadegorare_counts[groda] = {}
    if "graderingstillfalleList" in record:
        for grading_case in record["graderingstillfalleList"]:
            if "graderingList" in grading_case:
                for grading in grading_case["graderingList"]:
                    varde = grading.get("varde", 0.0)
                    if varde != 0.0:
                        skadegorare = grading.get("skadegorare")
                        if skadegorare:
                            groda_skadegorare_counts[groda][skadegorare] = \
                                groda_skadegorare_counts[groda].get(skadegorare, 0) + 1

# Get a sorted list of unique crops ("groda") based on total records (sum of counts) descending
sorted_groda = sorted(
    groda_skadegorare_counts.keys(), 
    key=lambda g: sum(groda_skadegorare_counts[g].values()),
    reverse=True
)

# Define grid dimensions: We'll use 5 columns.
cols = 5
num_graphs = len(sorted_groda)
rows = math.ceil(num_graphs / cols)

# Prepare subplot titles: use groda names for the first num_graphs subplots; others blank
subplot_titles = sorted_groda + [""] * (rows * cols - num_graphs)

# Create subplots grid
fig = make_subplots(
    rows=rows,
    cols=cols,
    subplot_titles=subplot_titles,
    vertical_spacing=0.1,
    horizontal_spacing=0.05
)

# For each groda, add a bar chart to its corresponding grid cell
for i, groda in enumerate(sorted_groda):
    # Compute row and column indices (Plotly indexing starts at 1)
    row_idx = i // cols + 1
    col_idx = i % cols + 1

    counts_dict = groda_skadegorare_counts[groda]
    # Sort counts for each groda by count (largest first)
    sorted_counts = dict(sorted(counts_dict.items(), key=lambda x: x[1], reverse=True))
    names = list(sorted_counts.keys())
    counts = list(sorted_counts.values())

    # Add bar chart trace to the specific subplot cell
    fig.add_trace(
        go.Bar(x=names, y=counts, name=groda),
        row=row_idx, col=col_idx
    )
    # Update the x-axis tick angle for clarity
    fig.update_xaxes(tickangle=45, row=row_idx, col=col_idx)

# Adjust overall figure layout (modify width and height as desired)
fig.update_layout(
    height=400 * rows,   # e.g., 400 pixels per row
    width=350 * cols,    # e.g., 350 pixels per column
    title_text="Unique 'Skadegorare' Counts per Groda (sorted by total records, varde != 0.0)",
    showlegend=False
)

# Save the composite interactive plot to an HTML file
fig.write_html("result/composite_groda_skadegorare_grid_sorted.html")
print("Composite interactive plot saved to composite_groda_skadegorare_grid_sorted.html")
