//Handles filtering logic, spatial interaction, and heatmap rendering based on user-selected crops, 
//pests, dates, and regions, updating the map and UI in real-time as filters change.
console.log("main_logic.js loaded.");

window.currentFilteredRecords = window.currentFilteredRecords || [];

document.addEventListener("DOMContentLoaded", function () {
  console.log("DOMContentLoaded in main_logic");
  initRegionBox();   
  attachMapEvents(); 
});


function filterRecord(record) {
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
          const pestOk = window.strictPestMode ? window.selectedPests.has(grade.skadegorare) : true;
          const nonZeroOk = window.includeZeroPest ? true : (parseFloat(grade.varde) > 0);
          return pestOk && nonZeroOk;
        });
      }
      newRecord.graderingstillfalleList.push(newEntry);
    }
  }

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
  const result = {
    lan: record.lan,
    groda: record.groda,
    lat_wgs84: record.lat_wgs84,
    lon_wgs84: record.lon_wgs84,
    graderingstillfalleList: []
  };
  let qualifies = (window.selectedPests.size === 0); 
  let foundNonZero = false;
  
  if (record.graderingstillfalleList) {
    for (const entry of record.graderingstillfalleList) {
      const newEntry = {};
      if (entry.graderingList) {
        newEntry.graderingList = [];
        for (const grade of entry.graderingList) {
          const pestOk = window.strictPestMode ? window.selectedPests.has(grade.skadegorare) : true;
          const nonZeroOk = window.includeZeroPest ? true : (parseFloat(grade.varde) > 0);
          if (pestOk && nonZeroOk) {
            newEntry.graderingList.push(grade);
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
  
  if (window.selectedPests.size > 0 && !qualifies) return null;
  if (!window.includeZeroPest && !foundNonZero) return null;
  
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

  const filterBySelected = window.selectedPests.size > 0;
  let foundSelectedGrade = false;
  let foundSelectedNonZero = false;

  for (let entry of gList) {
    if (!entry.graderingList) continue;
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

  if (!window.includeZeroPest && !foundSelectedNonZero) return false;
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

function recordQualifiesUnderZero(record) {
  const gList = record.graderingstillfalleList;
  if (!gList) return false;

  let foundAnyGrade = false;  
  let foundNonZero   = false;  

  for (let entry of gList) {
    if (!entry.graderingList) continue;
    const filteredGrades = window.strictPestMode
      ? entry.graderingList.filter(grade => window.selectedPests.has(grade.skadegorare))
      : entry.graderingList;
    
    if (filteredGrades.length === 0) continue; 
    
    foundAnyGrade = true;
    for (let grade of filteredGrades) {
      const val = parseFloat(grade.varde) || 0;
      if (val > 0) {
        foundNonZero = true;
      }
    }
  }

  if (!window.includeZeroPest && !foundNonZero) return false;
  if (window.selectedPests.size > 0 && !foundAnyGrade) return false;

  return true;
}



function updateHeatmap() {
  if (!window.map) {
    console.log("No map found in updateHeatmap.");
    return;
  }

  const dateSet = dateRangeIDs(window.selectedMinDate, window.selectedMaxDate);

  const grodaArr = Array.from(window.selectedGrodas);
  const grodaSet = unionOfGrodas(grodaArr);

  const pestArr = Array.from(window.selectedPests);
  let pestSet;

  pestSet = unionOfPests(pestArr);


  let finalSet = intersectSets(dateSet, grodaSet);
  finalSet = intersectSets(finalSet, pestSet);

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
        processedRec._id = rid;
        finalRecords.push(processedRec);
      }
    }
  }
if (window.selectedLans) {
  if (window.selectedLans.size > 0) {
    finalRecords = finalRecords.filter(rec => window.selectedLans.has(rec.lan));
  } else {
    finalRecords = []; 
  }
}

  window.currentFilteredRecords = finalRecords;

  
  const newPoints = finalRecords.map(r => [parseFloat(r.lat_wgs84), parseFloat(r.lon_wgs84)]);

  window.map.eachLayer(layer => {
    if (layer.options && layer.options.radius === 8 && layer.options.maxZoom === 13) {
      window.map.removeLayer(layer);
    }
  });

  window.dynamicHeatmap = L.heatLayer(newPoints, {
    radius: 8,
    maxZoom: 13,
    minOpacity: 0.5,
    blur: 15
  }).addTo(window.map);

  console.log("Heatmap updated. #points = ", newPoints.length);

  updateRegionBox(finalRecords);

  updateGrodaCounts();
  updatePestCounts();

  rebuildGrodaCheckboxes();
  rebuildPestCheckboxes();
}



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
