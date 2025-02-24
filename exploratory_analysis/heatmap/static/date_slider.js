// date_slider.js
console.log("date_slider.js loaded.");

document.addEventListener("DOMContentLoaded", function () {
  createDateSliderUI();
});

/** 
 * Build the date slider container, the start/end inputs, and the shift buttons.
 */
function createDateSliderUI() {
  const dateSliderContainer = document.createElement("div");
  dateSliderContainer.style.position = "fixed";
  dateSliderContainer.style.bottom = "20px";
  dateSliderContainer.style.left = "50%";
  dateSliderContainer.style.transform = "translateX(-50%)";
  dateSliderContainer.style.width = "80%";
  dateSliderContainer.style.zIndex = 1000;
  dateSliderContainer.style.background = "white";
  dateSliderContainer.style.padding = "10px";
  dateSliderContainer.style.border = "1px solid #ccc";
  document.body.appendChild(dateSliderContainer);

  // We assume `window.minDateEpoch` and `window.maxDateEpoch` are set from main.py
  // We also assume global selectedMinDate, selectedMaxDate exist (you can store them on window)
  window.selectedMinDate = window.minDateEpoch;
  window.selectedMaxDate = window.maxDateEpoch;

  // Make an input container
  const inputContainer = document.createElement("div");
  inputContainer.style.display = "flex";
  inputContainer.style.justifyContent = "space-between";
  inputContainer.style.marginBottom = "5px";

  const startDateInput = document.createElement("input");
  startDateInput.type = "text";
  startDateInput.value = epochToDateString(window.minDateEpoch);
  startDateInput.style.width = "150px";

  const endDateInput = document.createElement("input");
  endDateInput.type = "text";
  endDateInput.value = epochToDateString(window.maxDateEpoch);
  endDateInput.style.width = "150px";

  inputContainer.appendChild(startDateInput);
  inputContainer.appendChild(endDateInput);
  dateSliderContainer.appendChild(inputContainer);

  // The noUiSlider element
  const dateSliderElement = document.createElement("div");
  dateSliderContainer.appendChild(dateSliderElement);

  noUiSlider.create(dateSliderElement, {
    start: [window.minDateEpoch, window.maxDateEpoch],
    connect: true,
    tooltips: [
      {
        to: (val) => epochToDateString(val),
        from: (str) => dateStringToEpoch(str),
      },
      {
        to: (val) => epochToDateString(val),
        from: (str) => dateStringToEpoch(str),
      },
    ],
    range: {
      min: window.minDateEpoch,
      max: window.maxDateEpoch,
    },
    format: {
      to: (val) => parseInt(val),
      from: (val) => Number(val),
    },
  });

  dateSliderElement.noUiSlider.on("update", function (values, handle) {
    window.selectedMinDate = parseInt(values[0]);
    window.selectedMaxDate = parseInt(values[1]);
    startDateInput.value = epochToDateString(window.selectedMinDate);
    endDateInput.value = epochToDateString(window.selectedMaxDate);
    updateHeatmap();
  });

  startDateInput.addEventListener("change", function () {
    let typedEpoch = dateStringToEpoch(startDateInput.value);
    typedEpoch = Math.max(typedEpoch, window.minDateEpoch);
    typedEpoch = Math.min(typedEpoch, window.maxDateEpoch);
    let upperVal = parseInt(dateSliderElement.noUiSlider.get()[1]);
    dateSliderElement.noUiSlider.set([typedEpoch, upperVal]);
  });

  endDateInput.addEventListener("change", function () {
    let typedEpoch = dateStringToEpoch(endDateInput.value);
    typedEpoch = Math.max(typedEpoch, window.minDateEpoch);
    typedEpoch = Math.min(typedEpoch, window.maxDateEpoch);
    let lowerVal = parseInt(dateSliderElement.noUiSlider.get()[0]);
    dateSliderElement.noUiSlider.set([lowerVal, typedEpoch]);
  });

  // SHIFT buttons
  const shiftContainer = document.createElement("div");
  shiftContainer.style.textAlign = "center";
  shiftContainer.style.marginTop = "10px";

  const periodOptions = ["Day", "Week", "Year"];
  const periodOffsets = {
    Day: 86400000,
    Week: 604800000,
    Year: 31536000000,
  };
  let selectedPeriod = "Day";

  const periodContainer = document.createElement("div");
  periodContainer.style.marginBottom = "5px";

  periodOptions.forEach((opt) => {
    const btn = document.createElement("button");
    btn.innerText = opt;
    btn.style.margin = "0 5px";
    btn.id = "period_btn_" + opt;
    btn.addEventListener("click", function () {
      selectedPeriod = opt;
      periodOptions.forEach((o) => {
        const b = document.getElementById("period_btn_" + o);
        if (b) {
          b.style.fontWeight = o === selectedPeriod ? "bold" : "normal";
        }
      });
    });
    if (opt === selectedPeriod) {
      btn.style.fontWeight = "bold";
    }
    periodContainer.appendChild(btn);
  });
  shiftContainer.appendChild(periodContainer);

  // - button
  const minusBtn = document.createElement("button");
  minusBtn.innerText = "-";
  minusBtn.style.backgroundColor = "red";
  minusBtn.style.color = "white";
  minusBtn.style.margin = "0 10px";
  minusBtn.addEventListener("click", function () {
    const currentValues = dateSliderElement.noUiSlider.get();
    const offset = periodOffsets[selectedPeriod];
    let newLower = parseInt(currentValues[0]) - offset;
    let newUpper = parseInt(currentValues[1]) - offset;
    if (newLower < window.minDateEpoch) newLower = window.minDateEpoch;
    if (newUpper < newLower) newUpper = newLower;
    dateSliderElement.noUiSlider.set([newLower, newUpper]);
  });
  shiftContainer.appendChild(minusBtn);

  // + button
  const plusBtn = document.createElement("button");
  plusBtn.innerText = "+";
  plusBtn.style.backgroundColor = "green";
  plusBtn.style.color = "white";
  plusBtn.style.margin = "0 10px";
  plusBtn.addEventListener("click", function () {
    const currentValues = dateSliderElement.noUiSlider.get();
    const offset = periodOffsets[selectedPeriod];
    let newLower = parseInt(currentValues[0]) + offset;
    let newUpper = parseInt(currentValues[1]) + offset;
    if (newUpper > window.maxDateEpoch) newUpper = window.maxDateEpoch;
    if (newLower > newUpper) newLower = newUpper;
    dateSliderElement.noUiSlider.set([newLower, newUpper]);
  });
  shiftContainer.appendChild(plusBtn);

  dateSliderContainer.appendChild(shiftContainer);
}
