console.log("main_logic.js loaded.");

// currentFilteredRecords will hold the final array of record objects
window.currentFilteredRecords = window.currentFilteredRecords || [];

document.addEventListener("DOMContentLoaded", function () {
  console.log("DOMContentLoaded in main_logic");
  initRegionBox();   
  attachMapEvents(); 
});

/* 
  HELPER SET FUNCTIONS, BINARY SEARCH, ETC.
  ----------------------------------------
*/

function filterRecord(record) {
  // Create a new object with only needed properties.
  const newRecord = {
    lan: record.lan,
    groda: record.groda,
    lat_wgs84: record.lat_wgs84,
    lon_wgs84: record.lon_wgs84,
    graderingstillfalleList: []
  };

  if (record.graderingstillfalleList) {
    for (const entry of record.graderingstillfalleList) {
      const newEntry = Object.assign({}, entry);
      if (entry.graderingList) {
        newEntry.graderingList = entry.graderingList.filter(grade => {
          // Only keep the grade if:
          // - In strict mode, its pest is selected (or not in strict mode, all are kept)
          // - And if includeZeroPest is off, the grade's value is > 0.
          const pestOk = window.strictPestMode ? window.selectedPests.has(grade.skadegorare) : true;
          const nonZeroOk = window.includeZeroPest ? true : (parseFloat(grade.varde) > 0);
          return pestOk && nonZeroOk;
        });
      }
      newRecord.graderingstillfalleList.push(newEntry);
    }
  }

  // Recompute pests based on the filtered grades.
  let newPests = new Set();
  if (newRecord.graderingstillfalleList) {
    for (const entry of newRecord.graderingstillfalleList) {
      if (entry.graderingList) {
        for (const grade of entry.graderingList) {
          if (grade.skadegorare) {
            newPests.add(grade.skadegorare);
          }
        }
      }
    }
  }
  newRecord.pests = Array.from(newPests);
  return newRecord;
}


function processRecord(record) {
  // Build a minimal filtered record with only the needed properties.
  const result = {
    lan: record.lan,
    groda: record.groda,
    lat_wgs84: record.lat_wgs84,
    lon_wgs84: record.lon_wgs84,
    graderingstillfalleList: []
  };
  let qualifies = (window.selectedPests.size === 0); // if no pests selected, we default to true
  let foundNonZero = false;
  
  if (record.graderingstillfalleList) {
    for (const entry of record.graderingstillfalleList) {
      // Create a new entry and process its graderings.
      const newEntry = {};
      if (entry.graderingList) {
        newEntry.graderingList = [];
        for (const grade of entry.graderingList) {
          // Check if we keep this grade.
          const pestOk = window.strictPestMode ? window.selectedPests.has(grade.skadegorare) : true;
          const nonZeroOk = window.includeZeroPest ? true : (parseFloat(grade.varde) > 0);
          if (pestOk && nonZeroOk) {
            newEntry.graderingList.push(grade);
            // In non-strict mode but with some pests selected, require that at least one grade is for a selected pest.
            if (window.selectedPests.size > 0 && window.selectedPests.has(grade.skadegorare)) {
              qualifies = true;
            }
            if (parseFloat(grade.varde) > 0) {
              foundNonZero = true;
            }
          }
        }
      }
      result.graderingstillfalleList.push(newEntry);
    }
  }
  
  // If pests are selected, ensure at least one selected grade exists.
  if (window.selectedPests.size > 0 && !qualifies) return null;
  // If zero values are excluded, at least one grade must have value > 0.
  if (!window.includeZeroPest && !foundNonZero) return null;
  
  // Recompute the pest list.
  const pestSet = new Set();
  for (const entry of result.graderingstillfalleList) {
    if (entry.graderingList) {
      for (const grade of entry.graderingList) {
        if (grade.skadegorare) {
          pestSet.add(grade.skadegorare);
        }
      }
    }
  }
  result.pests = Array.from(pestSet);
  return result;
}


function recordQualifies(record) {
  const gList = record.graderingstillfalleList;
  if (!gList) return false;

  // Always filter grades if any pests are selected.
  const filterBySelected = window.selectedPests.size > 0;
  let foundSelectedGrade = false;
  let foundSelectedNonZero = false;

  for (let entry of gList) {
    if (!entry.graderingList) continue;
    // Always keep only the grades for selected pests if any are selected.
    const relevantGrades = filterBySelected
      ? entry.graderingList.filter(grade => window.selectedPests.has(grade.skadegorare))
      : entry.graderingList;
    
    if (relevantGrades.length === 0) continue;
    foundSelectedGrade = true;
    for (let grade of relevantGrades) {
      const val = parseFloat(grade.varde) || 0;
      if (val > 0) {
        foundSelectedNonZero = true;
      }
    }
  }

  // If we are excluding zero values, then we require at least one selected grade with a nonzero value.
  if (!window.includeZeroPest && !foundSelectedNonZero) return false;
  // And if any pests are selected, we must find at least one grade corresponding to a selected pest.
  if (filterBySelected && !foundSelectedGrade) return false;
  
  return true;
}


