# Laptop TV

Phone remote and control service for the Laptop TV project.

## Project Structure

```text
laptop-tv/
├── acer-control/
│   └── server.py
├── tv-remote/
│   ├── icons/
│   ├── app.js
│   ├── index.html
│   └── style.css
├── .venv/
├── .gitignore
└── README.md
```

---

# Development Setup

Two servers need to be running during development:

1. CONTROL SERVER
2. REMOTE WEB

Keep each running in its own VS Code terminal.

---

## CONTROL SERVER

The control server receives commands from the phone and controls the computer.

### Start

If the virtual environment is NOT active:

```bash
source .venv/bin/activate
python acer-control/server.py
```

If the terminal already starts with `(.venv)`:

```bash
python acer-control/server.py
```

You should see:

```text
HTTP control server running on port 8765
WebSocket server running on port 8766
```

### Stop

Press:

```text
Ctrl + C
```

### Restart

Press:

```text
Ctrl + C
```

Then run:

```bash
python acer-control/server.py
```

If `(.venv)` is no longer showing, run this first:

```bash
source .venv/bin/activate
```

---

## REMOTE WEB

This serves the HTML/CSS/JavaScript phone remote.

### Start

Open a separate VS Code terminal and run:

```bash
python3 -m http.server 8000 --bind 0.0.0.0 --directory tv-remote
```

You should see:

```text
Serving HTTP on 0.0.0.0 port 8000
```

### Stop

Press:

```text
Ctrl + C
```

### Restart

Press:

```text
Ctrl + C
```

Then run:

```bash
python3 -m http.server 8000 --bind 0.0.0.0 --directory tv-remote
```

You normally DO NOT need to restart this server after changing HTML, CSS or JavaScript.

Just refresh the page on the phone.

---

# Phone Remote

The current Mac IP is:

```text
192.168.1.93
```

Open this on the phone:

```text
http://192.168.1.93:8000/
```

The phone and computer must be connected to the same local Wi-Fi network.

---

# Server Ports

```text
8000 = Remote webpage
8765 = HTTP commands
8766 = WebSocket real-time controls
```

HTTP is used for commands such as:

- Netflix
- Left click
- Right click
- App launching
- Other button commands

WebSocket is used for real-time controls such as:

- Mouse movement
- Scrolling

---

# Check Mac IP Address

The Mac's local IP address can change.

Check it with:

```bash
ipconfig getifaddr en0
```

If the IP changes, update the URLs in:

```text
tv-remote/app.js
```

For example:

```js
const SERVER_URL = "http://192.168.1.93:8765";
const WEBSOCKET_URL = "ws://192.168.1.93:8766";
```

Then use the new IP on the phone:

```text
http://NEW-IP:8000/
```

---

# Current Working Features

- Phone connects to computer over local Wi-Fi
- Netflix button opens Netflix
- WebSocket connection
- Trackpad controls mouse
- Left click
- Right click
- Two-finger scroll

---

# Useful Git Commands

Check changes:

```bash
git status
```

Stage changes:

```bash
git add -A
```

Commit:

```bash
git commit -m "Describe the change"
```

Push:

```bash
git push
```

---

# Python Environment

The project uses a Python virtual environment:

```text
.venv/
```

Activate it with:

```bash
source .venv/bin/activate
```

Installed Python dependencies currently include:

- pyautogui
- websockets
- PyObjC / Quartz dependencies for macOS development

The `.venv` directory should NOT be committed to Git.

---

# Important

During development:

- Keep CONTROL SERVER running.
- Keep REMOTE WEB running.
- Restart CONTROL SERVER after changing `server.py`.
- Refresh the phone page after changing `app.js`, `index.html` or `style.css`.
- You normally do not need to restart REMOTE WEB after frontend changes.