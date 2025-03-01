import json
import datetime
import folium
from folium.plugins import HeatMap
from pyproj import Transformer
from folium import Element, JavascriptLink, CssLink
from collections import defaultdict


print("Generating static HTML (takes like 30secs).....")
def is_inside_sweden(lat, lon, lat_min=55.0, lat_max=70.0, lon_min=10.0, lon_max=25.0):
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max

def gather_pests(record):
    """Return a set of all 'skadegorare' (pests) found in the record."""
    pests = set()
    for entry in record.get("graderingstillfalleList", []):
        for grade in entry.get("graderingList", []):
            pest = grade.get("skadegorare")
            if pest:
                pests.add(pest)
    return pests

def get_earliest_date(record):
    """Return the earliest graderingsdatum as a datetime, or None if none exist."""
    earliest = None
    for entry in record.get("graderingstillfalleList", []):
        d = entry.get("graderingsdatum")
        if d:
            try:
                dt = datetime.datetime.strptime(d, "%Y-%m-%d")
                if earliest is None or dt < earliest:
                    earliest = dt
            except:
                pass
    return earliest

transformer = Transformer.from_crs("EPSG:3006", "EPSG:4326", always_xy=True)

with open("../../jordbruksverket_data/jordbruksverket_data.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

indexed_records = []  # store (record_id, record)
dateIndexList = []    # store [epoch_ms, record_id]
pestIndex = defaultdict(list)   # { pest => [record_id, ...] }
grodaIndex = defaultdict(list)  # { groda => [record_id, ...] }
lanIndex = defaultdict(list)

all_dates = []
record_id_to_obj = {}
next_id = 0

# 1) Convert coords, gather pests/crops, compute earliest date, fill indices
for original_record in data:
    lat = original_record.get("latitud")
    lon = original_record.get("longitud")
    if lat is None or lon is None:
        continue
    try:
        lon_deg, lat_deg = transformer.transform(float(lon), float(lat))
        # Make a shallow copy or just store in a new dict:
        record = dict(original_record)
        record["lat_wgs84"] = lat_deg
        record["lon_wgs84"] = lon_deg

        # gather groda
        g = record.get("groda", "")
        # gather pests
        pset = gather_pests(record)
        record["pests"] = list(pset)

        # compute earliest date
        earliest_dt = get_earliest_date(record)

        # if inside Sweden
        if is_inside_sweden(lat_deg, lon_deg):
            # Assign an ID
            rid = next_id
            next_id += 1

            record_id_to_obj[rid] = record

            # fill dateIndexList
            if earliest_dt:
                epoch_ms = int(earliest_dt.timestamp() * 1000)
                dateIndexList.append([epoch_ms, rid])
                all_dates.append(earliest_dt)

            # fill pestIndex
            for pest in pset:
                pestIndex[pest].append(rid)

            # fill grodaIndex
            if g:
                grodaIndex[g].append(rid)

            lan = record.get("lan", "Unknown")
            lanIndex[lan].append(rid)

    except:
        continue

# 2) Sort dateIndexList by epoch
dateIndexList.sort(key=lambda x: x[0])

# 3) Overall date bounds
if all_dates:
    min_date = min(all_dates)
    max_date = max(all_dates)
    min_epoch = int(min_date.timestamp() * 1000)
    max_epoch = int(max_date.timestamp() * 1000)
else:
    min_epoch = 0
    max_epoch = 0

# 4) Convert our Python structures to JSON
idToRecord_json = json.dumps({str(rid): record_id_to_obj[rid] for rid in record_id_to_obj})
dateIndex_json  = json.dumps(dateIndexList)  # array of [epoch, rid]
pestIndex_json  = json.dumps({k: v for k,v in pestIndex.items()})
grodaIndex_json = json.dumps({k: v for k,v in grodaIndex.items()})

unique_grodas_list = sorted(grodaIndex.keys())
unique_pests_list = sorted(pestIndex.keys())

grodas_json = json.dumps(list(unique_grodas_list))
pests_json  = json.dumps(list(unique_pests_list))

unique_lans_list = sorted(lanIndex.keys())
lans_json = json.dumps(list(unique_lans_list))
lanIndex_json = json.dumps({k: v for k, v in lanIndex.items()})


# Basic Folium map using just the lat/lon for initial display
m = folium.Map(location=[63, 16], zoom_start=6)

# (Optional) You could build an initial HeatMap from dateIndexList or skipping it
# We'll skip or do a small demonstration
# We'll do no HeatMap for now or a minimal one
folium.TileLayer("openstreetmap").add_to(m)

map_name = m.get_name()

init_js = f"""
window.idToRecord = {idToRecord_json};
window.dateIndex  = {dateIndex_json};
window.pestIndex  = {pestIndex_json};
window.grodaIndex = {grodaIndex_json};
window.lanIndex   = {lanIndex_json};

window.grodaList  = {grodas_json};
window.pestList   = {pests_json};
window.lanList    = {lans_json};
window.grodaCounts = {{}}; 
window.pestCounts = {{}};


window.minDateEpoch = {min_epoch};
window.maxDateEpoch = {max_epoch};
window.selectedMinDate = window.minDateEpoch;
window.selectedMaxDate = window.maxDateEpoch;

window.selectedGrodas = new Set(window.grodaList);
window.selectedPests = new Set(window.pestList);

window.selectedLans = new Set(window.lanList || []);


document.addEventListener('DOMContentLoaded', function() {{
  window.map = window['{map_name}'];
  if (!window.map) {{
    console.log("Map object not found under window['{map_name}'].");
  }} else {{
    console.log("Assigned 'window.map' to {map_name} successfully.");
  }}
  updateHeatmap();
  
}});


"""

m.get_root().script.add_child(Element(init_js))

# Add external libs
m.get_root().html.add_child(JavascriptLink("https://cdn.jsdelivr.net/npm/leaflet.heat@0.2.0/dist/leaflet-heat.min.js"))
m.get_root().header.add_child(CssLink("https://cdnjs.cloudflare.com/ajax/libs/noUiSlider/15.7.0/nouislider.min.css"))
m.get_root().html.add_child(JavascriptLink("https://cdnjs.cloudflare.com/ajax/libs/noUiSlider/15.7.0/nouislider.min.js"))
m.get_root().header.add_child(CssLink("https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/9.5.6/jsoneditor.min.css"))
m.get_root().html.add_child(JavascriptLink("https://cdnjs.cloudflare.com/ajax/libs/jsoneditor/9.5.6/jsoneditor.min.js"))
m.get_root().html.add_child(JavascriptLink("https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"))
m.get_root().header.add_child(CssLink("https://code.jquery.com/ui/1.13.2/themes/smoothness/jquery-ui.css"))
m.get_root().html.add_child(JavascriptLink("https://code.jquery.com/ui/1.13.2/jquery-ui.min.js"))

# Now reference your splitted JS
m.get_root().html.add_child(JavascriptLink("./static/helpers.js"))
m.get_root().html.add_child(JavascriptLink("./static/filters.js"))
m.get_root().html.add_child(JavascriptLink("./static/date_slider.js"))
m.get_root().html.add_child(JavascriptLink("./static/region_box.js"))
m.get_root().html.add_child(JavascriptLink("./static/main_logic.js"))

m.save("sweden_heatmap_split_js.html")
print("Map with indexing approach saved to 'sweden_heatmap_split_js.html'")
