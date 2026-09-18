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

from photos import get_all_photos


HOST = "0.0.0.0"
HTTP_PORT = 8765
WS_PORT = 8766

MOUSE_SENSITIVITY = 3.0
SCROLL_SENSITIVITY = 0.15

EDGE_PATH = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
)

RETROARCH_PATH = (
    r"C:\RetroArch-Win64\retroarch.exe"
)

PROFILE_ROOT = r"C:\LaptopTV\profiles"

SLIDESHOW_URL = (
    "http://192.168.1.187:8000/slideshow.html"
)


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
        "window_titles": [
            "Yle Areena",
            "Areena",
        ],
    },
}


# ----------------------------
# WINDOWS WINDOW CONTROL
# ----------------------------

user32 = ctypes.windll.user32

SW_RESTORE = 9
SW_MINIMIZE = 6

VK_MEDIA_PLAY_PAUSE = 0xB3

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004


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


def minimise_active_window():
    hwnd = user32.GetForegroundWindow()

    if not hwnd:
        return False

    user32.ShowWindow(
        hwnd,
        SW_MINIMIZE,
    )

    return True


def toggle_fullscreen():
    pyautogui.press(
        "f11"
    )

    return True


def media_play_pause():
    user32.keybd_event(
        VK_MEDIA_PLAY_PAUSE,
        0,
        KEYEVENTF_EXTENDEDKEY,
        0,
    )

    user32.keybd_event(
        VK_MEDIA_PLAY_PAUSE,
        0,
        KEYEVENTF_EXTENDEDKEY
        | KEYEVENTF_KEYUP,
        0,
    )

    return True


# ----------------------------
# EDGE APP LAUNCHER
# ----------------------------

def launch_edge_app(
    url,
    profile_name,
    window_titles,
):
    existing_window = find_window_by_title(
        window_titles
    )

    if existing_window:
        focus_window(existing_window)
        return True

    if not os.path.exists(EDGE_PATH):
        return False

    profile_path = os.path.join(
        PROFILE_ROOT,
        profile_name,
    )

    os.makedirs(
        profile_path,
        exist_ok=True,
    )

    subprocess.Popen(
        [
            EDGE_PATH,
            f"--app={url}",
            f"--user-data-dir={profile_path}",
            "--no-first-run",
            "--no-default-browser-check",
        ]
    )

    time.sleep(1.5)

    new_window = find_window_by_title(
        window_titles
    )

    if new_window:
        focus_window(
            new_window
        )

        time.sleep(
            0.2
        )

        pyautogui.press(
            "f11"
        )

    return True


def launch_streaming_service(
    service_name
):
    service = STREAMING_SERVICES.get(
        service_name
    )

    if not service:
        return False

    return launch_edge_app(
        service["url"],
        service["profile"],
        service["window_titles"],
    )


# ----------------------------
# PHOTO SLIDESHOW
# ----------------------------

def launch_slideshow():
    existing_window = find_window_by_title(
        ["TV Photos"]
    )

    if existing_window:
        focus_window(
            existing_window
        )

        return True

    if not os.path.exists(
        EDGE_PATH
    ):
        return False

    profile_path = os.path.join(
        PROFILE_ROOT,
        "slideshow",
    )

    os.makedirs(
        profile_path,
        exist_ok=True,
    )

    subprocess.Popen(
        [
            EDGE_PATH,
            f"--app={SLIDESHOW_URL}",
            f"--user-data-dir={profile_path}",
            "--no-first-run",
            "--no-default-browser-check",
        ]
    )

    slideshow_window = None

    for _ in range(
        20
    ):
        time.sleep(
            0.25
        )

        slideshow_window = find_window_by_title(
            ["TV Photos"]
        )

        if slideshow_window:
            break

    if slideshow_window:
        focus_window(
            slideshow_window
        )

        time.sleep(
            0.4
        )

        pyautogui.press(
            "f11"
        )

    return True


# ----------------------------
# RETROARCH
# ----------------------------

