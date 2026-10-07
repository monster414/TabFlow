# TabFlow

[简体中文](README.md) | [English](README_EN.md)

![Coded by Gemini 3.8 Flash](https://img.shields.io/badge/Coded%20by-Gemini%203.8%20Flash-4285F4?style=flat-square&logo=google&logoColor=white)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)

Lightweight Windows mouse gesture tool: **Hold Right Mouse Button + Scroll Wheel** to quickly switch tabs in browsers and applications.

---

## Features

- **Right-Click + Wheel Switching**: Scroll up to switch to the previous tab, scroll down to switch to the next tab. Supports continuous scrolling.
- **Accidental Trigger Prevention**:
  - Does not trigger page scrolling while gesturing; suppresses context menu on release.
  - Normal right-click still brings up native context menu instantly.
  - Automatically releases modifier keys (`Ctrl` / `Shift`) after gesture to prevent text selection stickiness.
- **Low Latency**: Based on Win32 low-level mouse hook (`WH_MOUSE_LL`). Mouse move events pass through directly with minimal resource usage.
- **Multi-App Support**:
  - Default presets for Chrome, Edge, Firefox, Brave, Opera, Vivaldi, Arc, Zen, etc.
  - Supports adding custom target processes (e.g. VS Code `code.exe`), or toggling Global Mode.
- **System Integration**:
  - Consistent icon across Windows Taskbar and Task Manager via `AppUserModelID`.
  - High-DPI scaling support.
  - Single-instance mutex guard, minimize to system tray, and Windows startup auto-launch.
- **Multi-Language Support**: Built-in Chinese and English interface, automatically matching system locale or toggled on the fly.

---

## How to Run

### 1. Standalone EXE (Recommended)
Run `dist\TabFlow.exe` directly (No Python environment required).

### 2. Run from Source
```bash
pip install -r requirements.txt
python main.py
```
Or double-click `run.bat` (silent launch without console window).

---

## Build

Double-click `build.bat` to package into a standalone single-file EXE.

The output executable is saved to `dist/TabFlow.exe`. The temporary compilation cache in `build/` can be safely removed anytime.

---

## Shortcut Modes

Switchable under the "Gestures & Hotkeys" tab:

| Mode | Switch Left (Previous) | Switch Right (Next) | Use Case |
| :--- | :--- | :--- | :--- |
| **Standard (Default)** | `Ctrl + Shift + Tab` | `Ctrl + Tab` | Most modern browsers & editors |
| **Directional** | `Ctrl + PageUp` | `Ctrl + PageDown` | Specific apps & custom browsers |

---

## Project Structure

```text
tab/
├── main.py             # Main GUI & application lifecycle
├── gesture_engine.py   # Mouse hook & gesture state machine
├── tray_manager.py     # System tray icon & menu
├── config_manager.py   # Config persistence & autostart registry
├── i18n.py             # Bilingual internationalization
├── app.ico             # Application icon
├── build.bat           # PyInstaller build script
├── run.bat             # Silent startup script
├── requirements.txt    # Python dependencies
├── .gitignore          # Git ignore configuration
├── LICENSE             # GNU GPL-3.0 License
├── README.md           # Chinese documentation
├── README_EN.md        # English documentation
└── dist/TabFlow.exe    # Standalone executable
```

---

## FAQ

- **Antivirus false positive?**
  The tool uses a low-level global mouse hook to capture wheel events and is packaged as a single binary via PyInstaller, which may trigger false alarms in some heuristic scanners. Simply add it to your whitelist.
- **Not working in certain apps?**
  If the target application (e.g. an editor running as Administrator) has elevated privileges, TabFlow must also run as Administrator to inject hotkeys due to Windows UIPI security restrictions.

---

## License

This project is licensed under the [GNU General Public License v3.0 (GPL-3.0)](LICENSE).
