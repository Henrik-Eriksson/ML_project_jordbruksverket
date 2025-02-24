console.log("filters.js loaded.");

document.addEventListener("DOMContentLoaded", function () {
  window.selectedGrodas = new Set(window.grodaList || []);
  window.selectedPests = new Set(window.pestList || []);
  window.includeZeroPest = false;
  window.strictPestMode = false;

  // We'll store user-chosen sort mode here:
  window.grodaSortMode = "nameAsc"; 
  window.pestSortMode  = "nameAsc";

  createGrodaFilterUI();
  createPestFilterUI();
});

// ==================== G R O D A ====================
function createGrodaFilterUI() {
  const grodaContainer = document.createElement("div");
  grodaContainer.style.position = "fixed";
  grodaContainer.style.bottom = "200px";
  grodaContainer.style.left = "10px";
  grodaContainer.style.width = "220px";
  grodaContainer.style.zIndex = 1000;
  grodaContainer.style.background = "white";
  grodaContainer.style.padding = "10px";
  grodaContainer.style.border = "1px solid #ccc";
  grodaContainer.style.maxHeight = "220px";
  grodaContainer.style.overflowY = "auto";

  const title = document.createElement("div");
  title.innerHTML = "<b>Groda Filter</b>";
  title.style.marginBottom = "5px";
  grodaContainer.appendChild(title);

  // Sort mode select
  const grodaSortSelect = document.createElement("select");
  const grodaSortOptions = [
    { value: "nameAsc",  label: "Name Asc" },
    { value: "nameDesc", label: "Name Desc" },
    { value: "countAsc", label: "Count Asc" },
    { value: "countDesc",label: "Count Desc" }
  ];
  grodaSortOptions.forEach(opt => {
    const o = document.createElement("option");
    o.value = opt.value;
    o.textContent = opt.label;
    grodaSortSelect.appendChild(o);
  });
  grodaSortSelect.value = window.grodaSortMode;
  grodaSortSelect.addEventListener("change", function () {
    window.grodaSortMode = grodaSortSelect.value;
    rebuildGrodaCheckboxes();
  });
  grodaContainer.appendChild(grodaSortSelect);

  // row of select/deselect
  const selAllBtn = document.createElement("button");
  selAllBtn.innerText = "Select All";
  selAllBtn.style.marginRight = "5px";
  selAllBtn.addEventListener("click", function () {
    window.selectedGrodas = new Set(window.grodaList);
    // Recompute
    updateHeatmap();
    // Now we have new currentFilteredRecords => update counts & checkboxes
    //updateGrodaCounts();
    //updatePestCounts();
    rebuildGrodaCheckboxes();
    rebuildPestCheckboxes();
  });
  grodaContainer.appendChild(selAllBtn);

  const desAllBtn = document.createElement("button");
  desAllBtn.innerText = "Deselect All";
  desAllBtn.addEventListener("click", function () {
    window.selectedGrodas = new Set();
    // Recompute
    updateHeatmap();
    //updateGrodaCounts();
    //updatePestCounts();
    rebuildGrodaCheckboxes();
    rebuildPestCheckboxes();
  });
  grodaContainer.appendChild(desAllBtn);

  // container for the actual checkboxes
  const grodaListDiv = document.createElement("div");
  grodaListDiv.id = "grodaListDiv";
  grodaListDiv.style.marginTop = "10px";
  grodaContainer.appendChild(grodaListDiv);

  document.body.appendChild(grodaContainer);

  // Build them initially
  rebuildGrodaCheckboxes();
}

function rebuildGrodaCheckboxes() {
  const container = document.getElementById("grodaListDiv");
  if (!container) return;
  container.innerHTML = "";

  // gather items
  const items = window.grodaList.map(g => {
    const isSelected = window.selectedGrodas.has(g);
    const c = window.grodaCounts[g] || 0; // after updateGrodaCounts
    return { name: g, checked: isSelected, count: c };
  });

  // sort
  items.sort((a, b) => {
    switch (window.grodaSortMode) {
      case "nameAsc":  return a.name.localeCompare(b.name);
      case "nameDesc": return b.name.localeCompare(a.name);
      case "countAsc": return a.count - b.count;
      case "countDesc":return b.count - a.count;
      default:         return a.name.localeCompare(b.name);
    }
  });

  items.forEach(obj => {
    const label = document.createElement("label");
    label.style.display = "block";
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = obj.checked;
    cb.addEventListener("change", function() {
      if (cb.checked) window.selectedGrodas.add(obj.name);
      else window.selectedGrodas.delete(obj.name);

      updateHeatmap();
      //updateGrodaCounts();
      //updatePestCounts();
      rebuildGrodaCheckboxes();
      rebuildPestCheckboxes();
    });
    label.appendChild(cb);

    label.appendChild(document.createTextNode(" " + obj.name + " (" + obj.count + ")"));
    container.appendChild(label);
  });
}

