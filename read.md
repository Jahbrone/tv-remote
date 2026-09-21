# Laptop TV / Kake Ruben

A DIY TV PC system that turns a Windows laptop into a remotely controlled streaming, gaming and media computer.

**Kake Ruben** is the Android remote used to control the TV PC over the local network.

Current release: **1.2.0**

---

# Overview

The system consists of three main parts:

1. **Windows control server**
   - Runs on the Acer TV PC.
   - Receives commands from the phone.
   - Controls mouse, keyboard, media, volume, windows and application launching.

2. **Web remote**
   - HTML/CSS/JavaScript interface.
   - Served directly from the Acer over the local network.
   - Provides the main Kake Ruben remote UI.

3. **Android app**
   - Native Android wrapper around the web remote.
   - Provides native functionality including haptic feedback, offline handling and lock-screen media controls.

---

# Current Setup

## TV PC

```text
Acer Aspire 5
Windows 11
IP: 192.168.1.187
```

The Acer is used closed-lid and connected to the TV.

## Network Services

```text
8000 = Remote web interface
8765 = HTTP control server
8766 = WebSocket real-time controls
```

## Android App

```text
Kake Ruben
Version 1.2.0
```

The phone and TV PC must be connected to the same local network.

---

# Project Structure

```text
tv-remote/
├── acer-control/
│   ├── albums.json
│   ├── NOTINUSEservermac.py
│   ├── photos.py
│   └── server.py
│
├── android-app/
│   ├── app/
│   ├── gradle/
│   ├── build.gradle.kts
│   ├── gradle.properties
│   ├── gradlew
│   ├── gradlew.bat
│   └── settings.gradle.kts
│
├── tv-remote/
│   ├── img/
│   ├── app.js
│   ├── index.html
│   ├── manifest.json
│   ├── slideshow.html
│   ├── style.css
│   ├── sw.js
│   └── webserver.py
│
├── .gitignore
└── read.md
```

Generated and local development directories such as `__pycache__`, `.gradle`, `.idea`, `.kotlin` and `local.properties` are omitted from this overview.

---

# Current Features

## Trackpad

The main remote contains a large touch trackpad.

Current controls include:

- Mouse movement
- Left click
- Right click
- Double-tap click
- Long-press click
- Two-finger scrolling
- Mouse click haptic feedback

Mouse movement is sent using WebSocket for responsive real-time control.

Current mouse settings on the Acer control server:

```python
MOUSE_SENSITIVITY = 3.0
SCROLL_SENSITIVITY = 0.15
```

---

# Keyboard

Kake can open the Android software keyboard and send keyboard input to the Acer.

Current functionality includes:

- Normal text input
- Enter
- Backspace
- Keyboard remains open while interacting with the trackpad and remote controls

The keyboard uses a hidden input field in the web interface to capture Android keyboard input.

---

# App Launching

Kake can launch and switch between applications and services including:

- Netflix
- Disney+
- Max
- YouTube
- YLE
- Web browser
- Steam
- RetroArch
- Photos

Streaming services are launched using dedicated Microsoft Edge profiles.

If a supported application is already running, the control server attempts to bring its existing window to the foreground rather than opening unnecessary additional copies.

---

# App Closing

Kake includes a **Close Apps** mode.

When enabled, supported application buttons switch from launch behaviour to close behaviour.

The remote UI changes appearance while Close Apps mode is active so that the current mode is obvious.

---

# Media and Window Controls

The main remote includes controls for:

- Back
- Fullscreen
- Play / Pause
- Minimise
- Volume up
- Volume down
- Desktop

The Back command sends:

```text
Alt + Left
```

to Windows.

This provides browser-style navigation in supported applications such as Edge.

---

# Android Lock-Screen Controls

Kake Ruben includes native Android media controls.

The lock-screen/media notification provides:

```text
Volume Down | Play/Pause | Volume Up
```

These controls communicate directly with the Acer control server and can be used without reopening the main Kake interface.

The Android app uses:

- Foreground service
- Android MediaSession
- Media-style notification

The MediaSession is refreshed when Kake is opened to improve reliability of the Android lock-screen media controls.

Compatible Android and Wear OS devices may also expose the media session to connected watches.

## Play/Pause Behaviour

Kake does not currently receive the Acer's actual playback state.

Because of this, Play/Pause is intentionally implemented as a simple **toggle** rather than attempting to display whether the Acer is currently playing or paused.

The lock-screen control therefore uses a combined Play/Pause symbol.

---

# Haptic Feedback

Native Android haptic feedback is available for mouse clicks.

The web interface communicates with the Android app through a JavaScript interface:

```text
AndroidHaptics
```

Haptic feedback is triggered for actual mouse clicks, including trackpad click actions.

Mouse movement and scrolling do not trigger haptics.

---

# Connection Handling

When Kake Ruben opens, the Android app checks whether the Acer web server is reachable.

If the Acer is online:

```text
Kake loads the remote interface.
```

If the Acer cannot be reached:

```text
Kake displays an offline screen with a retry button.
```

The web remote also contains a connection indicator showing the state of the WebSocket connection.

---

# Windows Control Server

The main Acer control server is:

```text
acer-control/server.py
```

It provides two services:

```text
HTTP:      port 8765
WebSocket: port 8766
```

## HTTP

HTTP is used for discrete commands such as:

- Application launching
- Application closing
- Left click
- Right click
- Keyboard commands
- Play/Pause
- Volume
- Back
- Fullscreen
- Minimise
- Desktop

