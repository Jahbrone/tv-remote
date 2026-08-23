const inputButton = document.getElementById("inputButton");
const inputPanel = document.getElementById("inputPanel");
const closeInputPanel = document.getElementById("closeInputPanel");
const keyboardInput = document.getElementById("keyboardInput");
const trackpad = document.getElementById("trackpad");

// Log all command buttons
const commandButtons = document.querySelectorAll("[data-command]");

commandButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const command = button.dataset.command;
    console.log(`Command: ${command}`);
  });
});

// Open keyboard + trackpad panel
inputButton.addEventListener("click", () => {
  inputPanel.classList.add("open");
});

// Close panel
closeInputPanel.addEventListener("click", () => {
  inputPanel.classList.remove("open");
});

// Keyboard test
keyboardInput.addEventListener("input", (event) => {
  console.log("Keyboard:", event.target.value);
});

// Trackpad movement only
let lastX = null;
let lastY = null;

trackpad.addEventListener("pointerdown", (event) => {
  lastX = event.clientX;
  lastY = event.clientY;

  trackpad.setPointerCapture(event.pointerId);
});

trackpad.addEventListener("pointermove", (event) => {
  if (lastX === null || lastY === null) return;

  const deltaX = event.clientX - lastX;
  const deltaY = event.clientY - lastY;

  console.log("Mouse move:", deltaX, deltaY);

  lastX = event.clientX;
  lastY = event.clientY;
});

trackpad.addEventListener("pointerup", (event) => {
  lastX = null;
  lastY = null;

  trackpad.releasePointerCapture(event.pointerId);
});