def launch_retroarch():
    existing_window = find_window_by_title(
        ["RetroArch"]
    )

    if existing_window:
        focus_window(
            existing_window
        )

        return True

    if not os.path.exists(
        RETROARCH_PATH
    ):
        return False

    subprocess.Popen(
        [RETROARCH_PATH]
    )

    retro_window = None

    for _ in range(
        20
    ):
        time.sleep(
            0.25
        )

        retro_window = find_window_by_title(
            ["RetroArch"]
        )

        if retro_window:
            break

    if retro_window:
        focus_window(
            retro_window
        )

        time.sleep(
            0.4
        )

        pyautogui.keyDown(
            "altleft"
        )

        pyautogui.press(
            "enter"
        )

        pyautogui.keyUp(
            "altleft"
        )

    return True


# ----------------------------
# CLOSE EDGE APP BY PROFILE
# ----------------------------

def close_edge_profile(
    profile_name
):
    profile_path = os.path.join(
        PROFILE_ROOT,
        profile_name,
    )

    powershell_command = rf"""
Get-CimInstance Win32_Process |
Where-Object {{
    $_.Name -eq 'msedge.exe' -and
    $_.CommandLine -like '*{profile_path}*'
}} |
ForEach-Object {{
    Stop-Process -Id $_.ProcessId -Force
}}
"""

    subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-WindowStyle",
            "Hidden",
            "-Command",
            powershell_command,
        ],
        check=False,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )

    return True


# ----------------------------
# CLOSE TV APPS
# ----------------------------

def close_edge_tv_apps():
    powershell_command = r"""
Get-CimInstance Win32_Process |
Where-Object {
    $_.Name -eq 'msedge.exe' -and
    $_.CommandLine -like '*C:\LaptopTV\profiles*'
} |
ForEach-Object {
    Stop-Process -Id $_.ProcessId -Force
}
"""

    subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-WindowStyle",
            "Hidden",
            "-Command",
            powershell_command,
        ],
        check=False,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


def close_steam():
    subprocess.run(
        [
            "taskkill",
            "/IM",
            "steam.exe",
            "/T",
            "/F",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )

    return True


def close_retroarch():
    subprocess.run(
        [
            "taskkill",
            "/IM",
            "retroarch.exe",
            "/T",
            "/F",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )

    return True


def close_tv_apps():
    close_edge_tv_apps()
    close_steam()
    close_retroarch()

    return True


# ----------------------------
# SELECTIVE CLOSE
# ----------------------------

def close_single_app(
    app_name
):
    if app_name in STREAMING_SERVICES:
        profile_name = STREAMING_SERVICES[
            app_name
        ]["profile"]

        return close_edge_profile(
            profile_name
        )

    if app_name == "screensaver":
        return close_edge_profile(
            "slideshow"
        )

    if app_name == "steam":
        return close_steam()

    if app_name == "retro":
        return close_retroarch()

    return False


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
    if ctypes.sizeof(
        ctypes.c_void_p
    ) == 8
    else ctypes.c_ulong
)


class MOUSEINPUT(
    ctypes.Structure
):
    _fields_ = [
        (
            "dx",
            wintypes.LONG,
        ),
        (
            "dy",
            wintypes.LONG,
        ),
        (
            "mouseData",
            wintypes.DWORD,
        ),
        (
            "dwFlags",
            wintypes.DWORD,
        ),
        (
            "time",
            wintypes.DWORD,
        ),
        (
            "dwExtraInfo",
            ULONG_PTR,
        ),
    ]


class INPUT_UNION(
    ctypes.Union
):
    _fields_ = [
        (
            "mi",
            MOUSEINPUT,
        ),
    ]


class INPUT(
    ctypes.Structure
):
    _anonymous_ = (
        "union",
    )

    _fields_ = [
        (
            "type",
            wintypes.DWORD,
        ),
        (
            "union",
            INPUT_UNION,
        ),
    ]


SendInput = user32.SendInput

SendInput.argtypes = (
    wintypes.UINT,
    ctypes.POINTER(
        INPUT
    ),
    ctypes.c_int,
)

SendInput.restype = (
    wintypes.UINT
)


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
            mouseData=int(
                mouse_data
            ),
            dwFlags=flags,
            time=0,
            dwExtraInfo=0,
        ),
    )

    SendInput(
        1,
        ctypes.byref(
            mouse_input
        ),
        ctypes.sizeof(
            INPUT
        ),
    )


