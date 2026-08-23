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

    lastTwoFingerY = (pointers[0].y + pointers[1].y) / 2;
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
  if (activePointers.size === 1 && lastSinglePointerPosition) {
    const deltaX = event.clientX - lastSinglePointerPosition.x;
    const deltaY = event.clientY - lastSinglePointerPosition.y;

    console.log("Mouse move:", deltaX, deltaY);

    lastSinglePointerPosition = {
      x: event.clientX,
      y: event.clientY,
    };
  }

  // TWO FINGERS: scroll
  if (activePointers.size === 2) {
    const pointers = Array.from(activePointers.values());

    const currentTwoFingerY = (pointers[0].y + pointers[1].y) / 2;

    if (lastTwoFingerY !== null) {
      const scrollDelta = currentTwoFingerY - lastTwoFingerY;

      console.log("Scroll:", scrollDelta);
    }

    lastTwoFingerY = currentTwoFingerY;
  }
});

function removePointer(event) {
  activePointers.delete(event.pointerId);

  // If we're back to one finger, reset mouse movement position
  if (activePointers.size === 1) {
    const remainingPointer = Array.from(activePointers.values())[0];

    lastSinglePointerPosition = {
      x: remainingPointer.x,
      y: remainingPointer.y,
    };

    lastTwoFingerY = null;
  }

  // No fingers left
  if (activePointers.size === 0) {
    lastSinglePointerPosition = null;
    lastTwoFingerY = null;
  }

  try {
    trackpad.releasePointerCapture(event.pointerId);
  } catch {
    // Pointer capture may already have been released
  }
}

trackpad.addEventListener("pointerup", removePointer);
trackpad.addEventListener("pointercancel", removePointer);
