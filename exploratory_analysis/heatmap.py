import json
import folium
from folium.plugins import HeatMap
from pyproj import Transformer
from folium import Element, JavascriptLink, CssLink

#Converts SWEREF 99 TM coordinates to WGS84, filters records within Sweden, saves location+crop data, and visualizes them as a heatmap using Folium.

def is_inside_sweden(lat, lon, lat_min=55.0, lat_max=70.0, lon_min=10.0, lon_max=25.0):
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max

transformer = Transformer.from_crs("EPSG:3006", "EPSG:4326", always_xy=True)

with open("../jordbruksverket_data/jordbruksverket_data.json", "r", encoding="utf-8") as infile:
    data = json.load(infile)

heat_data = []
filtered_records = []
json_heat_data = []
not_inside_sweden_ctr = 0

for record in data:
    lat = record.get("latitud")
    lon = record.get("longitud")
    groda = record.get("groda")
    if lat is None or lon is None:
        continue
    try:
        northing = float(lat)
        easting = float(lon)
        lon_deg, lat_deg = transformer.transform(easting, northing)
        record["lat_wgs84"] = lat_deg
        record["lon_wgs84"] = lon_deg
        if is_inside_sweden(lat_deg, lon_deg):
            heat_data.append([lat_deg, lon_deg])
            json_heat_data.append([lat_deg, lon_deg])
            json_heat_data.append(groda)
            filtered_records.append(record)
        else:
            not_inside_sweden_ctr += 1
    except Exception:
        continue

with open("result/lat_lon_fields.json", "w", encoding="utf-8") as outfile:
    json.dump(json_heat_data, outfile, ensure_ascii=False, indent=2)

print("Number of records outside Sweden:", not_inside_sweden_ctr)

m = folium.Map(location=[63, 16], zoom_start=6)
HeatMap(heat_data, radius=8, max_zoom=13).add_to(m)

filtered_data_json = json.dumps(filtered_records)

map_name = m.get_name()

#JS to create the sliders etc. to make the heatmap interactive 
my_js = f"""
console.log('working perfectly');
document.addEventListener('DOMContentLoaded', function() {{
    var aggregatedData = {filtered_data_json};
    var radiusThreshold = 0.05; 

    function degreesToMeters(deg) {{
        return deg * 111320;
    }}
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

    var cursorCircle = null;  
    var fixedCircle = null;   

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

    function onMapClick(e) {{
         var clickedLat = e.latlng.lat;
         var clickedLng = e.latlng.lng;
         console.log("Map clicked at:", clickedLat, clickedLng);
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
m.get_root().script.add_child(Element(my_js))

m.save("result/sweden_heatmap_filtered_click.html")
print("Map with filtered points, click event, slider, and cursor circle saved to sweden_heatmap_filtered_click.html")
