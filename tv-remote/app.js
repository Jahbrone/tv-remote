const SERVER_URL = "http://192.168.1.93:8765";
const WEBSOCKET_URL = "ws://192.168.1.93:8766";

const inputButton = document.getElementById("inputButton");
const inputPanel = document.getElementById("inputPanel");
const closeInputPanel = document.getElementById("closeInputPanel");
const keyboardInput = document.getElementById("keyboardInput");
const trackpad = document.getElementById("trackpad");

// ----------------------------
// WEBSOCKET CONNECTION
// ----------------------------

let controlSocket = null;

function connectControlSocket() {
  controlSocket = new WebSocket(WEBSOCKET_URL);

  controlSocket.addEventListener("open", () => {
    console.log("WebSocket connected");
  });

  controlSocket.addEventListener("close", () => {
    console.log("WebSocket disconnected");

    setTimeout(() => {
      connectControlSocket();
    }, 1000);
  });

  controlSocket.addEventListener("error", (error) => {
    console.error("WebSocket error:", error);
  });
}

connectControlSocket();

// ----------------------------
// STANDARD HTTP COMMANDS
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
// WEBSOCKET SEND HELPER
// ----------------------------

function sendSocketCommand(data) {
  if (
    controlSocket &&
    controlSocket.readyState === WebSocket.OPEN
  ) {
    controlSocket.send(JSON.stringify(data));
  }
}

// ----------------------------
// MOUSE MOVEMENT
// ----------------------------

let pendingMouseX = 0;
let pendingMouseY = 0;
let mouseSendScheduled = false;

function sendMouseMove(dx, dy) {
  pendingMouseX += dx;
  pendingMouseY += dy;

  if (mouseSendScheduled) return;

  mouseSendScheduled = true;

  requestAnimationFrame(() => {
    const moveX = pendingMouseX;
    const moveY = pendingMouseY;

    pendingMouseX = 0;
    pendingMouseY = 0;
    mouseSendScheduled = false;

    sendSocketCommand({
      command: "mouse-move",
      dx: moveX,
      dy: moveY,
    });
  });
}

// ----------------------------
// SCROLL
// ----------------------------

function sendScroll(delta) {
  sendSocketCommand({
    command: "scroll",
    delta: delta,
  });
}

// ----------------------------
// COMMAND BUTTONS
// ----------------------------

const commandButtons =
  document.querySelectorAll("[data-command]");

commandButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const command = button.dataset.command;

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

let lastKeyboardValue = "";

keyboardInput.addEventListener("input", (event) => {
  const currentValue = event.target.value;

  // New characters typed
  if (currentValue.length > lastKeyboardValue.length) {
    const newText =
      currentValue.slice(lastKeyboardValue.length);

    sendSocketCommand({
      command: "type-text",
      text: newText,
    });
  }

  // Characters deleted
  if (currentValue.length < lastKeyboardValue.length) {
    const deletedCount =
      lastKeyboardValue.length - currentValue.length;

    sendSocketCommand({
      command: "backspace",
      count: deletedCount,
    });
  }

  lastKeyboardValue = currentValue;
});

// Enter / Send
keyboardInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();

    sendSocketCommand({
      command: "key-press",
      key: "enter",
    });
  }
});

// ----------------------------
// ONE-FINGER TRACKPAD MOVEMENT
// ----------------------------

let activePointerId = null;
let lastPointerX = null;
let lastPointerY = null;

trackpad.addEventListener("pointerdown", (event) => {
  if (activePointerId !== null) return;

  activePointerId = event.pointerId;
  lastPointerX = event.clientX;
  lastPointerY = event.clientY;

  trackpad.setPointerCapture(event.pointerId);
});

trackpad.addEventListener("pointermove", (event) => {
  if (event.pointerId !== activePointerId) return;

  const deltaX = event.clientX - lastPointerX;
  const deltaY = event.clientY - lastPointerY;

  sendMouseMove(deltaX, deltaY);

  lastPointerX = event.clientX;
  lastPointerY = event.clientY;
});

function endPointer(event) {
  if (event.pointerId !== activePointerId) return;

  activePointerId = null;
  lastPointerX = null;
  lastPointerY = null;

  try {
    trackpad.releasePointerCapture(event.pointerId);
  } catch {
    // Already released.
  }
}

trackpad.addEventListener("pointerup", endPointer);
trackpad.addEventListener("pointercancel", endPointer);

// ----------------------------
// TWO-FINGER SCROLL
// ----------------------------

let lastTwoFingerY = null;

trackpad.addEventListener(
  "touchstart",
  (event) => {
    if (event.touches.length === 2) {
      event.preventDefault();

      const y1 = event.touches[0].clientY;
      const y2 = event.touches[1].clientY;

      lastTwoFingerY = (y1 + y2) / 2;

      activePointerId = null;
      lastPointerX = null;
      lastPointerY = null;
    }
  },
  { passive: false },
);

trackpad.addEventListener(
  "touchmove",
  (event) => {
    if (event.touches.length !== 2) return;

    event.preventDefault();

    const y1 = event.touches[0].clientY;
    const y2 = event.touches[1].clientY;

    const currentY = (y1 + y2) / 2;

    if (lastTwoFingerY !== null) {
      const delta = currentY - lastTwoFingerY;

      sendScroll(delta);
    }

    lastTwoFingerY = currentY;
  },
  { passive: false },
);

trackpad.addEventListener(
  "touchend",
  (event) => {
    if (event.touches.length < 2) {
      lastTwoFingerY = null;
    }
  },
  { passive: false },
);

trackpad.addEventListener(
  "touchcancel",
  () => {
    lastTwoFingerY = null;
  },
  { passive: false },
);