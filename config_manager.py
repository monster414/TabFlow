import json
import os
import sys
import winreg

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
REG_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "TabFlow_MouseSwitcher"

DEFAULT_BROWSERS = [
    "chrome.exe",
    "msedge.exe",
    "firefox.exe",
    "brave.exe",
    "opera.exe",
    "vivaldi.exe",
    "360chrome.exe",
    "360se.exe",
    "qqbrowser.exe",
    "sogouexplorer.exe",
    "browser.exe",
    "arc.exe",
    "zen.exe",
    "thorium.exe",
    "floorp.exe",
    "centbrowser.exe",
]

from i18n import detect_system_language

DEFAULT_CONFIG = {
    "enabled": True,
    "shortcut_mode": "ctrl_tab", # "ctrl_tab" or "ctrl_page"
    "reverse_scroll": False,
    "wheel_sensitivity": 120,
    "all_apps_mode": False,
    "minimize_to_tray": True,
    "autostart": False,
    "language": "zh", # "zh" or "en"
    "target_browsers": DEFAULT_BROWSERS,
}

class ConfigManager:
    def __init__(self):
        self.config = dict(DEFAULT_CONFIG)
        self.config["language"] = detect_system_language()
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.config.update(data)
            except Exception as e:
                print(f"[ConfigManager] Failed to load config: {e}")
        else:
            self.save()
        self._check_autostart_registry()

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[ConfigManager] Failed to save config: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()

    def _check_autostart_registry(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_READ) as key:
                val, _ = winreg.QueryValueEx(key, APP_NAME)
                self.config["autostart"] = bool(val)
        except FileNotFoundError:
            self.config["autostart"] = False
        except Exception:
            pass

    def set_autostart(self, enable: bool):
        self.config["autostart"] = enable
        self.save()
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
                if enable:
                    if getattr(sys, 'frozen', False):
                        cmd = f'"{sys.executable}"'
                    else:
                        base_dir = os.path.dirname(os.path.abspath(__file__))
                        run_bat = os.path.join(base_dir, "run.bat")
                        if os.path.exists(run_bat):
                            cmd = f'"{run_bat}"'
                        else:
                            python_exe = sys.executable.replace("python.exe", "pythonw.exe")
                            main_py = os.path.join(base_dir, "main.py")
                            cmd = f'"{python_exe}" "{main_py}"'
                    winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
                else:
                    try:
                        winreg.DeleteValue(key, APP_NAME)
                    except FileNotFoundError:
                        pass
        except Exception as e:
            print(f"[ConfigManager] Failed to update autostart registry: {e}")
