const SERVER_URL =
  "http://192.168.1.187:8765";

const WEBSOCKET_URL =
  "ws://192.168.1.187:8766";


const openKeyboardButton =
  document.getElementById(
    "openKeyboardButton"
  );

const keyboardInput =
  document.getElementById(
    "keyboardInput"
  );

const trackpad =
  document.getElementById(
    "trackpad"
  );

const powerButton =
  document.getElementById(
    "powerButton"
  );

const closeAppsButton =
  document.getElementById(
    "closeAppsButton"
  );

const connectionStatus =
  document.getElementById(
    "connectionStatus"
  );


// ----------------------------
// WEBSOCKET CONNECTION
// ----------------------------

let controlSocket = null;

let reconnectTimer = null;

const RECONNECT_DELAY = 500;


function setConnectionStatus(
  connected
) {

  if (!connectionStatus) {
    return;
  }


  connectionStatus.classList.toggle(
    "connected",
    connected
  );
}


function clearReconnectTimer() {

  if (
    reconnectTimer !== null
  ) {

    clearTimeout(
      reconnectTimer
    );

    reconnectTimer = null;
  }
}


function scheduleReconnect() {

  if (
    reconnectTimer !== null
  ) {
    return;
  }


  reconnectTimer =
    setTimeout(
      () => {

        reconnectTimer = null;

        connectControlSocket();

      },
      RECONNECT_DELAY
    );
}


function connectControlSocket(
  forceReconnect = false
) {

  clearReconnectTimer();


  if (controlSocket) {

    if (
      !forceReconnect &&
      (
        controlSocket.readyState ===
          WebSocket.OPEN ||
        controlSocket.readyState ===
          WebSocket.CONNECTING
      )
    ) {

      return;
    }


    try {

      controlSocket.close();

    } catch {

      // Socket was already closed.
    }


    controlSocket = null;
  }


  setConnectionStatus(
    false
  );


  const socket =
    new WebSocket(
      WEBSOCKET_URL
    );


  controlSocket =
    socket;


  socket.addEventListener(
    "open",
    () => {

      if (
        controlSocket !==
        socket
      ) {
        return;
      }


      console.log(
        "WebSocket connected"
      );


      clearReconnectTimer();


      setConnectionStatus(
        true
      );
    }
  );


  socket.addEventListener(
    "close",
    () => {

      if (
        controlSocket !==
        socket
      ) {
        return;
      }


      console.log(
        "WebSocket disconnected"
      );


      controlSocket =
        null;


      setConnectionStatus(
        false
      );


      scheduleReconnect();
    }
  );


  socket.addEventListener(
    "error",
    (error) => {

      if (
        controlSocket !==
        socket
      ) {
        return;
      }


      console.error(
        "WebSocket error:",
        error
      );


      setConnectionStatus(
        false
      );


      try {

        socket.close();

      } catch {

        // Socket was already closed.
      }
    }
  );
}


function reconnectControlSocket() {

  if (
    document.visibilityState !==
    "visible"
  ) {
    return;
  }


  connectControlSocket(
    true
  );
}


setConnectionStatus(
  false
);


connectControlSocket();


document.addEventListener(
  "visibilitychange",
  () => {

    if (
      document.visibilityState ===
      "visible"
    ) {

      reconnectControlSocket();
    }
  }
);


window.addEventListener(
  "focus",
  () => {

    reconnectControlSocket();
  }
);


window.addEventListener(
  "pageshow",
  () => {

    reconnectControlSocket();
  }
);


// ----------------------------
// HTTP COMMANDS
// ----------------------------

async function sendCommand(
  command
) {

  console.log(
    `Sending command: ${command}`
  );


  try {

    const response =
      await fetch(
        `${SERVER_URL}/command`,
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json",
          },

          body: JSON.stringify({
            command,
          }),
        }
      );


    if (!response.ok) {

      console.error(
        `Server error: ${response.status}`
      );

      return;
    }


    const data =
      await response.json();


    console.log(
      "Server response:",
      data
    );

  } catch (error) {

    console.error(
      "Could not reach control server:",
      error
    );
  }
}


// ----------------------------
// WEBSOCKET SEND
// ----------------------------

function sendSocketCommand(
  data
) {

  if (
    controlSocket &&
    controlSocket.readyState ===
      WebSocket.OPEN
  ) {

    controlSocket.send(
      JSON.stringify(data)
    );

    return;
  }


  connectControlSocket();
}


// ----------------------------
// HAPTIC FEEDBACK
// ----------------------------

