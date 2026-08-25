from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import asyncio
import ctypes
import json
import os
import subprocess
import threading
import time
import webbrowser

from ctypes import wintypes

import pyautogui
import websockets


HOST = "0.0.0.0"
HTTP_PORT = 8765
WS_PORT = 8766

MOUSE_SENSITIVITY = 3.0
SCROLL_SENSITIVITY = 0.15

EDGE_PATH = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
)

PROFILE_ROOT = r"C:\LaptopTV\profiles"


# ----------------------------
# STREAMING SERVICES
# ----------------------------

STREAMING_SERVICES = {
    "netflix": {
        "url": "https://www.netflix.com",
        "profile": "netflix",
        "window_titles": ["Netflix"],
    },
    "disney": {
        "url": "https://www.disneyplus.com",
        "profile": "disney",
        "window_titles": ["Disney"],
    },
    "max": {
        "url": "https://www.max.com",
        "profile": "max",
        "window_titles": ["Max"],
    },
    "youtube": {
        "url": "https://www.youtube.com",
        "profile": "youtube",
        "window_titles": ["YouTube"],
    },
    "yle": {
        "url": "https://areena.yle.fi",
        "profile": "yle",
        "window_titles": ["Yle Areena", "Areena"],
    },
}


# ----------------------------
# WINDOWS WINDOW CONTROL
# ----------------------------

user32 = ctypes.windll.user32

SW_RESTORE = 9


def find_window_by_title(keywords):
    found_window = None

    @ctypes.WINFUNCTYPE(
        wintypes.BOOL,
        wintypes.HWND,
        wintypes.LPARAM,
    )
    def enum_window_callback(hwnd, lparam):
        nonlocal found_window

        if not user32.IsWindowVisible(hwnd):
            return True

        length = user32.GetWindowTextLengthW(hwnd)

        if length == 0:
            return True

        buffer = ctypes.create_unicode_buffer(
            length + 1
        )

        user32.GetWindowTextW(
            hwnd,
            buffer,
            length + 1,
        )

        title = buffer.value.lower()

        for keyword in keywords:
            if keyword.lower() in title:
                found_window = hwnd
                return False

        return True

    user32.EnumWindows(
        enum_window_callback,
        0,
    )

    return found_window


def focus_window(hwnd):
    if not hwnd:
        return False

    if user32.IsIconic(hwnd):
        user32.ShowWindow(
            hwnd,
            SW_RESTORE,
        )

    user32.SetForegroundWindow(hwnd)

    return True


# ----------------------------
# EDGE APP LAUNCHER
# ----------------------------

def launch_streaming_service(service_name):
    service = STREAMING_SERVICES.get(
        service_name
    )

    if not service:
        return False

    existing_window = find_window_by_title(
        service["window_titles"]
    )

    if existing_window:
        focus_window(existing_window)
        return True

    if not os.path.exists(EDGE_PATH):
        return False

    profile_path = os.path.join(
        PROFILE_ROOT,
        service["profile"],
    )

    os.makedirs(
        profile_path,
        exist_ok=True,
    )

    subprocess.Popen(
        [
            EDGE_PATH,
            f'--app={service["url"]}',
            f"--user-data-dir={profile_path}",
            "--no-first-run",
            "--no-default-browser-check",
        ]
    )

    # Give Edge time to create the app window.
    time.sleep(1.5)

    new_window = find_window_by_title(
        service["window_titles"]
    )

    if new_window:
        focus_window(new_window)

        # Allow focus to settle before toggling fullscreen.
        time.sleep(0.2)

        pyautogui.press("f11")

    return True


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


SendInput = user32.SendInput

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
        -delta
        * SCROLL_SENSITIVITY
        * 120
    )

    if wheel_delta == 0:
        return

    send_mouse_input(
        mouse_data=wheel_delta,
        flags=MOUSEEVENTF_WHEEL,
    )


# ----------------------------
# STANDARD COMMANDS
# ----------------------------

def execute_command(command, data):
    if command in STREAMING_SERVICES:
        return launch_streaming_service(
            command
        )

    if command == "web":
        webbrowser.open(
            "https://www.google.com"
        )
        return True

    if command == "desktop":
        pyautogui.hotkey(
            "win",
            "d",
        )
        return True

    if command == "left-click":
        left_click()
        return True

    if command == "right-click":
        right_click()
        return True

    if command == "volume-up":
        pyautogui.press(
            "volumeup"
        )
        return True

    if command == "volume-down":
        pyautogui.press(
            "volumedown"
        )
        return True

    if command == "steam":
        try:
            os.startfile(
                "steam://open/bigpicture"
            )
            return True

        except OSError:
            return False

    if command == "retro":
        retroarch_path = (
            r"C:\RetroArch-Win64\retroarch.exe"
        )

        if os.path.exists(
            retroarch_path
        ):
            subprocess.Popen(
                [retroarch_path]
            )
            return True

        return False

    if command == "screensaver":
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

    return False


# ----------------------------
# HTTP SERVER
# ----------------------------

class ControlHandler(
    BaseHTTPRequestHandler
):

    def log_message(
        self,
        format,
        *args,
    ):
        pass

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

    server.serve_forever()


# ----------------------------
# WEBSOCKET SERVER
# ----------------------------

async def handle_websocket(
    websocket
):
    try:
        async for message in websocket:
            data = json.loads(
                message
            )

            command = data.get(
                "command"
            )

            if command == "mouse-move":
                dx = data.get(
                    "dx",
                    0,
                )

                dy = data.get(
                    "dy",
                    0,
                )

                move_mouse(
                    dx,
                    dy,
                )

            elif command == "scroll":
                delta = data.get(
                    "delta",
                    0,
                )

                scroll_mouse(
                    delta
                )

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

                for _ in range(
                    count
                ):
                    pyautogui.press(
                        "backspace"
                    )

            elif command == "key-press":
                key = data.get(
                    "key"
                )

                if key == "enter":
                    pyautogui.press(
                        "enter"
                    )

    except websockets.ConnectionClosed:
        pass

    except json.JSONDecodeError:
        pass

    except Exception:
        pass


async def run_websocket_server():
    async with websockets.serve(
        handle_websocket,
        HOST,
        WS_PORT,
    ):
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
        pass


if __name__ == "__main__":
    main()