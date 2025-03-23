//A Web Worker script that filters records by date, crop, and pest criteria using indexed lookups and set operations, 
//then returns processed, qualifying records for display (e.g. in a heatmap).

self.onmessage = function (e) {
  var data = e.data;
  function intersectSets(a, b) {
    var out = new Set();
    a.forEach(function (x) {
      if (b.has(x)) out.add(x);
    });
    return out;
  }
  function lowerBound(arr, val) {
    var lo = 0, hi = arr.length;
    while (lo < hi) {
      var mid = Math.floor((lo + hi) / 2);
      if (arr[mid][0] < val) lo = mid + 1;
      else hi = mid;
    }
    return lo;
  }
  function upperBound(arr, val) {
    var lo = 0, hi = arr.length;
    while (lo < hi) {
      var mid = Math.floor((lo + hi) / 2);
      if (arr[mid][0] <= val) lo = mid + 1;
      else hi = mid;
    }
    return lo;
  }
  function dateRangeIDs(minEpoch, maxEpoch, dateIndex) {
    var startIdx = lowerBound(dateIndex, minEpoch);
    var endIdx = upperBound(dateIndex, maxEpoch);
    var out = new Set();
    for (var i = startIdx; i < endIdx; i++) {
      out.add(dateIndex[i][1]);
    }
    return out;
  }
  function unionOfGrodas(grodas, grodaIndex) {
    var result = new Set();
    grodas.forEach(function (g) {
      var arr = grodaIndex[g] || [];
      arr.forEach(function (rid) { result.add(rid); });
    });
    return result;
  }
  function unionOfPests(pests, pestIndex) {
    var result = new Set();
    pests.forEach(function (p) {
      var arr = pestIndex[p] || [];
      arr.forEach(function (rid) { result.add(rid); });
    });
    return result;
  }
  function processRecord(record, selectedPests, includeZeroPest, strictPestMode) {
    var result = {
      lan: record.lan,
      groda: record.groda,
      lat_wgs84: record.lat_wgs84,
      lon_wgs84: record.lon_wgs84,
      graderingstillfalleList: []
    };
    var qualifies = (selectedPests.size === 0);
    var foundNonZero = false;
    if (record.graderingstillfalleList) {
      for (var i = 0; i < record.graderingstillfalleList.length; i++) {
        var entry = record.graderingstillfalleList[i];
        var newEntry = {};
        if (entry.graderingList) {
          newEntry.graderingList = [];
          for (var j = 0; j < entry.graderingList.length; j++) {
            var grade = entry.graderingList[j];
            var pestOk = strictPestMode ? selectedPests.has(grade.skadegorare) : true;
            var nonZeroOk = includeZeroPest ? true : (parseFloat(grade.varde) > 0);
            if (pestOk && nonZeroOk) {
              newEntry.graderingList.push(grade);
              if (selectedPests.size > 0 && selectedPests.has(grade.skadegorare)) {
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
    if (selectedPests.size > 0 && !qualifies) return null;
    if (!includeZeroPest && !foundNonZero) return null;
    var pestSet = new Set();
    for (var i = 0; i < result.graderingstillfalleList.length; i++) {
      var entry = result.graderingstillfalleList[i];
      if (entry.graderingList) {
        for (var j = 0; j < entry.graderingList.length; j++) {
          var grade = entry.graderingList[j];
          if (grade.skadegorare) {
            pestSet.add(grade.skadegorare);
          }
        }
      }
    }
    result.pests = Array.from(pestSet);
    return result;
  }
  function recordQualifies(record, selectedPests, includeZeroPest) {
    var gList = record.graderingstillfalleList;
    if (!gList) return false;
    var filterBySelected = selectedPests.size > 0;
    var foundSelectedGrade = false;
    var foundSelectedNonZero = false;
    for (var i = 0; i < gList.length; i++) {
      var entry = gList[i];
      if (!entry.graderingList) continue;
      var relevantGrades = filterBySelected
        ? entry.graderingList.filter(function (grade) { return selectedPests.has(grade.skadegorare); })
        : entry.graderingList;
      if (relevantGrades.length === 0) continue;
      foundSelectedGrade = true;
      for (var j = 0; j < relevantGrades.length; j++) {
        var grade = relevantGrades[j];
        var val = parseFloat(grade.varde) || 0;
        if (val > 0) {
          foundSelectedNonZero = true;
        }
      }
    }
    if (!includeZeroPest && !foundSelectedNonZero) return false;
    if (filterBySelected && !foundSelectedGrade) return false;
    return true;
  }
  
  var dateSet = dateRangeIDs(data.selectedMinDate, data.selectedMaxDate, data.dateIndex);
  var grodaSet = unionOfGrodas(data.selectedGrodas, data.grodaIndex);
  var pestSet = unionOfPests(data.selectedPests, data.pestIndex);
  var finalSet = intersectSets(dateSet, grodaSet);
  finalSet = intersectSets(finalSet, pestSet);
  var finalRecords = [];
  finalSet.forEach(function (rid) {
    var originalRec = data.idToRecord[rid];
    if (originalRec) {
      var processedRec = processRecord(originalRec, data.selectedPestsSet, data.includeZeroPest, data.strictPestMode);
      if (processedRec && recordQualifies(processedRec, data.selectedPestsSet, data.includeZeroPest)) {
        processedRec._id = rid;
        finalRecords.push(processedRec);
      }
    }
  });
  self.postMessage({ finalRecords: finalRecords });
};