function mouseClickHaptic() {

  try {

    if (
      window.AndroidHaptics &&
      typeof window.AndroidHaptics.click ===
        "function"
    ) {

      window.AndroidHaptics.click();
    }

  } catch (error) {

    console.error(
      "Haptic feedback failed:",
      error
    );
  }
}


// ----------------------------
// TRACKPAD CLICK FEEDBACK
// ----------------------------

function showClickFeedback(
  clientX,
  clientY
) {

  const rect =
    trackpad.getBoundingClientRect();


  const x =
    clientX - rect.left;

  const y =
    clientY - rect.top;


  const ring =
    document.createElement(
      "span"
    );


  ring.className =
    "trackpad-click-ring";


  ring.style.left =
    `${x}px`;

  ring.style.top =
    `${y}px`;


  trackpad.appendChild(
    ring
  );


  ring.addEventListener(
    "animationend",
    () => {

      ring.remove();
    },
    {
      once: true,
    }
  );


  setTimeout(
    () => {

      if (
        ring.isConnected
      ) {

        ring.remove();
      }

    },
    500
  );
}


// ----------------------------
// POWER — LONG HOLD
// ----------------------------

const POWER_HOLD_TIME =
  1000;

let powerHoldTimer = null;

let powerTriggered = false;


function startPowerHold(
  event
) {

  event.preventDefault();

  powerTriggered = false;

  powerButton.classList.add(
    "holding"
  );


  powerHoldTimer =
    setTimeout(
      () => {

        powerTriggered = true;

        powerHoldTimer = null;


        powerButton.classList.remove(
          "holding"
        );

        powerButton.classList.add(
          "power-triggered"
        );


        sendCommand(
          "power"
        );


        setTimeout(
          () => {

            powerButton.classList.remove(
              "power-triggered"
            );

          },
          300
        );

      },
      POWER_HOLD_TIME
    );
}


function cancelPowerHold() {

  if (
    powerHoldTimer !== null
  ) {

    clearTimeout(
      powerHoldTimer
    );

    powerHoldTimer = null;
  }


  if (!powerTriggered) {

    powerButton.classList.remove(
      "holding"
    );
  }
}


powerButton.addEventListener(
  "pointerdown",
  startPowerHold
);

powerButton.addEventListener(
  "pointerup",
  cancelPowerHold
);

powerButton.addEventListener(
  "pointerleave",
  cancelPowerHold
);

powerButton.addEventListener(
  "pointercancel",
  cancelPowerHold
);


// ----------------------------
// CLOSE MODE
// ----------------------------

const CLOSEABLE_COMMANDS =
  new Set([
    "netflix",
    "disney",
    "max",
    "youtube",
    "yle",
    "steam",
    "retro",
    "screensaver",
  ]);


let closeMode = false;


function setCloseMode(
  enabled
) {

  closeMode = enabled;


  document.body.classList.toggle(
    "close-mode-active",
    closeMode
  );


  closeAppsButton.classList.toggle(
    "close-mode-active",
    closeMode
  );


  closeAppsButton.textContent =
    "×";
}


closeAppsButton.addEventListener(
  "click",
  (event) => {

    event.preventDefault();
    event.stopPropagation();


    setCloseMode(
      !closeMode
    );
  }
);


// ----------------------------
// COMMAND BUTTONS
// ----------------------------

const commandButtons =
  document.querySelectorAll(
    "[data-command]"
  );


commandButtons.forEach(
  (button) => {

    button.addEventListener(
      "click",
      (event) => {

        const command =
          button.dataset.command;


        if (
          command === "power"
        ) {
          return;
        }


        if (closeMode) {

          event.preventDefault();
          event.stopPropagation();


          if (
            CLOSEABLE_COMMANDS.has(
              command
            )
          ) {

            sendCommand(
              `close-${command}`
            );

            setCloseMode(
              false
            );
          }

          return;
        }


        if (
          command === "left-click" ||
          command === "right-click"
        ) {

          mouseClickHaptic();
        }


        sendCommand(
          command
        );
      }
    );
  }
);


// ----------------------------
// KEYBOARD
// ----------------------------

const KEYBOARD_SENTINEL =
  " ";


function resetKeyboardInput() {

  keyboardInput.value =
    KEYBOARD_SENTINEL;


  keyboardInput.setSelectionRange(
    KEYBOARD_SENTINEL.length,
    KEYBOARD_SENTINEL.length
  );
}


function keyboardIsOpen() {

  return (
    document.activeElement ===
    keyboardInput
  );
}


