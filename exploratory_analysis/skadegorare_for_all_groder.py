import json
import math
from plotly.subplots import make_subplots
import plotly.graph_objects as go

#Aggregates and visualizes non-zero pest ("skadegorare") counts per crop ("groda") in a grid of interactive bar charts, sorted by total records, and saves as an HTML file.

with open("../jordbruksverket_data/jordbruksverket_data.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

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

sorted_groda = sorted(
    groda_skadegorare_counts.keys(), 
    key=lambda g: sum(groda_skadegorare_counts[g].values()),
    reverse=True
)

cols = 5
num_graphs = len(sorted_groda)
rows = math.ceil(num_graphs / cols)

subplot_titles = sorted_groda + [""] * (rows * cols - num_graphs)

fig = make_subplots(
    rows=rows,
    cols=cols,
    subplot_titles=subplot_titles,
    vertical_spacing=0.1,
    horizontal_spacing=0.05
)

for i, groda in enumerate(sorted_groda):
    row_idx = i // cols + 1
    col_idx = i % cols + 1

    counts_dict = groda_skadegorare_counts[groda]
    sorted_counts = dict(sorted(counts_dict.items(), key=lambda x: x[1], reverse=True))
    names = list(sorted_counts.keys())
    counts = list(sorted_counts.values())

    fig.add_trace(
        go.Bar(x=names, y=counts, name=groda),
        row=row_idx, col=col_idx
    )
    fig.update_xaxes(tickangle=45, row=row_idx, col=col_idx)

fig.update_layout(
    height=400 * rows,   
    width=350 * cols,    
    title_text="Unique 'Skadegorare' Counts per Groda (sorted by total records, varde != 0.0)",
    showlegend=False
)

fig.write_html("result/composite_groda_skadegorare_grid_sorted.html")
print("Composite interactive plot saved to composite_groda_skadegorare_grid_sorted.html")