function intersectSets(a, b) {
  const out = new Set();
  for (const x of a) {
    if (b.has(x)) out.add(x);
  }
  return out;
}
function lowerBound(arr, val) {
  let lo = 0, hi = arr.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (arr[mid][0] < val) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}
function upperBound(arr, val) {
  let lo = 0, hi = arr.length;
  while (lo < hi) {
    const mid = (lo + hi) >> 1;
    if (arr[mid][0] <= val) lo = mid + 1;
    else hi = mid;
  }
  return lo;
}
function dateRangeIDs(minEpoch, maxEpoch) {
  // window.dateIndex is sorted [ [epoch, rid], ...]
  const startIdx = lowerBound(window.dateIndex, minEpoch);
  const endIdx   = upperBound(window.dateIndex, maxEpoch);
  const out = new Set();
  for (let i = startIdx; i < endIdx; i++) {
    const rid = window.dateIndex[i][1];
    out.add(rid);
  }
  return out;
}
function unionOfGrodas(grodas) {
  const result = new Set();
  grodas.forEach(g => {
    const arr = window.grodaIndex[g] || [];
    arr.forEach(rid => result.add(rid));
  });
  return result;
}
function unionOfPests(pests) {
  const result = new Set();
  pests.forEach(p => {
    const arr = window.pestIndex[p] || [];
    arr.forEach(rid => result.add(rid));
  });
  return result;
}
function intersectionOfPests(pests) {
  if (pests.length === 0) {
    // Some prefer returning "all possible" instead,
    // but let's keep the old logic: no pests => empty
    return new Set();
  }
  let current = new Set(window.pestIndex[pests[0]] || []);
  for (let i = 1; i < pests.length; i++) {
    const arr = window.pestIndex[pests[i]] || [];
    const s2  = new Set(arr);
    current   = intersectSets(current, s2);
    if (current.size === 0) break;
  }
  return current;
}

//Records that only has graderingar = 0  
function recordQualifiesUnderZero(record) {
  const gList = record.graderingstillfalleList;
  if (!gList) return false;

  let foundAnyGrade = false;  // indicates that at least one grade (for a selected pest in strict mode) was found
  let foundNonZero   = false;  // indicates that at least one such grade has varde > 0

  for (let entry of gList) {
    if (!entry.graderingList) continue;
    // If strict mode is enabled, filter out grades for pests not selected.
    const filteredGrades = window.strictPestMode
      ? entry.graderingList.filter(grade => window.selectedPests.has(grade.skadegorare))
      : entry.graderingList;
    
    if (filteredGrades.length === 0) continue; // this entry has no selected pest measurements
    
    foundAnyGrade = true;
    for (let grade of filteredGrades) {
      const val = parseFloat(grade.varde) || 0;
      if (val > 0) {
        foundNonZero = true;
      }
    }
  }

  // if includeZeroPest is off, we require at least one grade with a nonzero value
  if (!window.includeZeroPest && !foundNonZero) return false;
  // if pests are selected but none appear in the filtered grades, skip this record
  if (window.selectedPests.size > 0 && !foundAnyGrade) return false;

  return true;
}