function showKeyboard() {

  resetKeyboardInput();

  keyboardInput.focus();

  openKeyboardButton.classList.add(
    "keyboard-open"
  );
}


function hideKeyboard() {

  keyboardInput.blur();

  openKeyboardButton.classList.remove(
    "keyboard-open"
  );
}


openKeyboardButton.addEventListener(
  "click",
  () => {

    if (keyboardIsOpen()) {

      hideKeyboard();

    } else {

      showKeyboard();
    }
  }
);


keyboardInput.addEventListener(
  "blur",
  () => {

    openKeyboardButton.classList.remove(
      "keyboard-open"
    );
  }
);


keyboardInput.addEventListener(
  "focus",
  resetKeyboardInput
);


// ----------------------------
// REMOTE KEYBOARD
// ----------------------------

keyboardInput.addEventListener(
  "beforeinput",
  (event) => {

    const inputType =
      event.inputType;


    if (
      inputType ===
      "deleteContentBackward"
    ) {

      event.preventDefault();


      sendSocketCommand({
        command:
          "backspace",

        count: 1,
      });


      resetKeyboardInput();

      return;
    }


    if (
      inputType ===
        "insertLineBreak" ||
      inputType ===
        "insertParagraph"
    ) {

      event.preventDefault();


      sendSocketCommand({
        command:
          "key-press",

        key:
          "enter",
      });


      resetKeyboardInput();

      return;
    }


    if (
      inputType ===
        "insertText" ||
      inputType ===
        "insertCompositionText"
    ) {

      if (!event.data) {
        return;
      }


      event.preventDefault();


      sendSocketCommand({
        command:
          "type-text",

        text:
          event.data,
      });


      resetKeyboardInput();
    }
  }
);


// ----------------------------
// MOUSE MOVEMENT
// ----------------------------

let pendingMouseX = 0;
let pendingMouseY = 0;

let mouseSendScheduled =
  false;


function sendMouseMove(
  dx,
  dy
) {

  pendingMouseX += dx;

  pendingMouseY += dy;


  if (
    mouseSendScheduled
  ) {
    return;
  }


  mouseSendScheduled =
    true;


  requestAnimationFrame(
    () => {

      const moveX =
        pendingMouseX;

      const moveY =
        pendingMouseY;


      pendingMouseX = 0;

      pendingMouseY = 0;

      mouseSendScheduled =
        false;


      sendSocketCommand({
        command:
          "mouse-move",

        dx:
          moveX,

        dy:
          moveY,
      });
    }
  );
}


// ----------------------------
// TRACKPAD CLICK GESTURES
// ----------------------------

const HOLD_CLICK_TIME =
  450;

const MOVE_THRESHOLD =
  8;

const DOUBLE_TAP_TIME =
  300;

const DOUBLE_TAP_DISTANCE =
  35;


let holdTimer = null;

let pointerStartX = null;
let pointerStartY = null;

let pointerMoved = false;

let holdTriggered = false;

let lastTapTime = 0;

let lastTapX = null;
let lastTapY = null;


function sendLeftClick(
  clientX,
  clientY
) {

  showClickFeedback(
    clientX,
    clientY
  );


  mouseClickHaptic();


  sendSocketCommand({
    command:
      "left-click",
  });
}


function cancelHold() {

  if (
    holdTimer !== null
  ) {

    clearTimeout(
      holdTimer
    );

    holdTimer = null;
  }
}


function resetTapHistory() {

  lastTapTime = 0;

  lastTapX = null;

  lastTapY = null;
}


// ----------------------------
// ONE-FINGER TRACKPAD
// ----------------------------

let activePointerId = null;

let lastPointerX = null;
let lastPointerY = null;


trackpad.addEventListener(
  "pointerdown",
  (event) => {

    if (
      activePointerId !== null
    ) {
      return;
    }


    activePointerId =
      event.pointerId;


    lastPointerX =
      event.clientX;

    lastPointerY =
      event.clientY;


    pointerStartX =
      event.clientX;

    pointerStartY =
      event.clientY;


    pointerMoved =
      false;

    holdTriggered =
      false;


    trackpad.setPointerCapture(
      event.pointerId
    );


    cancelHold();


    const holdX =
      event.clientX;

    const holdY =
      event.clientY;


    holdTimer =
      setTimeout(
        () => {

          if (
            !pointerMoved &&
            activePointerId ===
              event.pointerId
          ) {

            holdTriggered =
              true;

            resetTapHistory();

            sendLeftClick(
              holdX,
              holdY
            );
          }


          holdTimer =
            null;

        },
        HOLD_CLICK_TIME
      );
  }
);


