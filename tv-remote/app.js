const SERVER_URL = "http://localhost:8765";

const inputButton = document.getElementById("inputButton");
const inputPanel = document.getElementById("inputPanel");
const closeInputPanel = document.getElementById("closeInputPanel");
const keyboardInput = document.getElementById("keyboardInput");
const trackpad = document.getElementById("trackpad");


// ----------------------------
// SEND COMMAND TO CONTROL SERVER
// ----------------------------

async function sendCommand(command) {
  console.log(`Sending command: ${command}`);

  try {
    const response = await fetch(`${SERVER_URL}/command`, {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        command: command,
      }),
    });

    if (!response.ok) {
      console.error(`Server error: ${response.status}`);
      return;
    }

    const data = await response.json();

    console.log("Server response:", data);

  } catch (error) {
    console.error("Could not reach control server:", error);
  }
}


// ----------------------------
// COMMAND BUTTONS
// ----------------------------

const commandButtons = document.querySelectorAll("[data-command]");

commandButtons.forEach((button) => {
  button.addEventListener("click", () => {

    const command = button.dataset.command;

    // Opening the input panel is local UI behaviour,
    // so don't send it to the control server.
    if (command !== "input") {
      sendCommand(command);
    }

  });
});


// ----------------------------
// INPUT PANEL
// ----------------------------

inputButton.addEventListener("click", () => {
  inputPanel.classList.add("open");
});

closeInputPanel.addEventListener("click", () => {
  inputPanel.classList.remove("open");
});


// ----------------------------
// KEYBOARD
// ----------------------------

keyboardInput.addEventListener("input", (event) => {
  console.log("Keyboard:", event.target.value);
});


// ----------------------------
// TRACKPAD
// ----------------------------

let activePointers = new Map();
let lastSinglePointerPosition = null;
let lastTwoFingerY = null;


trackpad.addEventListener("pointerdown", (event) => {

  activePointers.set(event.pointerId, {
    x: event.clientX,
    y: event.clientY,
  });

  trackpad.setPointerCapture(event.pointerId);

  // One finger = mouse movement
  if (activePointers.size === 1) {

    lastSinglePointerPosition = {
      x: event.clientX,
      y: event.clientY,
    };

    lastTwoFingerY = null;
  }

  // Two fingers = scrolling
  if (activePointers.size === 2) {

    const pointers = Array.from(activePointers.values());

    lastTwoFingerY =
      (pointers[0].y + pointers[1].y) / 2;

    lastSinglePointerPosition = null;
  }
});


trackpad.addEventListener("pointermove", (event) => {

  if (!activePointers.has(event.pointerId)) return;

  activePointers.set(event.pointerId, {
    x: event.clientX,
    y: event.clientY,
  });


  // ONE FINGER: mouse movement

  if (
    activePointers.size === 1 &&
    lastSinglePointerPosition
  ) {

    const deltaX =
      event.clientX - lastSinglePointerPosition.x;

    const deltaY =
      event.clientY - lastSinglePointerPosition.y;

    console.log("Mouse move:", deltaX, deltaY);

    lastSinglePointerPosition = {
      x: event.clientX,
      y: event.clientY,
    };
  }


  // TWO FINGERS: scrolling

  if (activePointers.size === 2) {

    const pointers =
      Array.from(activePointers.values());

    const currentTwoFingerY =
      (pointers[0].y + pointers[1].y) / 2;

    if (lastTwoFingerY !== null) {

      const scrollDelta =
        currentTwoFingerY - lastTwoFingerY;

      console.log("Scroll:", scrollDelta);
    }

    lastTwoFingerY = currentTwoFingerY;
  }
});


function removePointer(event) {

  activePointers.delete(event.pointerId);

  if (activePointers.size === 1) {

    const remainingPointer =
      Array.from(activePointers.values())[0];

    lastSinglePointerPosition = {
      x: remainingPointer.x,
      y: remainingPointer.y,
    };

    lastTwoFingerY = null;
  }

  if (activePointers.size === 0) {

    lastSinglePointerPosition = null;
    lastTwoFingerY = null;
  }

  try {
    trackpad.releasePointerCapture(event.pointerId);
  } catch {
    // Pointer capture may already be released.
  }
}


trackpad.addEventListener("pointerup", removePointer);
trackpad.addEventListener("pointercancel", removePointer);