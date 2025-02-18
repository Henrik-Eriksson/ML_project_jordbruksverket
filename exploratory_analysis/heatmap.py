import json
import folium
from folium.plugins import HeatMap
from pyproj import Transformer
from folium import Element, JavascriptLink, CssLink

def is_inside_sweden(lat, lon, lat_min=55.0, lat_max=70.0, lon_min=10.0, lon_max=25.0):
    """
    Returns True if (lat, lon) is within the defined bounds for Sweden.
    """
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max

# Create a transformer to convert from SWEREF 99 TM (EPSG:3006) to WGS84 (EPSG:4326)
transformer = Transformer.from_crs("EPSG:3006", "EPSG:4326", always_xy=True)

# Load the aggregated data from file.
with open("../aggregated_data.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

# Prepare lists for the heatmap and for filtered records (inside Sweden).
heat_data = []
filtered_records = []
not_inside_sweden_ctr = 0

for record in data:
    lat = record.get("latitud")
    lon = record.get("longitud")
    if lat is None or lon is None:
        continue
    try:
        # Convert the coordinates (assumed to be in SWEREF 99 TM)
        northing = float(lat)
        easting = float(lon)
        # transformer.transform expects (easting, northing)
        lon_deg, lat_deg = transformer.transform(easting, northing)
        # Store the converted coordinates in the record.
        record["lat_wgs84"] = lat_deg
        record["lon_wgs84"] = lon_deg
        # Check if the converted coordinates are inside Sweden.
        if is_inside_sweden(lat_deg, lon_deg):
            heat_data.append([lat_deg, lon_deg])
            filtered_records.append(record)
        else:
            not_inside_sweden_ctr += 1
    except Exception:
        continue

print("Number of records outside Sweden:", not_inside_sweden_ctr)

# Create a Folium map centered on Sweden.
m = folium.Map(location=[63, 16], zoom_start=6)
HeatMap(heat_data, radius=8, max_zoom=13).add_to(m)

# Dump the filtered records (only inside Sweden) into a JSON string for JavaScript.
filtered_data_json = json.dumps(filtered_records)

# Get the Folium map variable name.
map_name = m.get_name()

# Define custom JavaScript.
# This script:
#  - Creates a slider (range input) at the top left to adjust the selection radius.
#  - Updates a global variable 'radiusThreshold' when the slider is moved.
#  - Attaches a mousemove event to show a blue dashed circle following the cursor.
#  - Attaches a click event that draws a fixed red dashed circle at the clicked location and logs nearby records.
#  - Uses a simple degrees-to-meters conversion function.
my_js = f"""
console.log('working perfectly');
document.addEventListener('DOMContentLoaded', function() {{
    var aggregatedData = {filtered_data_json};
    var radiusThreshold = 0.05; // initial threshold in degrees

    // Simple conversion from degrees to meters (latitude-based approximation)
    function degreesToMeters(deg) {{
        return deg * 111320;
    }}

    // Create a slider container and add it to the document body.
    var sliderContainer = document.createElement('div');
    sliderContainer.style.position = 'fixed';
    sliderContainer.style.top = '10px';
    sliderContainer.style.left = '10px';
    sliderContainer.style.zIndex = 1000;
    sliderContainer.style.background = 'white';
    sliderContainer.style.padding = '10px';
    sliderContainer.style.border = '1px solid #ccc';
    sliderContainer.innerHTML = '<label for="radiusSlider">Selection Radius (°): </label>' +
                                '<input type="range" id="radiusSlider" min="0.01" max="0.2" step="0.01" value="0.05">' +
                                '<span id="radiusValue">0.05</span>';
    document.body.appendChild(sliderContainer);

    // Update the threshold when slider value changes.
    var slider = document.getElementById('radiusSlider');
    var radiusValueSpan = document.getElementById('radiusValue');
    slider.addEventListener('input', function() {{
        radiusThreshold = parseFloat(slider.value);
        radiusValueSpan.innerText = radiusThreshold.toFixed(2);
        if (cursorCircle) {{
            cursorCircle.setRadius(degreesToMeters(radiusThreshold));
        }}
        if (fixedCircle) {{
            fixedCircle.setRadius(degreesToMeters(radiusThreshold));
        }}
    }});

    var cursorCircle = null;  // circle that follows the cursor
    var fixedCircle = null;   // circle fixed on click

    // Attach mousemove event to show/update the cursor circle.
    function onMapMouseMove(e) {{
         var lat = e.latlng.lat;
         var lng = e.latlng.lng;
         if (!cursorCircle) {{
             cursorCircle = L.circle([lat, lng], {{
                 radius: degreesToMeters(radiusThreshold),
                 color: 'blue',
                 dashArray: '5,5',
                 fill: false
             }});
             map.addLayer(cursorCircle);
         }} else {{
             cursorCircle.setLatLng([lat, lng]);
             cursorCircle.setRadius(degreesToMeters(radiusThreshold));
         }}
    }}

    // Click event: draw a fixed red dashed circle and log nearby records.
    function onMapClick(e) {{
         var clickedLat = e.latlng.lat;
         var clickedLng = e.latlng.lng;
         console.log("Map clicked at:", clickedLat, clickedLng);
         // Remove the fixed circle if it exists.
         if (fixedCircle) {{
             map.removeLayer(fixedCircle);
         }}
         fixedCircle = L.circle([clickedLat, clickedLng], {{
             radius: degreesToMeters(radiusThreshold),
             color: 'red',
             dashArray: '5,5',
             fill: false
         }});
         fixedCircle.addTo(map);

         var nearbyRecords = aggregatedData.filter(function(record) {{
             var lat = parseFloat(record.lat_wgs84);
             var lng = parseFloat(record.lon_wgs84);
             if (isNaN(lat) || isNaN(lng)) return false;
             return Math.abs(lat - clickedLat) < radiusThreshold &&
                    Math.abs(lng - clickedLng) < radiusThreshold;
         }});
         console.log("Nearby records:", nearbyRecords);
    }}

    // Wait a moment to ensure the map variable is defined.
    setTimeout(function() {{
         try {{
             var map_obj = eval("{map_name}");
             if (map_obj) {{
                window.map = map_obj; // assign to a global variable 'map'
                map.on('mousemove', onMapMouseMove);
                map.on('click', onMapClick);
                console.log("Mousemove and click events attached to map:", "{map_name}");
             }} else {{
                console.log("Map object is null or undefined.");
             }}
         }} catch (err) {{
             console.log("Error evaluating map variable:", err);
         }}
    }}, 1000);
}});
"""

# Attach the inline JavaScript to the HTML.
m.get_root().script.add_child(Element(my_js))

# (Optional) You can also add external CSS/JS if needed:
# m.get_root().header.add_child(CssLink('./static/style.css'))
# m.get_root().html.add_child(JavascriptLink('./static/js.js'))

# Save the resulting map to an HTML file.
m.save("result/sweden_heatmap_filtered_click.html")
print("Map with filtered points, click event, slider, and cursor circle saved to sweden_heatmap_filtered_click.html")
