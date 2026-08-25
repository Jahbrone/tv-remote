from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import asyncio
import ctypes
import json
import os
import subprocess
import threading
import webbrowser

from ctypes import wintypes

import pyautogui
import websockets


HOST = "0.0.0.0"
HTTP_PORT = 8765
WS_PORT = 8766

MOUSE_SENSITIVITY = 3.0
SCROLL_SENSITIVITY = 0.15


# ----------------------------
# WINDOWS NATIVE INPUT
# ----------------------------

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_WHEEL = 0x0800

ULONG_PTR = (
    ctypes.c_ulonglong
    if ctypes.sizeof(ctypes.c_void_p) == 8
    else ctypes.c_ulong
)


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
    ]


class INPUT(ctypes.Structure):
    _anonymous_ = ("union",)

    _fields_ = [
        ("type", wintypes.DWORD),
        ("union", INPUT_UNION),
    ]


SendInput = ctypes.windll.user32.SendInput

SendInput.argtypes = (
    wintypes.UINT,
    ctypes.POINTER(INPUT),
    ctypes.c_int,
)

SendInput.restype = wintypes.UINT


def send_mouse_input(
    dx=0,
    dy=0,
    mouse_data=0,
    flags=0,
):
    mouse_input = INPUT(
        type=INPUT_MOUSE,
        mi=MOUSEINPUT(
            dx=int(dx),
            dy=int(dy),
            mouseData=int(mouse_data),
            dwFlags=flags,
            time=0,
            dwExtraInfo=0,
        ),
    )

    SendInput(
        1,
        ctypes.byref(mouse_input),
        ctypes.sizeof(INPUT),
    )


# ----------------------------
# NATIVE MOUSE
# ----------------------------

def move_mouse(dx, dy):
    send_mouse_input(
        dx=dx * MOUSE_SENSITIVITY,
        dy=dy * MOUSE_SENSITIVITY,
        flags=MOUSEEVENTF_MOVE,
    )


def left_click():
    send_mouse_input(
        flags=MOUSEEVENTF_LEFTDOWN,
    )

    send_mouse_input(
        flags=MOUSEEVENTF_LEFTUP,
    )


def right_click():
    send_mouse_input(
        flags=MOUSEEVENTF_RIGHTDOWN,
    )

    send_mouse_input(
        flags=MOUSEEVENTF_RIGHTUP,
    )


def scroll_mouse(delta):
    wheel_delta = int(
        -delta * SCROLL_SENSITIVITY * 120
    )

    if wheel_delta == 0:
        return

    send_mouse_input(
        mouse_data=wheel_delta,
        flags=MOUSEEVENTF_WHEEL,
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
        left_click()
        return True

    if command == "right-click":
        right_click()
        return True

    if command == "volume-up":
        pyautogui.press("volumeup")
        return True

    if command == "volume-down":
        pyautogui.press("volumedown")
        return True

    if command == "steam":
        steam_path = (
            r"C:\Program Files (x86)\Steam\Steam.exe"
        )

        if os.path.exists(steam_path):
            subprocess.Popen(
                [steam_path, "-bigpicture"]
            )
            return True

        print("Steam not found")
        return False

    if command == "retro":
        retroarch_path = (
            r"C:\RetroArch-Win64\retroarch.exe"
        )

        if os.path.exists(retroarch_path):
            subprocess.Popen(
                [retroarch_path]
            )
            return True

        print("RetroArch not found")
        return False

    if command == "screensaver":
        print(
            "Screensaver command received "
            "— not configured yet"
        )
        return False

    if command == "power":
        subprocess.run(
            [
                "rundll32.exe",
                "powrprof.dll,SetSuspendState",
                "0,1,0",
            ],
            check=False,
        )
        return True

    print(
        f"No action configured for: {command}"
    )

    return False


# ----------------------------
# HTTP SERVER
# ----------------------------

class ControlHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header(
            "Access-Control-Allow-Origin",
            "*",
        )

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
            self.headers.get(
                "Content-Length",
                0,
            )
        )

        body = self.rfile.read(
            content_length
        )

        try:
            data = json.loads(body)

            command = data.get(
                "command"
            )

            print(
                f"Received command: {command}"
            )

            executed = execute_command(
                command,
                data,
            )

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
                (
                    json.dumps(response)
                    + "\n"
                ).encode()
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
        f"HTTP control server running "
        f"on port {HTTP_PORT}"
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

            command = data.get(
                "command"
            )

            if command == "mouse-move":
                dx = data.get("dx", 0)
                dy = data.get("dy", 0)

                move_mouse(
                    dx,
                    dy,
                )

            elif command == "scroll":
                delta = data.get(
                    "delta",
                    0,
                )

                scroll_mouse(delta)

            elif command == "type-text":
                text = data.get(
                    "text",
                    "",
                )

                if text:
                    pyautogui.write(
                        text,
                        interval=0,
                    )

            elif command == "backspace":
                count = int(
                    data.get(
                        "count",
                        1,
                    )
                )

                for _ in range(count):
                    pyautogui.press(
                        "backspace"
                    )

            elif command == "key-press":
                key = data.get("key")

                if key == "enter":
                    pyautogui.press(
                        "enter"
                    )

    except websockets.ConnectionClosed:
        pass

    except json.JSONDecodeError:
        print(
            "Invalid WebSocket JSON received"
        )

    except Exception as error:
        print(
            f"WebSocket error: {error}"
        )

    finally:
        print(
            "WebSocket disconnected"
        )


async def run_websocket_server():
    async with websockets.serve(
        handle_websocket,
        HOST,
        WS_PORT,
    ):
        print(
            f"WebSocket server running "
            f"on port {WS_PORT}"
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
        print(
            "\nStopping control server..."
        )


if __name__ == "__main__":
    main()