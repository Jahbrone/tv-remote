const inputButton = document.getElementById("inputButton");
const inputPanel = document.getElementById("inputPanel");
const closeInputPanel = document.getElementById("closeInputPanel");
const keyboardInput = document.getElementById("keyboardInput");
const trackpad = document.getElementById("trackpad");

inputButton.addEventListener("click", () => {
  inputPanel.classList.add("open");
});

closeInputPanel.addEventListener("click", () => {
  inputPanel.classList.remove("open");
});

keyboardInput.addEventListener("input", (event) => {
  console.log("Typed:", event.target.value);
});

trackpad.addEventListener("pointermove", (event) => {
  if (event.buttons === 1) {
    console.log("Trackpad:", event.movementX, event.movementY);
  }
});