trackpad.addEventListener(
  "pointermove",
  (event) => {

    if (
      event.pointerId !==
      activePointerId
    ) {
      return;
    }


    const deltaX =
      event.clientX -
      lastPointerX;

    const deltaY =
      event.clientY -
      lastPointerY;


    const totalMoveX =
      event.clientX -
      pointerStartX;

    const totalMoveY =
      event.clientY -
      pointerStartY;


    const distance =
      Math.hypot(
        totalMoveX,
        totalMoveY
      );


    if (
      distance >
      MOVE_THRESHOLD
    ) {

      pointerMoved =
        true;

      cancelHold();

      resetTapHistory();
    }


    sendMouseMove(
      deltaX,
      deltaY
    );


    lastPointerX =
      event.clientX;

    lastPointerY =
      event.clientY;
  }
);


function endPointer(
  event
) {

  if (
    event.pointerId !==
    activePointerId
  ) {
    return;
  }


  cancelHold();


  if (
    !pointerMoved &&
    !holdTriggered
  ) {

    const now =
      Date.now();


    const timeDifference =
      now -
      lastTapTime;


    const tapDistance =
      (
        lastTapX === null ||
        lastTapY === null
      )

        ? Infinity

        : Math.hypot(
            event.clientX -
              lastTapX,

            event.clientY -
              lastTapY
          );


    if (
      timeDifference <=
        DOUBLE_TAP_TIME &&
      tapDistance <=
        DOUBLE_TAP_DISTANCE
    ) {

      sendLeftClick(
        event.clientX,
        event.clientY
      );

      resetTapHistory();

    } else {

      lastTapTime =
        now;

      lastTapX =
        event.clientX;

      lastTapY =
        event.clientY;
    }
  }


  activePointerId =
    null;

  lastPointerX =
    null;

  lastPointerY =
    null;

  pointerStartX =
    null;

  pointerStartY =
    null;

  pointerMoved =
    false;

  holdTriggered =
    false;


  try {

    trackpad.releasePointerCapture(
      event.pointerId
    );

  } catch {

    // Already released.
  }
}


trackpad.addEventListener(
  "pointerup",
  endPointer
);


trackpad.addEventListener(
  "pointercancel",
  (event) => {

    cancelHold();

    resetTapHistory();


    if (
      event.pointerId ===
      activePointerId
    ) {

      activePointerId =
        null;

      lastPointerX =
        null;

      lastPointerY =
        null;

      pointerStartX =
        null;

      pointerStartY =
        null;
    }
  }
);


// ----------------------------
// TWO-FINGER SCROLL
// ----------------------------

let lastTwoFingerY = null;


function sendScroll(
  delta
) {

  sendSocketCommand({
    command:
      "scroll",

    delta,
  });
}


trackpad.addEventListener(
  "touchstart",
  (event) => {

    if (
      event.touches.length !==
      2
    ) {
      return;
    }


    event.preventDefault();


    cancelHold();

    resetTapHistory();


    pointerMoved =
      true;

    holdTriggered =
      false;


    const y1 =
      event.touches[0]
        .clientY;

    const y2 =
      event.touches[1]
        .clientY;


    lastTwoFingerY =
      (y1 + y2) / 2;


    activePointerId =
      null;

    lastPointerX =
      null;

    lastPointerY =
      null;
  },
  {
    passive: false,
  }
);


trackpad.addEventListener(
  "touchmove",
  (event) => {

    if (
      event.touches.length !==
      2
    ) {
      return;
    }


    event.preventDefault();


    const y1 =
      event.touches[0]
        .clientY;

    const y2 =
      event.touches[1]
        .clientY;


    const currentY =
      (y1 + y2) / 2;


    if (
      lastTwoFingerY !==
      null
    ) {

      const delta =
        currentY -
        lastTwoFingerY;


      sendScroll(
        -delta
      );
    }


    lastTwoFingerY =
      currentY;
  },
  {
    passive: false,
  }
);


trackpad.addEventListener(
  "touchend",
  (event) => {

    if (
      event.touches.length <
      2
    ) {

      lastTwoFingerY =
        null;
    }
  },
  {
    passive: false,
  }
);


trackpad.addEventListener(
  "touchcancel",
  () => {

    lastTwoFingerY =
      null;

    cancelHold();

    resetTapHistory();
  },
  {
    passive: false,
  }
);