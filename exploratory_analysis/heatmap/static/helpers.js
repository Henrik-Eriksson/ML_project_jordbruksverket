// helpers.js
console.log("helpers.js loaded.");

function epochToDateString(epoch) {
  const d = new Date(epoch);
  let month = "" + (d.getMonth() + 1);
  let day   = "" + d.getDate();
  let year  = d.getFullYear();
  if (month.length < 2) month = "0" + month;
  if (day.length < 2)   day   = "0" + day;
  return [year, month, day].join("-");
}

function dateStringToEpoch(dstr) {
  const parts = dstr.split("-");
  if (parts.length !== 3) return 0;
  const year  = parseInt(parts[0], 10);
  const month = parseInt(parts[1], 10) - 1;
  const day   = parseInt(parts[2], 10);
  return new Date(year, month, day).getTime();
}

function degreesToMeters(deg) {
  return deg * 111320;
}

function anySelectedPestHasValueAboveZero(record) {
  if (!record.graderingstillfalleList) return false;
  for (let entry of record.graderingstillfalleList) {
    if (!entry.graderingList) continue;
    for (let grade of entry.graderingList) {
      const pestName = grade.skadegorare;
      if (!pestName) continue;
      if (window.selectedPests.has(pestName)) {
        const val = parseFloat(grade.varde) || 0;
        if (val > 0) {
          return true;
        }
      }
    }
  }
  return false;
}
