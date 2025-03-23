//Implements a draggable, resizable “Region Box” UI to view, expand, filter, and download records by region (län), syncing interactively with the heatmap and global state.
console.log("region_box.js loaded.");

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

function initRegionBox() {
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

  regionBoxContentElem = document.createElement("div");
  regionBoxContentElem.id = "regionBoxContent";
  regionBoxElem.appendChild(regionBoxContentElem);

  $(() => {
    $("#regionBox").draggable({ handle: "#regionBoxHeader" });
    $("#regionBox").resizable();
  });

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


function updateRegionBox(filteredRecords) {
  let filteredRecordsById = {};
  let filteredIDs = new Set();
  filteredRecords.forEach(rec => {
    if (rec._id !== undefined) {
      filteredRecordsById[rec._id] = rec;
      filteredIDs.add(rec._id);
    }
  });

  let regionGroups = {};
  window.lanList.forEach(lan => {
    let lanIDs = window.lanIndex[lan] || [];
    let groupIDs = lanIDs.filter(id => filteredIDs.has(id));
    regionGroups[lan] = groupIDs.map(id => filteredRecordsById[id]);
  });

  const totalSpan = document.getElementById("totalRecordCount");
  if (totalSpan) {
    totalSpan.innerText = "Total: " + filteredRecords.length;
  }

  if (!regionBoxContentElem) return;
  let html = "";

  html += `<div style="margin-bottom:5px;">` +
          `<button id="regionSelectAll">Select All</button> ` +
          `<button id="regionDeselectAll">Deselect All</button>` +
          `</div>`;

  window.lanList.forEach(lan => {
    const count = (regionGroups[lan] && regionGroups[lan].length) || 0;
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
      window.lanList.forEach(lan => window.selectedLans.delete(lan));
      updateHeatmap()
      
      updateRegionBox(filteredRecords);
    });
  }

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
