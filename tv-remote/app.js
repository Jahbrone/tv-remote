const SERVER_URL = "http://192.168.1.187:8765";
const WEBSOCKET_URL = "ws://192.168.1.187:8766";

const inputButton = document.getElementById("inputButton");
const inputPanel = document.getElementById("inputPanel");
const closeInputPanel = document.getElementById("closeInputPanel");
const openKeyboardButton = document.getElementById("openKeyboardButton");
const keyboardInput = document.getElementById("keyboardInput");
const trackpad = document.getElementById("trackpad");
const powerButton = document.getElementById("powerButton");

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
        command,
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
// WEBSOCKET SEND
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
// POWER — LONG HOLD
// ----------------------------

const POWER_HOLD_TIME = 1000;

let powerHoldTimer = null;
let powerTriggered = false;

function startPowerHold(event) {
  event.preventDefault();

  powerTriggered = false;

  powerButton.classList.add("holding");

  powerHoldTimer = setTimeout(() => {
    powerTriggered = true;
    powerHoldTimer = null;

    powerButton.classList.remove("holding");
    powerButton.classList.add("power-triggered");

    sendCommand("power");

    setTimeout(() => {
      powerButton.classList.remove("power-triggered");
    }, 300);
  }, POWER_HOLD_TIME);
}

function cancelPowerHold() {
  if (powerHoldTimer !== null) {
    clearTimeout(powerHoldTimer);
    powerHoldTimer = null;
  }

  if (!powerTriggered) {
    powerButton.classList.remove("holding");
  }
}

powerButton.addEventListener("pointerdown", startPowerHold);
powerButton.addEventListener("pointerup", cancelPowerHold);
powerButton.addEventListener("pointerleave", cancelPowerHold);
powerButton.addEventListener("pointercancel", cancelPowerHold);

// ----------------------------
// COMMAND BUTTONS
// ----------------------------

const commandButtons = document.querySelectorAll("[data-command]");

commandButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const command = button.dataset.command;

    if (
      command === "power" ||
      command === "input"
    ) {
      return;
    }

    sendCommand(command);
  });
});

// ----------------------------
// INPUT PANEL
// ----------------------------

const KEYBOARD_SENTINEL = " ";

function resetKeyboardInput() {
  keyboardInput.value = KEYBOARD_SENTINEL;

  keyboardInput.setSelectionRange(
    KEYBOARD_SENTINEL.length,
    KEYBOARD_SENTINEL.length,
  );
}

function showKeyboard() {
  resetKeyboardInput();
  keyboardInput.focus();
}

function hideKeyboard() {
  keyboardInput.blur();
}

function keyboardIsOpen() {
  return document.activeElement === keyboardInput;
}

inputButton.addEventListener("click", () => {
  // Always open the trackpad with the phone keyboard hidden.
  hideKeyboard();

  inputPanel.classList.add("open");
});

closeInputPanel.addEventListener("click", () => {
  hideKeyboard();

  inputPanel.classList.remove("open");
});

openKeyboardButton.addEventListener("click", () => {
  if (keyboardIsOpen()) {
    hideKeyboard();
  } else {
    showKeyboard();
  }
});

// ----------------------------
// REMOTE KEYBOARD
// ----------------------------

keyboardInput.addEventListener("focus", () => {
  resetKeyboardInput();
});

keyboardInput.addEventListener("beforeinput", (event) => {
  const inputType = event.inputType;

  // BACKSPACE
  if (inputType === "deleteContentBackward") {
    event.preventDefault();

    sendSocketCommand({
      command: "backspace",
      count: 1,
    });

    resetKeyboardInput();

    return;
  }

  // ENTER
  if (
    inputType === "insertLineBreak" ||
    inputType === "insertParagraph"
  ) {
    event.preventDefault();

    sendSocketCommand({
      command: "key-press",
      key: "enter",
    });

    resetKeyboardInput();

    return;
  }

  // NORMAL TEXT
  if (
    inputType === "insertText" ||
    inputType === "insertCompositionText"
  ) {
    if (!event.data) {
      return;
    }

    event.preventDefault();

    sendSocketCommand({
      command: "type-text",
      text: event.data,
    });

    resetKeyboardInput();
  }
});

// ----------------------------
// MOUSE MOVEMENT
// ----------------------------

let pendingMouseX = 0;
let pendingMouseY = 0;
let mouseSendScheduled = false;

function sendMouseMove(dx, dy) {
  pendingMouseX += dx;
  pendingMouseY += dy;

  if (mouseSendScheduled) {
    return;
  }

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
// ONE-FINGER TRACKPAD
// ----------------------------

let activePointerId = null;
let lastPointerX = null;
let lastPointerY = null;

trackpad.addEventListener("pointerdown", (event) => {
  if (activePointerId !== null) {
    return;
  }

  activePointerId = event.pointerId;

  lastPointerX = event.clientX;
  lastPointerY = event.clientY;

  trackpad.setPointerCapture(event.pointerId);
});

trackpad.addEventListener("pointermove", (event) => {
  if (event.pointerId !== activePointerId) {
    return;
  }

  const deltaX = event.clientX - lastPointerX;
  const deltaY = event.clientY - lastPointerY;

  sendMouseMove(deltaX, deltaY);

  lastPointerX = event.clientX;
  lastPointerY = event.clientY;
});

function endPointer(event) {
  if (event.pointerId !== activePointerId) {
    return;
  }

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

function sendScroll(delta) {
  sendSocketCommand({
    command: "scroll",
    delta,
  });
}

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
  {
    passive: false,
  },
);

trackpad.addEventListener(
  "touchmove",
  (event) => {
    if (event.touches.length !== 2) {
      return;
    }

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
  {
    passive: false,
  },
);

trackpad.addEventListener(
  "touchend",
  (event) => {
    if (event.touches.length < 2) {
      lastTwoFingerY = null;
    }
  },
  {
    passive: false,
  },
);

trackpad.addEventListener(
  "touchcancel",
  () => {
    lastTwoFingerY = null;
  },
  {
    passive: false,
  },
);