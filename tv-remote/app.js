const SERVER_URL = "http://192.168.1.93:8765";

const inputButton = document.getElementById("inputButton");
const inputPanel = document.getElementById("inputPanel");
const closeInputPanel = document.getElementById("closeInputPanel");
const keyboardInput = document.getElementById("keyboardInput");
const trackpad = document.getElementById("trackpad");

// ----------------------------
// SEND STANDARD COMMAND
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
// THROTTLED MOUSE MOVEMENT
// ----------------------------

let pendingMouseX = 0;
let pendingMouseY = 0;
let mouseSendScheduled = false;

function sendMouseMove(dx, dy) {
  pendingMouseX += dx;
  pendingMouseY += dy;

  if (mouseSendScheduled) return;

  mouseSendScheduled = true;

  requestAnimationFrame(async () => {
    const moveX = pendingMouseX;
    const moveY = pendingMouseY;

    pendingMouseX = 0;
    pendingMouseY = 0;
    mouseSendScheduled = false;

    try {
      await fetch(`${SERVER_URL}/command`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          command: "mouse-move",
          dx: moveX,
          dy: moveY,
        }),
      });
    } catch (error) {
      console.error("Mouse movement failed:", error);
    }
  });
}

// ----------------------------
// COMMAND BUTTONS
// ----------------------------

const commandButtons = document.querySelectorAll("[data-command]");

commandButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const command = button.dataset.command;

    // Opening the input panel is local UI only.
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

  // ----------------------------
  // ONE FINGER: MOUSE MOVEMENT
  // ----------------------------

  if (
    activePointers.size === 1 &&
    lastSinglePointerPosition
  ) {
    const deltaX =
      event.clientX - lastSinglePointerPosition.x;

    const deltaY =
      event.clientY - lastSinglePointerPosition.y;

    console.log("Mouse move:", deltaX, deltaY);

    sendMouseMove(deltaX, deltaY);

    lastSinglePointerPosition = {
      x: event.clientX,
      y: event.clientY,
    };
  }

  // ----------------------------
  // TWO FINGERS: SCROLL
  // ----------------------------

  if (activePointers.size === 2) {
    const pointers =
      Array.from(activePointers.values());

    const currentTwoFingerY =
      (pointers[0].y + pointers[1].y) / 2;

    if (lastTwoFingerY !== null) {
      const scrollDelta =
        currentTwoFingerY - lastTwoFingerY;

      console.log("Scroll:", scrollDelta);

      // Scroll not sent to server yet.
    }

    lastTwoFingerY = currentTwoFingerY;
  }
});

function removePointer(event) {
  activePointers.delete(event.pointerId);

  // Back to one finger after a two-finger gesture
  if (activePointers.size === 1) {
    const remainingPointer =
      Array.from(activePointers.values())[0];

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
    // Pointer capture may already have been released.
  }
}

trackpad.addEventListener("pointerup", removePointer);
trackpad.addEventListener("pointercancel", removePointer);