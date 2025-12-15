// Get references to DOM elements
const fileInput = document.getElementById("fileInput");
const uploadSection = document.getElementById("uploadSection");
const previewSection = document.getElementById("previewSection");
const coinSection = document.getElementById("coinSection");
const resultSection = document.getElementById("resultSection");
const resetBtn = document.getElementById("resetBtn");
const billImage = document.getElementById("billImage");
const detectBox = document.getElementById("detectBox");
const billValueText = document.getElementById("billValue");
const calculateBtn = document.getElementById("calculateBtn");

// Variables to store detected bill and selected coins
let detectedBill = 0;
let selectedCoins = [];

// Handle file upload
fileInput.addEventListener("change", () => {
  const file = fileInput.files[0]; // Get the selected file
  if (!file) return; // Exit if no file selected

  const reader = new FileReader();
  reader.onload = e => {
    billImage.src = e.target.result; // Display uploaded image
    uploadSection.classList.add("hidden"); // Hide upload section
    previewSection.classList.remove("hidden"); // Show preview section

    // Simulate bill detection after a short delay
    setTimeout(detectBill, 1200);
  };
  reader.readAsDataURL(file); // Read file as data URL
});

// Simulate bill detection
function detectBill() {
  const bills = [20, 50, 100, 200, 500, 1000]; // Possible bill denominations
  detectedBill = bills[Math.floor(Math.random() * bills.length)]; // Randomly select a bill

  detectBox.classList.add("detected"); // Highlight detection box
  detectBox.innerText = `₱${detectedBill}`; // Show detected bill in box
  billValueText.innerText = `₱${detectedBill}`; // Update coin section text

  coinSection.classList.remove("hidden"); // Show coin selection section
}

// Handle coin selection
document.querySelectorAll(".coin").forEach(btn => {
  btn.addEventListener("click", () => {
    const value = parseInt(btn.dataset.value); // Get coin value from data attribute

    if (selectedCoins.includes(value)) {
      // Deselect coin if already selected
      selectedCoins = selectedCoins.filter(v => v !== value);
      btn.classList.remove("selected");
    } else {
      // Select coin
      selectedCoins.push(value);
      btn.classList.add("selected");
    }

    // Enable/disable calculate button based on selection
    calculateBtn.disabled = selectedCoins.length === 0;
  });
});

// Calculate coin breakdown
calculateBtn.addEventListener("click", () => {
  let remaining = detectedBill; // Remaining amount to break down
  let result = {}; // Object to store coin counts
  selectedCoins.sort((a, b) => b - a); // Sort coins descending

  // First pass: distribute coins from largest to smallest
  while (remaining > 0) {
    let used = false; // Track if any coin was used in this pass
    for (let coin of selectedCoins) {
      if (remaining >= coin) {
        result[coin] = (result[coin] || 0) + 1; // Increment coin count
        remaining -= coin; // Subtract coin from remaining
        used = true;
      }
    }
    if (!used) break; // Stop if no coin can be used
  }

  // Build HTML to display results
  let html = "<h3>DISPENSED COINS</h3>";
  Object.keys(result).forEach(coin => {
    html += `<div class="result-item">${result[coin]} × ₱${coin}</div>`;
  });

  // Show remainder if any
  if (remaining > 0) {
    html += `<div class="result-item">REMAINDER: ₱${remaining}</div>`;
  }

  resultSection.innerHTML = html; // Update result section
  resultSection.classList.remove("hidden"); // Show results
  resetBtn.classList.remove("hidden"); // Show reset button
});

// Reset the application
resetBtn.addEventListener("click", () => location.reload());