## WebSocket

WebSocket is used for real-time controls where low latency is more important, including:

- Mouse movement
- Scrolling

---

# Remote Web Server

The web remote is located in:

```text
tv-remote/
```

and is served on:

```text
Port 8000
```

The current Acer address is:

```text
http://192.168.1.187:8000/
```

The JavaScript remote communicates with:

```js
const SERVER_URL =
  "http://192.168.1.187:8765";

const WEBSOCKET_URL =
  "ws://192.168.1.187:8766";
```

---

# Running the Servers Manually

The Acer normally starts the required services automatically.

They can also be started manually for development or troubleshooting.

## Control Server

From the project root:

```bash
python acer-control/server.py
```

The expected output includes:

```text
HTTP control server running on port 8765
WebSocket server running on port 8766
```

After changing:

```text
acer-control/server.py
```

restart the control server for the changes to take effect.

---

# Remote Web Server

The web interface can be served using the project's web server or a basic Python HTTP server.

For example:

```bash
python -m http.server 8000 --bind 0.0.0.0 --directory tv-remote
```

Changes to:

```text
app.js
index.html
style.css
```

normally do not require the web server itself to be restarted.

Reloading/reopening Kake will load the updated files from the Acer.

---

# Automatic Startup

The Acer uses Windows Task Scheduler to automatically start the required Laptop TV services.

The control server is configured to start automatically and restart if required.

This means normal TV use should not require manually opening a terminal or starting the Python server.

---

# Android App

The Android project is located at:

```text
android-app/
```

The app is developed using Android Studio.

The native Android app loads:

```text
http://192.168.1.187:8000
```

inside an Android WebView.

Native Android code provides functionality that is unavailable or less reliable from the web interface alone, including:

- Haptic feedback
- Foreground media service
- MediaSession
- Lock-screen media controls
- Offline detection
- Retry handling

---

# Web Changes vs Android Changes

The main remote interface is hosted by the Acer rather than bundled permanently into the Android APK.

Therefore changes to:

```text
app.js
index.html
style.css
```

generally **do not require a new APK**.

The normal process is:

```text
Change web files on Mac
↓
Commit and push
↓
Pull latest main on Acer
↓
Reopen/refresh Kake
```

Changes to native Android functionality inside:

```text
android-app/
```

require rebuilding and reinstalling the Android application.

---

# Building Kake Ruben

Current release:

```text
Kake Ruben 1.2.0
```

To create a signed release APK in Android Studio:

```text
Build
→ Generate Signed App Bundle or APK
→ APK
→ Select existing Kake Ruben keystore
→ release
→ Build
```

The generated APK can be found under the Android build output, typically:

```text
android-app/app/build/outputs/apk/release/
```

The release APK can then be renamed, for example:

```text
Kake-Ruben-1.2.0.apk
```

---

# Signing Key

Future versions of Kake Ruben must use the existing Kake Ruben signing keystore.

Using the same signing key allows Android to install a new release as an update over the existing application.

The signing keystore should be backed up somewhere safe.

It should **never be committed to Git**.

---

# Git Workflow

Development work is normally done on a separate branch.

Typical workflow:

```text
main
↓
Create update/feature branch
↓
Make changes
↓
Test
↓
Commit
↓
Push
↓
Merge into main
↓
Push main
↓
Pull main on Acer
↓
Final test
```

`main` should contain the current stable version.

Old local and remote feature branches can be deleted after they have been successfully merged and tested.

---

# Updating the Acer

After changes have been merged into `main`, update the Acer with:

```bash
git checkout main
git pull
```

Changes to the web remote become available immediately after the Acer has pulled the updated files.

Changes to `server.py` require the control server to be restarted.

---

# Known Issues

## YouTube Play/Pause

Play/Pause can occasionally be unreliable when YouTube is the first media application used after startup.

It appears to behave normally after another Edge media session, such as Netflix, has been active.

The issue affects both:

- Main Kake Play/Pause control
- Android lock-screen Play/Pause control

Because both controls exhibit the same behaviour, the issue is likely related to Windows/Edge media-session handling rather than the Android lock-screen implementation.

---

## Wake on LAN

Wake on LAN from Windows S3 sleep is not currently reliable.

The Acer can sleep normally, but remote network wake functionality still requires further investigation.

---

# Version History

## 1.2.0

Current stable release.

Changes include:

- Added Back button
- Added native Android lock-screen media controls
- Added Volume Down / Play-Pause / Volume Up lock-screen actions
- Added Android MediaSession support
- Added MediaSession refresh behaviour
- Added mouse-click haptic feedback
- Improved keyboard behaviour
- Keyboard now remains open while using remote controls
- Moved keyboard control into the mouse-button row
- Added combined Play/Pause lock-screen control
- Improved Android media-control reliability
- General UI and reliability improvements

---

# Future / Open Items

Potential future work includes:

- Improve YouTube Play/Pause reliability
- Improve Wake on LAN reliability
- Reverse/configurable scroll direction
- Improve keyboard symbol/international keyboard handling
- Google Photos/slideshow improvements
- Further Wear OS remote functionality

---

# Important

Laptop TV is currently configured specifically for the home Acer TV PC.

The system contains local IP addresses and Windows-specific application paths.

Moving Kake to another computer or network would require configuration changes for:

- Host IP address
- Application paths
- Streaming profiles
- Server startup
- Platform-specific computer controls

The project is intended primarily for use over a trusted local home network.