import json
from collections import Counter
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt

def count_jordart_entries():
    with open("../aggregated_data.json", "r", encoding="utf-8") as infile:
        data = json.load(infile)
    
    jordart_counter = Counter()
    
    for entry in data:
        jordart = entry.get("jordart", "Unknown")
        jordart_counter[jordart] += 1
    
    return jordart_counter

def save_counts_to_file(counts, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(counts, file, indent=4, ensure_ascii=False)

def count_skadegorare_for_all_jordtyper():
    with open("../aggregated_data.json", "r", encoding="utf-8") as infile:
        data = json.load(infile)
    
    jordtyp_skadegorare_counts = {}
    
    for entry in data:
        jordtyp = entry.get("jordart", "Unknown")
        if jordtyp not in jordtyp_skadegorare_counts:
            jordtyp_skadegorare_counts[jordtyp] = Counter()
        
        for graderingstillfalle in entry.get("graderingstillfalleList", []):
            for gradering in graderingstillfalle.get("graderingList", []):
                if gradering.get("varde", 0) != 0:
                    skadegorare = gradering.get("skadegorare", "Unknown")
                    jordtyp_skadegorare_counts[jordtyp][skadegorare] += 1
    
    return jordtyp_skadegorare_counts

def plot_jordart_counts(counts):
    sorted_counts = dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))
    plt.figure(figsize=(10, 6))
    plt.bar(sorted_counts.keys(), sorted_counts.values(), color='skyblue')
    plt.xlabel("Jordart")
    plt.ylabel("Count")
    plt.title("Jordart Counts")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def plot_skadegorare_counts(skadegorare_counts, output_file="result/jordart_skadegorare_counts.html"):
    # Count the number of subplots needed
    num_plots = len([k for k, v in skadegorare_counts.items() if v])

    if num_plots == 0:
        print("No data to plot.")
        return

    # Create subplots
    fig = make_subplots(rows=num_plots, cols=1, subplot_titles=[f"Skadegorare Counts for {jordtyp}" for jordtyp in skadegorare_counts.keys() if skadegorare_counts[jordtyp]])

    row = 1
    for jordtyp, skadegorare_data in skadegorare_counts.items():
        if not skadegorare_data:
            continue
        
        sorted_data = dict(sorted(skadegorare_data.items(), key=lambda x: x[1], reverse=True))
        fig.add_trace(
            go.Bar(x=list(sorted_data.keys()), y=list(sorted_data.values()), marker_color='skyblue'),
            row=row,
            col=1
        )
        row += 1

    fig.update_layout(height=300 * num_plots, title_text="Skadegorare Counts by Jordtyp", showlegend=False)

    # **Save the figure as an HTML file**
    fig.write_html(output_file)
    print(f"Plot saved as {output_file}")

output_file = "result/jordart_counts.json"
skadegorare_output_file = "result/jordart_skadegorare_count.json"

#Count of jordarts
counts = count_jordart_entries()
save_counts_to_file(counts, output_file)
#plot_jordart_counts(counts)

#Count of skadegorare != 0 based on soiltype
skadegorare_counts = count_skadegorare_for_all_jordtyper()
save_counts_to_file(skadegorare_counts, skadegorare_output_file)
#plot_skadegorare_counts(skadegorare_counts)