from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import webbrowser

import pyautogui


HOST = "0.0.0.0"
PORT = 8765

MOUSE_SENSITIVITY = 1


def execute_command(command, data):
    if command == "netflix":
        webbrowser.open("https://www.netflix.com")
        return True

    if command == "mouse-move":
        dx = data.get("dx", 0)
        dy = data.get("dy", 0)

        pyautogui.moveRel(
            dx * MOUSE_SENSITIVITY,
            dy * MOUSE_SENSITIVITY,
            duration=0,
        )

        return True

    print(f"No action configured for: {command}")
    return False


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

        content_length = int(self.headers.get("Content-Length", 0))
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
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()

            self.wfile.write(
                (json.dumps(response) + "\n").encode()
            )

        except json.JSONDecodeError:
            self.send_response(400)
            self._send_cors_headers()
            self.end_headers()


def run_server():
    server = HTTPServer((HOST, PORT), ControlHandler)

    print(f"Control server running on port {PORT}")

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nStopping server...")

    finally:
        server.server_close()


if __name__ == "__main__":
    run_server()