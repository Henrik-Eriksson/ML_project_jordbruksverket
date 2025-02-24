// region_box.js
console.log("region_box.js loaded.");

/**
 * This region box shows a summary for each region (lan) with an integrated
 * checkbox (so you can select/deselect that region), the region name with its record count,
 * and an expand button to view the details. There are also "Select All" and "Deselect All" buttons.
 *
 * The region box is updated each time the filtered records change.
 */

// Global references for the region box elements.
let regionBoxElem = null;
let regionBoxContentElem = null;
let regionBoxHeaderElem = null;
let isRegionBoxMaximized = false;

const defaultRegionBoxStyle = {
  top: "100px",
  right: "20px",
  width: "300px",
  height: "400px"
};
const maximizedRegionBoxStyle = {
  top: "0px",
  left: "0px",
  width: "100%",
  height: "100%"
};

/** Called once at DOMContentLoaded to build the region box. */
function initRegionBox() {
  // Create the main container.
  regionBoxElem = document.createElement("div");
  regionBoxElem.id = "regionBox";
  regionBoxElem.style.position = "fixed";
  regionBoxElem.style.top = defaultRegionBoxStyle.top;
  regionBoxElem.style.right = defaultRegionBoxStyle.right;
  regionBoxElem.style.width = defaultRegionBoxStyle.width;
  regionBoxElem.style.height = defaultRegionBoxStyle.height;
  regionBoxElem.style.overflow = "auto";
  regionBoxElem.style.background = "white";
  regionBoxElem.style.border = "1px solid #ccc";
  regionBoxElem.style.zIndex = 10000;
  regionBoxElem.style.resize = "both";
  document.body.appendChild(regionBoxElem);

  // Header with title, total count, toggle and download buttons.
  regionBoxHeaderElem = document.createElement("div");
  regionBoxHeaderElem.id = "regionBoxHeader";
  regionBoxHeaderElem.style.cursor = "move";
  regionBoxHeaderElem.style.background = "#ddd";
  regionBoxHeaderElem.style.padding = "5px";
  regionBoxHeaderElem.style.borderBottom = "1px solid #ccc";
  regionBoxHeaderElem.innerHTML =
    "<span><b>Region Box</b></span> <span id='totalRecordCount' style='margin-left:10px;'></span> " +
    "<button id='regionBoxToggle'>Maximize</button> " +
    "<button id='downloadJsonBtn'>Download JSON</button>";
  regionBoxElem.appendChild(regionBoxHeaderElem);

  // Create content container for region summaries.
  regionBoxContentElem = document.createElement("div");
  regionBoxContentElem.id = "regionBoxContent";
  regionBoxElem.appendChild(regionBoxContentElem);

  // Make the region box draggable/resizable (requires jQuery UI).
  $(() => {
    $("#regionBox").draggable({ handle: "#regionBoxHeader" });
    $("#regionBox").resizable();
  });

  // Set up toggle and download buttons.
  const toggleBtn = document.getElementById("regionBoxToggle");
  toggleBtn.addEventListener("click", function () {
    if (!isRegionBoxMaximized) {
      regionBoxElem.style.top = maximizedRegionBoxStyle.top;
      regionBoxElem.style.left = maximizedRegionBoxStyle.left;
      regionBoxElem.style.width = maximizedRegionBoxStyle.width;
      regionBoxElem.style.height = maximizedRegionBoxStyle.height;
      toggleBtn.innerText = "Minimize";
      isRegionBoxMaximized = true;
    } else {
      regionBoxElem.style.top = defaultRegionBoxStyle.top;
      regionBoxElem.style.right = defaultRegionBoxStyle.right;
      regionBoxElem.style.width = defaultRegionBoxStyle.width;
      regionBoxElem.style.height = defaultRegionBoxStyle.height;
      regionBoxElem.style.left = "";
      toggleBtn.innerText = "Maximize";
      isRegionBoxMaximized = false;
    }
  });

  const dlBtn = document.getElementById("downloadJsonBtn");
  dlBtn.addEventListener("click", function () {
    const data = JSON.stringify(window.currentFilteredRecords || [], null, 2);
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "filtered_records.json";
    a.click();
    URL.revokeObjectURL(url);
  });
}

/**
 * Update the region box after filtering.
 * This function groups the filtered records by region (lan) using your precomputed index.
 * It then builds the UI for each region – always showing all regions from window.lanList,
 * with a checkbox (whose checked state reflects window.selectedLans), the region name with its count,
 * and an expand button. "Select All" and "Deselect All" buttons are added at the top.
 */