// ==================== P E S T ====================
function createPestFilterUI() {
  const pestContainer = document.createElement("div");
  pestContainer.style.position = "fixed";
  pestContainer.style.bottom = "200px";
  pestContainer.style.left = "240px";
  pestContainer.style.width = "220px";
  pestContainer.style.zIndex = 1000;
  pestContainer.style.background = "white";
  pestContainer.style.padding = "10px";
  pestContainer.style.border = "1px solid #ccc";
  pestContainer.style.maxHeight = "220px";
  pestContainer.style.overflowY = "auto";

  const pestTitle = document.createElement("div");
  pestTitle.innerHTML = "<b>Pest Filter</b>";
  pestTitle.style.marginBottom = "5px";
  pestContainer.appendChild(pestTitle);

  // Strict Pest Mode
  const strictDiv = document.createElement("div");
  strictDiv.style.marginBottom = "5px";
  const strictCb = document.createElement("input");
  strictCb.type = "checkbox";
  strictCb.id = "strict_pest_cb";
  strictCb.checked = false;
  strictCb.addEventListener("change", function () {
    window.strictPestMode = strictCb.checked;
    updateHeatmap(); 
    //updateGrodaCounts();
    //updatePestCounts();
    rebuildGrodaCheckboxes();
    rebuildPestCheckboxes();
  });
  strictDiv.appendChild(strictCb);
  strictDiv.appendChild(document.createTextNode(" Strict Pest Mode"));
  pestContainer.appendChild(strictDiv);

  // Include pest=0
  const zeroDiv = document.createElement("div");
  zeroDiv.style.marginBottom = "5px";
  const zeroCb = document.createElement("input");
  zeroCb.type = "checkbox";
  zeroCb.id = "pest_zero_cb";
  zeroCb.checked = false;
  zeroCb.addEventListener("change", function () {
    window.includeZeroPest = zeroCb.checked;
    updateHeatmap(); 
    //updateGrodaCounts();
    //updatePestCounts();
    rebuildGrodaCheckboxes();
    rebuildPestCheckboxes();
  });
  zeroDiv.appendChild(zeroCb);
  zeroDiv.appendChild(document.createTextNode(" Include pest value = 0"));
  pestContainer.appendChild(zeroDiv);

  // Sorting select
  const pestSortSelect = document.createElement("select");
  const pestSortOptions = [
    { value: "nameAsc",  label: "Name Asc" },
    { value: "nameDesc", label: "Name Desc" },
    { value: "countAsc", label: "Count Asc" },
    { value: "countDesc",label: "Count Desc" }
  ];
  pestSortOptions.forEach(opt => {
    const o = document.createElement("option");
    o.value = opt.value;
    o.textContent = opt.label;
    pestSortSelect.appendChild(o);
  });
  pestSortSelect.value = window.pestSortMode;
  pestSortSelect.addEventListener("change", function() {
    window.pestSortMode = pestSortSelect.value;
    rebuildPestCheckboxes();
  });
  pestContainer.appendChild(pestSortSelect);

  // row of select/deselect
  const pestSelAll = document.createElement("button");
  pestSelAll.innerText = "Select All";
  pestSelAll.style.marginRight = "5px";
  pestSelAll.addEventListener("click", function () {
    window.selectedPests = new Set(window.pestList);
    updateHeatmap();
    //updateGrodaCounts();
    //updatePestCounts();
    rebuildGrodaCheckboxes();
    rebuildPestCheckboxes();
  });
  pestContainer.appendChild(pestSelAll);

  const pestDesAll = document.createElement("button");
  pestDesAll.innerText = "Deselect All";
  pestDesAll.addEventListener("click", function () {
    window.selectedPests = new Set();
    updateHeatmap();
    //updateGrodaCounts();
    //updatePestCounts();
    rebuildGrodaCheckboxes();
    rebuildPestCheckboxes();
  });
  pestContainer.appendChild(pestDesAll);

  const pestListDiv = document.createElement("div");
  pestListDiv.id = "pestListDiv";
  pestListDiv.style.marginTop = "10px";
  pestContainer.appendChild(pestListDiv);

  document.body.appendChild(pestContainer);

  rebuildPestCheckboxes();
}

function rebuildPestCheckboxes() {
  const container = document.getElementById("pestListDiv");
  if (!container) return;
  container.innerHTML = "";

  const items = window.pestList.map(p => {
    const isSelected = window.selectedPests.has(p);
    const c = window.pestCounts[p] || 0;
    return { name: p, checked: isSelected, count: c };
  });

  switch (window.pestSortMode) {
    case "nameAsc":
      items.sort((a, b) => a.name.localeCompare(b.name));
      break;
    case "nameDesc":
      items.sort((a, b) => b.name.localeCompare(a.name));
      break;
    case "countAsc":
      items.sort((a, b) => a.count - b.count);
      break;
    case "countDesc":
      items.sort((a, b) => b.count - a.count);
      break;
    default:
      items.sort((a, b) => a.name.localeCompare(b.name));
  }

  items.forEach(obj => {
    const label = document.createElement("label");
    label.style.display = "block";

    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = obj.checked;
    cb.addEventListener("change", function() {
      if (cb.checked) window.selectedPests.add(obj.name);
      else window.selectedPests.delete(obj.name);
      updateHeatmap();
      //updateGrodaCounts();
      //updatePestCounts();
      rebuildGrodaCheckboxes();
      rebuildPestCheckboxes();
    });
    label.appendChild(cb);

    label.appendChild(document.createTextNode(" " + obj.name + " (" + obj.count + ")"));
    container.appendChild(label);
  });
}
