from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import asyncio
import json
import os
import subprocess
import threading
import webbrowser

import pyautogui
import websockets


HOST = "0.0.0.0"
HTTP_PORT = 8765
WS_PORT = 8766

MOUSE_SENSITIVITY = 1
SCROLL_SENSITIVITY = 0.15


# ----------------------------
# MOUSE MOVEMENT
# ----------------------------

def move_mouse(dx, dy):
    pyautogui.moveRel(
        dx * MOUSE_SENSITIVITY,
        dy * MOUSE_SENSITIVITY,
        duration=0,
    )


# ----------------------------
# STANDARD HTTP COMMANDS
# ----------------------------

def execute_command(command, data):
    if command == "netflix":
        webbrowser.open("https://www.netflix.com")
        return True

    if command == "disney":
        webbrowser.open("https://www.disneyplus.com")
        return True

    if command == "max":
        webbrowser.open("https://www.max.com")
        return True

    if command == "youtube":
        webbrowser.open("https://www.youtube.com")
        return True

    if command == "yle":
        webbrowser.open("https://areena.yle.fi")
        return True

    if command == "web":
        webbrowser.open("https://www.google.com")
        return True

    if command == "desktop":
        pyautogui.hotkey("win", "d")
        return True

    if command == "left-click":
        pyautogui.click()
        return True

    if command == "right-click":
        pyautogui.rightClick()
        return True

    if command == "volume-up":
        pyautogui.press("volumeup")
        return True

    if command == "volume-down":
        pyautogui.press("volumedown")
        return True

    if command == "steam":
        steam_path = r"C:\Program Files (x86)\Steam\Steam.exe"

        if os.path.exists(steam_path):
            subprocess.Popen([steam_path, "-bigpicture"])
            return True

        print("Steam not found")
        return False

    if command == "retro":
        retroarch_path = r"C:\RetroArch-Win64\retroarch.exe"

        if os.path.exists(retroarch_path):
            subprocess.Popen([retroarch_path])
            return True

        print("RetroArch not found")
        return False

    if command == "screensaver":
        print("Screensaver command received — not configured yet")
        return False

    if command == "power":
        print("Power command received — not configured yet")
        return False

    print(f"No action configured for: {command}")
    return False


# ----------------------------
# HTTP SERVER
# ----------------------------

class ControlHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header(
            "Access-Control-Allow-Methods",
            "POST, OPTIONS",
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type",
        )

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

            if command == "mouse-move":
                dx = data.get("dx", 0)
                dy = data.get("dy", 0)

                move_mouse(dx, dy)

            elif command == "scroll":
                delta = data.get("delta", 0)

                scroll_amount = int(
                    -delta * SCROLL_SENSITIVITY
                )

                if scroll_amount != 0:
                    pyautogui.scroll(scroll_amount)

            elif command == "type-text":
                text = data.get("text", "")

                if text:
                    pyautogui.write(
                        text,
                        interval=0,
                    )

            elif command == "backspace":
                count = int(
                    data.get("count", 1)
                )

                for _ in range(count):
                    pyautogui.press("backspace")

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