# ----------------------------
# NATIVE MOUSE
# ----------------------------

def move_mouse(
    dx,
    dy
):
    send_mouse_input(
        dx=dx
        * MOUSE_SENSITIVITY,

        dy=dy
        * MOUSE_SENSITIVITY,

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


def scroll_mouse(
    delta
):
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
# UNICODE KEYBOARD INPUT
# ----------------------------

def type_unicode_text(
    text
):
    for char in text:
        codepoint = ord(
            char
        )

        if codepoint <= 0xFFFF:
            utf16_units = [
                codepoint
            ]

        else:
            codepoint -= 0x10000

            high_surrogate = (
                0xD800
                + (
                    codepoint
                    >> 10
                )
            )

            low_surrogate = (
                0xDC00
                + (
                    codepoint
                    & 0x3FF
                )
            )

            utf16_units = [
                high_surrogate,
                low_surrogate,
            ]

        for unit in utf16_units:
            user32.keybd_event(
                0,
                unit,
                KEYEVENTF_UNICODE,
                0,
            )

            user32.keybd_event(
                0,
                unit,
                KEYEVENTF_UNICODE
                | KEYEVENTF_KEYUP,
                0,
            )


# ----------------------------
# STANDARD COMMANDS
# ----------------------------

def execute_command(
    command,
    data
):
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

    if command == "play-pause":
        return media_play_pause()

    if command == "minimise":
        return minimise_active_window()

    if command == "fullscreen":
        return toggle_fullscreen()

    if command == "steam":
        try:
            os.startfile(
                "steam://open/bigpicture"
            )

            return True

        except OSError:
            return False

    if command == "retro":
        return launch_retroarch()

    if command == "screensaver":
        return launch_slideshow()

    if command == "close-apps":
        return close_tv_apps()

    if command.startswith(
        "close-"
    ):
        app_name = command.removeprefix(
            "close-"
        )

        return close_single_app(
            app_name
        )

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

    def _send_cors_headers(
        self
    ):
        self.send_header(
            "Access-Control-Allow-Origin",
            "*",
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET, POST, OPTIONS",
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type",
        )

    def do_OPTIONS(
        self
    ):
        self.send_response(
            204
        )

        self._send_cors_headers()

        self.end_headers()

    def do_GET(
        self
    ):
        if self.path == "/photos":
            photos = get_all_photos()

            response = {
                "photos": photos,
            }

            self.send_response(
                200
            )

            self.send_header(
                "Content-Type",
                "application/json",
            )

            self._send_cors_headers()

            self.end_headers()

            self.wfile.write(
                (
                    json.dumps(
                        response
                    )
                    + "\n"
                ).encode()
            )

            return

        self.send_response(
            404
        )

        self._send_cors_headers()

        self.end_headers()

    def do_POST(
        self
    ):
        if (
            self.path
            != "/command"
        ):
            self.send_response(
                404
            )

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
            data = json.loads(
                body
            )

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

            self.send_response(
                200
            )

            self.send_header(
                "Content-Type",
                "application/json",
            )

            self._send_cors_headers()

            self.end_headers()

            self.wfile.write(
                (
                    json.dumps(
                        response
                    )
                    + "\n"
                ).encode()
            )

        except json.JSONDecodeError:
            self.send_response(
                400
            )

            self._send_cors_headers()

            self.end_headers()


def run_http_server():
    server = ThreadingHTTPServer(
        (
            HOST,
            HTTP_PORT,
        ),
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

            elif command == "left-click":
                left_click()

            elif command == "right-click":
                right_click()

            elif command == "type-text":
                text = data.get(
                    "text",
                    "",
                )

                if text:
                    type_unicode_text(
                        text
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