function updateRegionBox(filteredRecords) {
  // Build a lookup for filtered records by id.
  let filteredRecordsById = {};
  let filteredIDs = new Set();
  filteredRecords.forEach(rec => {
    if (rec._id !== undefined) {
      filteredRecordsById[rec._id] = rec;
      filteredIDs.add(rec._id);
    }
  });

  // Group by lan using the precomputed index.
  let regionGroups = {};
  window.lanList.forEach(lan => {
    let lanIDs = window.lanIndex[lan] || [];
    // Even if a region has 0 records, we want to display it.
    let groupIDs = lanIDs.filter(id => filteredIDs.has(id));
    regionGroups[lan] = groupIDs.map(id => filteredRecordsById[id]);
  });

  // Update total count display.
  const totalSpan = document.getElementById("totalRecordCount");
  if (totalSpan) {
    totalSpan.innerText = "Total: " + filteredRecords.length;
  }

  // Build the region box HTML.
  if (!regionBoxContentElem) return;
  let html = "";

  // Add "Select All" / "Deselect All" buttons.
  html += `<div style="margin-bottom:5px;">` +
          `<button id="regionSelectAll">Select All</button> ` +
          `<button id="regionDeselectAll">Deselect All</button>` +
          `</div>`;

  // For each region in your global list, create a summary row.
  window.lanList.forEach(lan => {
    // If there are no records, groupIDs is empty so count is 0.
    const count = (regionGroups[lan] && regionGroups[lan].length) || 0;
    // Build a row with a checkbox, region name (with count), and an expand button.
    html += `<div class="region-summary" style="margin-bottom:5px; border-bottom:1px solid #eee; padding-bottom:5px;">`;
    html += `<label style="display:inline-block;">`;
    const checked = window.selectedLans.has(lan) ? "checked" : "";
    html += `<input type="checkbox" class="region-checkbox" data-region="${lan}" ${checked}> `;
    html += `<b>${lan}</b> (${count} records)`;
    html += `</label> `;
    html += `<button class="expand-btn" data-region="${lan}">+</button>`;
    html += `<div class="region-details" id="region_details_${lan}" style="display:none; height:200px; overflow:auto;"></div>`;
    html += `</div>`;
  });

  regionBoxContentElem.innerHTML = html;

  // Attach event listeners to the region checkboxes.
  const regionCheckboxes = regionBoxContentElem.querySelectorAll(".region-checkbox");
  regionCheckboxes.forEach(cb => {
    cb.addEventListener("change", function () {
      const lan = cb.getAttribute("data-region");
      if (cb.checked) {
        window.selectedLans.add(lan);
      } else {
        window.selectedLans.delete(lan);
      }
      updateHeatmap();
    });
  });

  // Attach event listeners to the "Select All" and "Deselect All" buttons.
  const selectAllBtn = document.getElementById("regionSelectAll");
  const deselectAllBtn = document.getElementById("regionDeselectAll");
  if (selectAllBtn) {
    selectAllBtn.addEventListener("click", function () {
      window.lanList.forEach(lan => window.selectedLans.add(lan));
      updateHeatmap();
      updateRegionBox(filteredRecords);
    });
  }
  if (deselectAllBtn) {
    deselectAllBtn.addEventListener("click", function () {
      // Instead of clearing, we want to keep all rows visible.
      // Clearing window.selectedLans means no region is selected and heatmap will show 0 records.
      // (This is your desired behavior.)
      window.lanList.forEach(lan => window.selectedLans.delete(lan));
      updateHeatmap()
      
      updateRegionBox(filteredRecords);
    });
  }

  // Setup expand/collapse for each region row.
  const expandButtons = regionBoxContentElem.getElementsByClassName("expand-btn");
  [...expandButtons].forEach(btn => {
    btn.addEventListener("click", function () {
      const region = btn.getAttribute("data-region");
      const det = document.getElementById(`region_details_${region}`);
      if (det.style.display === "none") {
        det.style.display = "block";
        btn.innerText = "-";
        det.innerHTML = "";
        const options = { mode: "view", modes: ["tree", "view"] };
        try {
          const editor = new JSONEditor(det, options);
          editor.set(regionGroups[region]);
          $(det).resizable({ handles: "n, e, s, w, ne, se, sw, nw" });
        } catch (err) {
          det.innerHTML = "Error: " + err;
        }
      } else {
        det.style.display = "none";
        btn.innerText = "+";
      }
    });
  });
}