//--------------------------------------
function updateHeatmap() {
  if (!window.map) {
    console.log("No map found in updateHeatmap.");
    return;
  }

  // 1) date-based set
  const dateSet = dateRangeIDs(window.selectedMinDate, window.selectedMaxDate);

  // 2) union of grodas
  const grodaArr = Array.from(window.selectedGrodas);
  const grodaSet = unionOfGrodas(grodaArr);

  // 3) pests => union or intersection
  const pestArr = Array.from(window.selectedPests);
  let pestSet;

  pestSet = unionOfPests(pestArr);


  // Combine
  let finalSet = intersectSets(dateSet, grodaSet);
  finalSet = intersectSets(finalSet, pestSet);

  // Build initial finalRecords
  let prelimRecords = [];

  let finalRecords = [];

  for (let rid of finalSet) {
    const originalRec = window.idToRecord[String(rid)];

      if (originalRec)
      {
        prelimRecords.push(originalRec);
      }

    if (originalRec) {
      const processedRec = processRecord(originalRec);
      if (processedRec) {
        // Attach id for later use (e.g. in lan grouping)
        processedRec._id = rid;
        finalRecords.push(processedRec);
      }
    }
  }
    // If region filtering is enabled, only keep records from selected regions.
if (window.selectedLans) {
  if (window.selectedLans.size > 0) {
    finalRecords = finalRecords.filter(rec => window.selectedLans.has(rec.lan));
  } else {
    finalRecords = []; // no region selected means no records
  }
}

  window.currentFilteredRecords = finalRecords;

  



  // Build points for the heatmap
  const newPoints = finalRecords.map(r => [parseFloat(r.lat_wgs84), parseFloat(r.lon_wgs84)]);

  // remove old heatmap
  window.map.eachLayer(layer => {
    if (layer.options && layer.options.radius === 8 && layer.options.maxZoom === 13) {
      window.map.removeLayer(layer);
    }
  });

  // add new heatmap
  window.dynamicHeatmap = L.heatLayer(newPoints, {
    radius: 8,
    maxZoom: 13,
    minOpacity: 0.5,
    blur: 15
  }).addTo(window.map);

  console.log("Heatmap updated. #points = ", newPoints.length);

  // Update region box
  updateRegionBox(finalRecords);

  // Update counts (populates window.grodaCounts / pestCounts)
  updateGrodaCounts();
  updatePestCounts();

  // Rebuild filter checkboxes so the displayed counts reflect changes
  rebuildGrodaCheckboxes();
  rebuildPestCheckboxes();
}


/* -------------- Counting -------------- */

function updateGrodaCounts() {
  window.grodaCounts = {};
  window.grodaList.forEach(g => {
    let c = 0;
    for (let rec of window.currentFilteredRecords) {
      if (rec.groda === g) {
        c++;
      }
    }
    window.grodaCounts[g] = c;
    const span = document.getElementById("groda_count_" + g);
    if (span) {
      span.innerText = " (" + c + ")";
    }
  });
}

function getRecordSelectedPests(record) {
  let pests = new Set();
  for (let entry of record.graderingstillfalleList || []) {
    let grades = entry.graderingList || [];
    // In strict mode, only consider grades for pests that are selected.
    if (window.strictPestMode) {
      grades = grades.filter(grade => window.selectedPests.has(grade.skadegorare));
    }
    grades.forEach(grade => {
      if (grade.skadegorare) {
        pests.add(grade.skadegorare);
      }
    });
  }
  return pests;
}

function updatePestCounts() {
  window.pestCounts = {};
  window.pestList.forEach(p => {
    let c = 0;
    for (let rec of window.currentFilteredRecords) {
      const recordPests = window.strictPestMode ? getRecordSelectedPests(rec) : new Set(rec.pests || []);
      if (recordPests.has(p)) {
        c++;
      }
    }
    window.pestCounts[p] = c;
    const span = document.getElementById("pest_count_" + p);
    if (span) {
      span.innerText = " (" + c + ")";
    }
  });
}



/* -------------- Map events -------------- */
let cursorCircle = null;
let fixedCircle  = null;

function attachMapEvents() {
  if (!window.map) {
    return;
  }
  window.map.on("mousemove", onMapMouseMove);
  window.map.on("click", onMapClick);
  console.log("Map events attached in main_logic.");
}

function onMapMouseMove(e) {
  const lat = e.latlng.lat;
  const lng = e.latlng.lng;
  if (!cursorCircle) {
    cursorCircle = L.circle([lat, lng], {
      radius: degreesToMeters(window.spatialThreshold || 0.05),
      color: "blue",
      dashArray: "5,5",
      fill: false
    }).addTo(window.map);
  } else {
    cursorCircle.setLatLng([lat, lng]);
    cursorCircle.setRadius(degreesToMeters(window.spatialThreshold || 0.05));
  }
}

function onMapClick(e) {
  const lat = e.latlng.lat;
  const lng = e.latlng.lng;
  console.log("Map clicked at:", lat, lng);

  if (fixedCircle) {
    window.map.removeLayer(fixedCircle);
  }
  fixedCircle = L.circle([lat, lng], {
    radius: degreesToMeters(window.spatialThreshold || 0.05),
    color: "red",
    dashArray: "5,5",
    fill: false
  }).addTo(window.map);

  const nearby = window.currentFilteredRecords.filter(rec => {
    const rlat = parseFloat(rec.lat_wgs84);
    const rlng = parseFloat(rec.lon_wgs84);
    if (isNaN(rlat) || isNaN(rlng)) return false;
    return (Math.abs(rlat - lat) < (window.spatialThreshold||0.05) &&
            Math.abs(rlng - lng) < (window.spatialThreshold||0.05));
  });
  console.log("Nearby records:", nearby);
}
