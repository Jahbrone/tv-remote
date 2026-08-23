from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import asyncio
import json
import threading
import webbrowser

import pyautogui
import websockets

from Quartz import (
    CGEventCreate,
    CGEventGetLocation,
    CGEventCreateMouseEvent,
    CGEventPost,
    kCGEventMouseMoved,
    kCGMouseButtonLeft,
    kCGHIDEventTap,
)


HOST = "0.0.0.0"
HTTP_PORT = 8765
WS_PORT = 8766

MOUSE_SENSITIVITY = 1
SCROLL_SENSITIVITY = 0.15


# ----------------------------
# NATIVE MAC MOUSE MOVEMENT
# ----------------------------

def move_mouse(dx, dy):
    event = CGEventCreate(None)
    position = CGEventGetLocation(event)

    new_x = position.x + dx
    new_y = position.y + dy

    move_event = CGEventCreateMouseEvent(
        None,
        kCGEventMouseMoved,
        (new_x, new_y),
        kCGMouseButtonLeft,
    )

    CGEventPost(kCGHIDEventTap, move_event)


# ----------------------------
# STANDARD HTTP COMMANDS
# ----------------------------

def execute_command(command, data):
    if command == "netflix":
        webbrowser.open("https://www.netflix.com")
        return True

    if command == "left-click":
        pyautogui.click()
        return True

    if command == "right-click":
        pyautogui.rightClick()
        return True

    print(f"No action configured for: {command}")
    return False


# ----------------------------
# HTTP SERVER
# ----------------------------

class ControlHandler(BaseHTTPRequestHandler):

    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(204)
        self._send_cors_headers()
        self.end_headers()

    def do_POST(self):
        if self.path != "/command":
            self.send_response(404)
            self._send_cors_headers()
            self.end_headers()
            return

        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
            command = data.get("command")

            print(f"Received command: {command}")

            executed = execute_command(command, data)

            response = {
                "status": "ok",
                "command": command,
                "executed": executed,
            }

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json",
            )

            self._send_cors_headers()
            self.end_headers()

            self.wfile.write(
                (json.dumps(response) + "\n").encode()
            )

        except json.JSONDecodeError:
            self.send_response(400)
            self._send_cors_headers()
            self.end_headers()


def run_http_server():
    server = ThreadingHTTPServer(
        (HOST, HTTP_PORT),
        ControlHandler,
    )

    print(
        f"HTTP control server running on port {HTTP_PORT}"
    )

    server.serve_forever()


# ----------------------------
# WEBSOCKET SERVER
# ----------------------------

async def handle_websocket(websocket):
    print("WebSocket connected")

    try:
        async for message in websocket:
            data = json.loads(message)
            command = data.get("command")

            # Mouse movement
            if command == "mouse-move":
                dx = data.get("dx", 0)
                dy = data.get("dy", 0)

                move_mouse(
                    dx * MOUSE_SENSITIVITY,
                    dy * MOUSE_SENSITIVITY,
                )

            # Two-finger scroll
            elif command == "scroll":
                delta = data.get("delta", 0)

                scroll_amount = int(
                    -delta * SCROLL_SENSITIVITY
                )

                if scroll_amount != 0:
                    pyautogui.scroll(scroll_amount)

            # Type normal text
            elif command == "type-text":
                text = data.get("text", "")

                if text:
                    pyautogui.write(
                        text,
                        interval=0,
                    )

            # Backspace
            elif command == "backspace":
                count = int(
                    data.get("count", 1)
                )

                for _ in range(count):
                    pyautogui.press("backspace")

            # Special key presses
            elif command == "key-press":
                key = data.get("key")

                if key == "enter":
                    pyautogui.press("enter")

    except websockets.ConnectionClosed:
        pass

    except json.JSONDecodeError:
        print("Invalid WebSocket JSON received")

    except Exception as error:
        print(f"WebSocket error: {error}")

    finally:
        print("WebSocket disconnected")


async def run_websocket_server():
    async with websockets.serve(
        handle_websocket,
        HOST,
        WS_PORT,
    ):
        print(
            f"WebSocket server running on port {WS_PORT}"
        )

        await asyncio.Future()


# ----------------------------
# START EVERYTHING
# ----------------------------

def main():
    http_thread = threading.Thread(
        target=run_http_server,
        daemon=True,
    )

    http_thread.start()

    try:
        asyncio.run(
            run_websocket_server()
        )

    except KeyboardInterrupt:
        print("\nStopping control server...")


if __name__ == "__main__":
    main()