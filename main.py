import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import threading
import time
import subprocess

from config_manager import ConfigManager
from gesture_engine import GestureEngine, HookService
from tray_manager import TrayManager
from i18n import I18nManager

# Color Palette (Modern Slate & Indigo Theme)
THEME = {
    "bg": "#0f172a",          # Slate 900
    "card": "#1e293b",        # Slate 800
    "card_border": "#334155", # Slate 700
    "input_bg": "#0f172a",
    "primary": "#6366f1",     # Indigo 500
    "primary_hover": "#4f46e5",
    "success": "#10b981",     # Emerald 500
    "success_bg": "#064e3b",
    "warning": "#f59e0b",     # Amber 500
    "warning_bg": "#78350f",
    "danger": "#ef4444",      # Red 500
    "text_title": "#f8fafc",  # White
    "text_body": "#e2e8f0",   # Slate 200
    "text_muted": "#94a3b8",  # Slate 400
    "highlight": "#38bdf8",   # Sky blue
}

POPULAR_BROWSERS = [
    ("Google Chrome", "chrome.exe"),
    ("Microsoft Edge", "msedge.exe"),
    ("Mozilla Firefox", "firefox.exe"),
    ("Brave Browser", "brave.exe"),
    ("Opera Browser", "opera.exe"),
    ("Vivaldi", "vivaldi.exe"),
    ("360安全浏览器", "360se.exe"),
    ("360极速浏览器", "360chrome.exe"),
    ("QQ浏览器", "qqbrowser.exe"),
    ("搜狗浏览器", "sogouexplorer.exe"),
    ("Cent Browser", "centbrowser.exe"),
    ("Arc Browser", "arc.exe"),
    ("Zen Browser", "zen.exe"),
    ("Floorp Browser", "floorp.exe"),
]

class TabFlowApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Managers & Config
        self.config_mgr = ConfigManager()
        self.i18n = I18nManager(self.config_mgr.get("language", "zh"))
        
        self.title(self.i18n.t("app_title"))
        self.geometry("660x780")
        self.minsize(580, 700)
        self.configure(bg=THEME["bg"])

        # 查找应用图标 (优先支持 PyInstaller 单文件 _MEIPASS 目录，兼顾 exe 目录及源码目录)
        ico_candidates = []
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                ico_candidates.append(os.path.join(sys._MEIPASS, "app.ico"))
            ico_candidates.append(os.path.join(os.path.dirname(os.path.abspath(sys.executable)), "app.ico"))
        else:
            ico_candidates.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.ico"))

        for ico in ico_candidates:
            if os.path.exists(ico):
                try:
                    self.iconbitmap(default=ico)
                    break
                except Exception:
                    try:
                        self.iconbitmap(ico)
                        break
                    except Exception:
                        pass

        self.engine = GestureEngine(self.config_mgr.config)
        self.hook_service = HookService(self.engine)
        
        # Engine callbacks for live UI feedback
        self.engine.on_switch_callback = self._on_gesture_switched
        self.engine.on_state_callback = self._on_gesture_state_changed

        # Tray Manager
        self.tray = TrayManager(
            on_show=self._show_window_from_tray,
            on_toggle=self._toggle_service_from_tray,
            on_exit=self._exit_app,
            is_enabled=self.config_mgr.get("enabled", True),
            i18n=self.i18n
        )

        # UI State variables
        self.var_enabled = tk.BooleanVar(value=self.config_mgr.get("enabled", True))
        self.var_shortcut_mode = tk.StringVar(value=self.config_mgr.get("shortcut_mode", "ctrl_tab"))
        self.var_reverse_scroll = tk.BooleanVar(value=self.config_mgr.get("reverse_scroll", False))
        self.var_all_apps = tk.BooleanVar(value=self.config_mgr.get("all_apps_mode", False))
        self.var_min_tray = tk.BooleanVar(value=self.config_mgr.get("minimize_to_tray", True))
        self.var_autostart = tk.BooleanVar(value=self.config_mgr.get("autostart", False))
        self.var_sensitivity = tk.IntVar(value=self.config_mgr.get("wheel_sensitivity", 120))
        self.var_language = tk.StringVar(value=self.i18n.lang)

        # Browser checkboxes
        self.browser_vars = {}
        active_browsers = set(b.lower() for b in self.config_mgr.get("target_browsers", []))
        for _, exe in POPULAR_BROWSERS:
            self.browser_vars[exe] = tk.BooleanVar(value=exe.lower() in active_browsers)

        # Build UI
        self._init_styles()
        self._build_header()
        self._build_live_card()
        self._build_tabs()
        self._build_bottom_bar()

        # Window protocol
        self.protocol("WM_DELETE_WINDOW", self._on_close_window)

        # Start hook service
        if self.var_enabled.get():
            self._start_hook()

        # Start Tray
        self.tray.start()

    def _init_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Style Notebook
        style.configure("TNotebook", background=THEME["bg"], borderwidth=0)
        style.configure("TNotebook.Tab", background=THEME["card"], foreground=THEME["text_muted"],
                        padding=[16, 8], font=("Microsoft YaHei UI", 10, "bold"), borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", THEME["primary"])],
                  foreground=[("selected", "#ffffff")])

    def _build_header(self):
        header_frame = tk.Frame(self, bg=THEME["bg"])
        header_frame.pack(fill=tk.X, padx=24, pady=(20, 12))

        # Title & subtitle
        title_box = tk.Frame(header_frame, bg=THEME["bg"])
        title_box.pack(side=tk.LEFT)

        self.lbl_app_title = tk.Label(
            title_box, text=self.i18n.t("header_title"), font=("Microsoft YaHei UI", 18, "bold"),
            bg=THEME["bg"], fg=THEME["text_title"]
        )
        self.lbl_app_title.pack(anchor=tk.W)

        self.lbl_app_subtitle = tk.Label(
            title_box, text=self.i18n.t("header_subtitle"), font=("Microsoft YaHei UI", 9),
            bg=THEME["bg"], fg=THEME["text_muted"]
        )
        self.lbl_app_subtitle.pack(anchor=tk.W, pady=(2, 0))

        # Controls box (Language Toggle + Status Pill + Big Toggle Button)
        toggle_box = tk.Frame(header_frame, bg=THEME["bg"])
        toggle_box.pack(side=tk.RIGHT)

        # Language toggle button in header
        self.btn_lang = tk.Button(
            toggle_box,
            text="English" if self.i18n.lang == "zh" else "中文",
            font=("Microsoft YaHei UI", 9, "bold"),
            bg=THEME["card"], fg=THEME["highlight"],
            activebackground=THEME["card_border"], activeforeground=THEME["text_title"],
            relief=tk.FLAT, padx=10, pady=4, cursor="hand2",
            command=self._toggle_language
        )
        self.btn_lang.pack(side=tk.LEFT, padx=(0, 10))

        self.status_pill = tk.Label(
            toggle_box,
            text=self.i18n.t("status_running") if self.var_enabled.get() else self.i18n.t("status_paused"),
            font=("Microsoft YaHei UI", 10, "bold"),
            bg=THEME["success_bg"] if self.var_enabled.get() else THEME["warning_bg"],
            fg=THEME["success"] if self.var_enabled.get() else THEME["warning"],
            padx=12, pady=4, relief=tk.FLAT
        )
        self.status_pill.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_toggle = tk.Button(
            toggle_box,
            text=self.i18n.t("btn_pause") if self.var_enabled.get() else self.i18n.t("btn_resume"),
            font=("Microsoft YaHei UI", 9, "bold"),
            bg=THEME["warning"] if self.var_enabled.get() else THEME["success"],
            fg="#ffffff", activebackground="#475569", activeforeground="#ffffff",
            relief=tk.FLAT, padx=14, pady=5, cursor="hand2",
            command=self._toggle_service
        )
        self.btn_toggle.pack(side=tk.LEFT)

    def _build_live_card(self):
        # Card Container
        card = tk.Frame(self, bg=THEME["card"], bd=1, relief=tk.SOLID, highlightbackground=THEME["card_border"])
        card.pack(fill=tk.X, padx=24, pady=(0, 14))

        # Header of card
        self.lbl_card_title = tk.Label(
            card, text=self.i18n.t("card_monitor_title"), font=("Microsoft YaHei UI", 10, "bold"),
            bg=THEME["card"], fg=THEME["text_body"]
        )
        self.lbl_card_title.pack(anchor=tk.W, padx=16, pady=(12, 8))

        # Direction indicator boxes
        dir_frame = tk.Frame(card, bg=THEME["card"])
        dir_frame.pack(fill=tk.X, padx=16, pady=(0, 12))

        # Left Indicator
        self.box_left = tk.Label(
            dir_frame, text=self.i18n.t("box_scroll_up"),
            font=("Microsoft YaHei UI", 9, "bold"),
            bg=THEME["input_bg"], fg=THEME["text_muted"],
            padx=10, pady=10, relief=tk.GROOVE
        )
        self.box_left.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 6))

        # Right Indicator
        self.box_right = tk.Label(
            dir_frame, text=self.i18n.t("box_scroll_down"),
            font=("Microsoft YaHei UI", 9, "bold"),
            bg=THEME["input_bg"], fg=THEME["text_muted"],
            padx=10, pady=10, relief=tk.GROOVE
        )
        self.box_right.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=(6, 0))

        # Stats bar below indicators
        stats_frame = tk.Frame(card, bg=THEME["card"])
        stats_frame.pack(fill=tk.X, padx=16, pady=(0, 12))

        self.lbl_rbutton_state = tk.Label(
            stats_frame, text=self.i18n.t("rbutton_released"), font=("Microsoft YaHei UI", 9),
            bg=THEME["card"], fg=THEME["text_muted"]
        )
        self.lbl_rbutton_state.pack(side=tk.LEFT)

        self.lbl_current_proc = tk.Label(
            stats_frame, text=self.i18n.t("target_none"), font=("Microsoft YaHei UI", 9),
            bg=THEME["card"], fg=THEME["text_muted"]
        )
        self.lbl_current_proc.pack(side=tk.LEFT, padx=(20, 0))

        self.lbl_counter = tk.Label(
            stats_frame, text=self.i18n.t("switched_count", count=0), font=("Microsoft YaHei UI", 9, "bold"),
            bg=THEME["card"], fg=THEME["highlight"]
        )
        self.lbl_counter.pack(side=tk.RIGHT)

    def _build_tabs(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 14))

        # Tab 1: Gestures & Shortcuts
        self.tab_settings = tk.Frame(self.notebook, bg=THEME["card"])
        self.notebook.add(self.tab_settings, text=self.i18n.t("tab_settings"))
        self._init_tab_settings()

        # Tab 2: Target Browsers
        self.tab_browsers = tk.Frame(self.notebook, bg=THEME["card"])
        self.notebook.add(self.tab_browsers, text=self.i18n.t("tab_browsers"))
        self._init_tab_browsers()

        # Tab 3: System & Autostart
        self.tab_system = tk.Frame(self.notebook, bg=THEME["card"])
        self.notebook.add(self.tab_system, text=self.i18n.t("tab_system"))
        self._init_tab_system()

    def _init_tab_settings(self):
        frame = self.tab_settings

        # Shortcut Mode Option
        self.lbl_group1 = tk.Label(
            frame, text=self.i18n.t("group_shortcut_mode"), font=("Microsoft YaHei UI", 10, "bold"),
            bg=THEME["card"], fg=THEME["text_title"]
        )
        self.lbl_group1.pack(anchor=tk.W, padx=20, pady=(16, 6))

        self.rb1 = tk.Radiobutton(
            frame, text=self.i18n.t("mode_ctrl_tab"),
            variable=self.var_shortcut_mode, value="ctrl_tab",
            font=("Microsoft YaHei UI", 9), bg=THEME["card"], fg=THEME["text_body"],
            selectcolor=THEME["input_bg"], activebackground=THEME["card"], activeforeground=THEME["text_title"]
        )
        self.rb1.pack(anchor=tk.W, padx=24, pady=3)

        self.rb2 = tk.Radiobutton(
            frame, text=self.i18n.t("mode_ctrl_page"),
            variable=self.var_shortcut_mode, value="ctrl_page",
            font=("Microsoft YaHei UI", 9), bg=THEME["card"], fg=THEME["text_body"],
            selectcolor=THEME["input_bg"], activebackground=THEME["card"], activeforeground=THEME["text_title"]
        )
        self.rb2.pack(anchor=tk.W, padx=24, pady=3)

        # Divider
        tk.Frame(frame, height=1, bg=THEME["card_border"]).pack(fill=tk.X, padx=20, pady=12)

        # Scroll Direction
        self.lbl_group2 = tk.Label(
            frame, text=self.i18n.t("group_scroll"), font=("Microsoft YaHei UI", 10, "bold"),
            bg=THEME["card"], fg=THEME["text_title"]
        )
        self.lbl_group2.pack(anchor=tk.W, padx=20, pady=(4, 6))

        self.cb_rev = tk.Checkbutton(
            frame, text=self.i18n.t("chk_reverse_scroll"),
            variable=self.var_reverse_scroll,
            font=("Microsoft YaHei UI", 9), bg=THEME["card"], fg=THEME["text_body"],
            selectcolor=THEME["input_bg"], activebackground=THEME["card"], activeforeground=THEME["text_title"]
        )
        self.cb_rev.pack(anchor=tk.W, padx=24, pady=3)

        # Sensitivity description
        sens_box = tk.Frame(frame, bg=THEME["card"])
        sens_box.pack(anchor=tk.W, padx=24, pady=6)

        self.lbl_sens = tk.Label(
            sens_box, text=self.i18n.t("lbl_sensitivity"), font=("Microsoft YaHei UI", 9),
            bg=THEME["card"], fg=THEME["text_body"]
        )
        self.lbl_sens.pack(side=tk.LEFT)

        self.scale_sens = tk.Scale(
            sens_box, from_=60, to=240, resolution=30, orient=tk.HORIZONTAL,
            variable=self.var_sensitivity, length=180,
            bg=THEME["card"], fg=THEME["text_body"], highlightthickness=0,
            troughcolor=THEME["input_bg"], activebackground=THEME["primary"]
        )
        self.scale_sens.pack(side=tk.LEFT, padx=8)

        self.lbl_sens_tip = tk.Label(
            sens_box, text=self.i18n.t("lbl_sens_tip"), font=("Microsoft YaHei UI", 8),
            bg=THEME["card"], fg=THEME["text_muted"]
        )
        self.lbl_sens_tip.pack(side=tk.LEFT)

        # Divider
        tk.Frame(frame, height=1, bg=THEME["card_border"]).pack(fill=tk.X, padx=20, pady=12)

        # Gesture Scope
        self.lbl_group3 = tk.Label(
            frame, text=self.i18n.t("group_scope"), font=("Microsoft YaHei UI", 10, "bold"),
            bg=THEME["card"], fg=THEME["text_title"]
        )
        self.lbl_group3.pack(anchor=tk.W, padx=20, pady=(4, 6))

        self.cb_all = tk.Checkbutton(
            frame, text=self.i18n.t("chk_all_apps"),
            variable=self.var_all_apps,
            font=("Microsoft YaHei UI", 9), bg=THEME["card"], fg=THEME["text_body"],
            selectcolor=THEME["input_bg"], activebackground=THEME["card"], activeforeground=THEME["text_title"]
        )
        self.cb_all.pack(anchor=tk.W, padx=24, pady=3)

    def _init_tab_browsers(self):
        frame = self.tab_browsers

        top_bar = tk.Frame(frame, bg=THEME["card"])
        top_bar.pack(fill=tk.X, padx=20, pady=(14, 8))

        self.lbl_browser_title = tk.Label(
            top_bar, text=self.i18n.t("lbl_browser_list"), font=("Microsoft YaHei UI", 10, "bold"),
            bg=THEME["card"], fg=THEME["text_title"]
        )
        self.lbl_browser_title.pack(side=tk.LEFT)

        self.btn_scan = tk.Button(
            top_bar, text=self.i18n.t("btn_scan"), font=("Microsoft YaHei UI", 9),
            bg=THEME["input_bg"], fg=THEME["highlight"], relief=tk.FLAT,
            padx=10, pady=3, cursor="hand2", command=self._scan_running_browsers
        )
        self.btn_scan.pack(side=tk.RIGHT)

        # Scrollable area for browser list
        list_container = tk.Frame(frame, bg=THEME["card"])
        list_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

        # Grid of checkboxes (2 columns)
        grid_frame = tk.Frame(list_container, bg=THEME["card"])
        grid_frame.pack(fill=tk.BOTH, expand=True)

        for i, (name, exe) in enumerate(POPULAR_BROWSERS):
            row = i // 2
            col = i % 2
            cb = tk.Checkbutton(
                grid_frame, text=f"{name} ({exe})",
                variable=self.browser_vars[exe],
                font=("Microsoft YaHei UI", 9), bg=THEME["card"], fg=THEME["text_body"],
                selectcolor=THEME["input_bg"], activebackground=THEME["card"], activeforeground=THEME["text_title"]
            )
            cb.grid(row=row, column=col, sticky=tk.W, padx=(0 if col == 0 else 16), pady=3)

        # Custom processes section
        custom_frame = tk.Frame(frame, bg=THEME["card"])
        custom_frame.pack(fill=tk.X, padx=20, pady=(6, 12))

        self.lbl_custom = tk.Label(
            custom_frame, text=self.i18n.t("lbl_custom_proc"),
            font=("Microsoft YaHei UI", 9, "bold"), bg=THEME["card"], fg=THEME["text_title"]
        )
        self.lbl_custom.pack(anchor=tk.W, pady=(0, 4))

        input_row = tk.Frame(custom_frame, bg=THEME["card"])
        input_row.pack(fill=tk.X)

        self.entry_custom_exe = tk.Entry(
            input_row, font=("Microsoft YaHei UI", 9),
            bg=THEME["input_bg"], fg=THEME["text_title"],
            insertbackground="#ffffff", relief=tk.FLAT
        )
        self.entry_custom_exe.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=(0, 8))

        self.btn_add = tk.Button(
            input_row, text=self.i18n.t("btn_add"), font=("Microsoft YaHei UI", 9, "bold"),
            bg=THEME["primary"], fg="#ffffff", relief=tk.FLAT, padx=12, pady=4,
            cursor="hand2", command=self._add_custom_browser
        )
        self.btn_add.pack(side=tk.RIGHT)

        # Custom list display
        self.lbl_custom_list = tk.Label(
            custom_frame, text=self._get_custom_browsers_display(),
            font=("Microsoft YaHei UI", 8), bg=THEME["card"], fg=THEME["text_muted"],
            wraplength=540, justify=tk.LEFT
        )
        self.lbl_custom_list.pack(anchor=tk.W, pady=(4, 0))

    def _init_tab_system(self):
        frame = self.tab_system

        self.lbl_system_group = tk.Label(
            frame, text=self.i18n.t("group_preference"), font=("Microsoft YaHei UI", 10, "bold"),
            bg=THEME["card"], fg=THEME["text_title"]
        )
        self.lbl_system_group.pack(anchor=tk.W, padx=20, pady=(16, 8))

        self.cb_min = tk.Checkbutton(
            frame, text=self.i18n.t("chk_minimize_tray"),
            variable=self.var_min_tray,
            font=("Microsoft YaHei UI", 9), bg=THEME["card"], fg=THEME["text_body"],
            selectcolor=THEME["input_bg"], activebackground=THEME["card"], activeforeground=THEME["text_title"]
        )
        self.cb_min.pack(anchor=tk.W, padx=24, pady=4)

        self.cb_auto = tk.Checkbutton(
            frame, text=self.i18n.t("chk_autostart"),
            variable=self.var_autostart,
            font=("Microsoft YaHei UI", 9), bg=THEME["card"], fg=THEME["text_body"],
            selectcolor=THEME["input_bg"], activebackground=THEME["card"], activeforeground=THEME["text_title"],
            command=self._on_toggle_autostart
        )
        self.cb_auto.pack(anchor=tk.W, padx=24, pady=4)

        # Language selection row
        lang_box = tk.Frame(frame, bg=THEME["card"])
        lang_box.pack(anchor=tk.W, padx=24, pady=6)

        self.lbl_lang_setting = tk.Label(
            lang_box, text=self.i18n.t("lbl_language"), font=("Microsoft YaHei UI", 9),
            bg=THEME["card"], fg=THEME["text_body"]
        )
        self.lbl_lang_setting.pack(side=tk.LEFT)

        self.rb_lang_zh = tk.Radiobutton(
            lang_box, text="简体中文", variable=self.var_language, value="zh",
            command=lambda: self._set_language("zh"),
            font=("Microsoft YaHei UI", 9), bg=THEME["card"], fg=THEME["text_body"],
            selectcolor=THEME["input_bg"], activebackground=THEME["card"], activeforeground=THEME["text_title"]
        )
        self.rb_lang_zh.pack(side=tk.LEFT, padx=(6, 14))

        self.rb_lang_en = tk.Radiobutton(
            lang_box, text="English", variable=self.var_language, value="en",
            command=lambda: self._set_language("en"),
            font=("Microsoft YaHei UI", 9), bg=THEME["card"], fg=THEME["text_body"],
            selectcolor=THEME["input_bg"], activebackground=THEME["card"], activeforeground=THEME["text_title"]
        )
        self.rb_lang_en.pack(side=tk.LEFT)

        # Info Guide Box
        guide_box = tk.Frame(frame, bg=THEME["input_bg"], padx=14, pady=12)
        guide_box.pack(fill=tk.X, padx=24, pady=(16, 0))

        self.lbl_guide_title = tk.Label(
            guide_box, text=self.i18n.t("guide_title"), font=("Microsoft YaHei UI", 9, "bold"),
            bg=THEME["input_bg"], fg=THEME["highlight"]
        )
        self.lbl_guide_title.pack(anchor=tk.W)

        self.tip_labels = []
        tips = [
            self.i18n.t("tip_1"),
            self.i18n.t("tip_2"),
            self.i18n.t("tip_3"),
            self.i18n.t("tip_4"),
            self.i18n.t("tip_5"),
        ]
        for tip in tips:
            lbl = tk.Label(
                guide_box, text=tip, font=("Microsoft YaHei UI", 8),
                bg=THEME["input_bg"], fg=THEME["text_muted"], anchor=tk.W
            )
            lbl.pack(anchor=tk.W, pady=2)
            self.tip_labels.append(lbl)

    def _build_bottom_bar(self):
        bar = tk.Frame(self, bg=THEME["bg"])
        bar.pack(fill=tk.X, padx=24, pady=(0, 20))

        self.btn_min = tk.Button(
            bar, text=self.i18n.t("btn_min_tray"), font=("Microsoft YaHei UI", 9),
            bg=THEME["card"], fg=THEME["text_body"], relief=tk.FLAT,
            padx=14, pady=6, cursor="hand2", command=self._hide_to_tray
        )
        self.btn_min.pack(side=tk.LEFT)

        self.btn_exit = tk.Button(
            bar, text=self.i18n.t("btn_exit"), font=("Microsoft YaHei UI", 9),
            bg=THEME["card"], fg=THEME["danger"], relief=tk.FLAT,
            padx=14, pady=6, cursor="hand2", command=self._exit_app
        )
        self.btn_exit.pack(side=tk.LEFT, padx=(10, 0))

        self.btn_save = tk.Button(
            bar, text=self.i18n.t("btn_save"), font=("Microsoft YaHei UI", 9, "bold"),
            bg=THEME["primary"], fg="#ffffff", relief=tk.FLAT,
            padx=18, pady=6, cursor="hand2", command=self._save_and_apply_config
        )
        self.btn_save.pack(side=tk.RIGHT)

    # ----------------- Internationalization / Language -----------------
    def _toggle_language(self):
        new_lang = "en" if self.var_language.get() == "zh" else "zh"
        self._set_language(new_lang)

    def _set_language(self, lang_code):
        if lang_code not in ("zh", "en"):
            return
        self.var_language.set(lang_code)
        self.i18n.set_language(lang_code)
        self.config_mgr.set("language", lang_code)
        self._refresh_ui_texts()
        if self.tray:
            self.tray.update_language()

    def _refresh_ui_texts(self):
        self.title(self.i18n.t("app_title"))
        self.lbl_app_title.config(text=self.i18n.t("header_title"))
        self.lbl_app_subtitle.config(text=self.i18n.t("header_subtitle"))
        self.btn_lang.config(text="English" if self.var_language.get() == "zh" else "中文")

        # Status & Toggle Button
        if self.var_enabled.get():
            self.status_pill.config(text=self.i18n.t("status_running"))
            self.btn_toggle.config(text=self.i18n.t("btn_pause"))
        else:
            self.status_pill.config(text=self.i18n.t("status_paused"))
            self.btn_toggle.config(text=self.i18n.t("btn_resume"))

        # Monitor Card
        self.lbl_card_title.config(text=self.i18n.t("card_monitor_title"))
        self.box_left.config(text=self.i18n.t("box_scroll_up"))
        self.box_right.config(text=self.i18n.t("box_scroll_down"))
        if self.engine.rbutton_down:
            self.lbl_rbutton_state.config(text=self.i18n.t("rbutton_pressed"))
        else:
            self.lbl_rbutton_state.config(text=self.i18n.t("rbutton_released"))

        if self.engine.current_proc_name:
            self.lbl_current_proc.config(text=self.i18n.t("target_app", proc=self.engine.current_proc_name))
        else:
            self.lbl_current_proc.config(text=self.i18n.t("target_none"))
        self.lbl_counter.config(text=self.i18n.t("switched_count", count=self.engine.total_switches))

        # Notebook tabs
        self.notebook.tab(0, text=self.i18n.t("tab_settings"))
        self.notebook.tab(1, text=self.i18n.t("tab_browsers"))
        self.notebook.tab(2, text=self.i18n.t("tab_system"))

        # Tab 1
        self.lbl_group1.config(text=self.i18n.t("group_shortcut_mode"))
        self.rb1.config(text=self.i18n.t("mode_ctrl_tab"))
        self.rb2.config(text=self.i18n.t("mode_ctrl_page"))
        self.lbl_group2.config(text=self.i18n.t("group_scroll"))
        self.cb_rev.config(text=self.i18n.t("chk_reverse_scroll"))
        self.lbl_sens.config(text=self.i18n.t("lbl_sensitivity"))
        self.lbl_sens_tip.config(text=self.i18n.t("lbl_sens_tip"))
        self.lbl_group3.config(text=self.i18n.t("group_scope"))
        self.cb_all.config(text=self.i18n.t("chk_all_apps"))

        # Tab 2
        self.lbl_browser_title.config(text=self.i18n.t("lbl_browser_list"))
        self.btn_scan.config(text=self.i18n.t("btn_scan"))
        self.lbl_custom.config(text=self.i18n.t("lbl_custom_proc"))
        self.btn_add.config(text=self.i18n.t("btn_add"))
        self.lbl_custom_list.config(text=self._get_custom_browsers_display())

        # Tab 3
        self.lbl_system_group.config(text=self.i18n.t("group_preference"))
        self.cb_min.config(text=self.i18n.t("chk_minimize_tray"))
        self.cb_auto.config(text=self.i18n.t("chk_autostart"))
        self.lbl_lang_setting.config(text=self.i18n.t("lbl_language"))
        self.lbl_guide_title.config(text=self.i18n.t("guide_title"))
        tips = [
            self.i18n.t("tip_1"),
            self.i18n.t("tip_2"),
            self.i18n.t("tip_3"),
            self.i18n.t("tip_4"),
            self.i18n.t("tip_5"),
        ]
        for lbl, tip_text in zip(self.tip_labels, tips):
            lbl.config(text=tip_text)

        # Bottom Bar
        self.btn_min.config(text=self.i18n.t("btn_min_tray"))
        self.btn_exit.config(text=self.i18n.t("btn_exit"))
        self.btn_save.config(text=self.i18n.t("btn_save"))

    # ----------------- Custom Browsers Helper -----------------
    def _get_custom_browsers_display(self):
        targets = self.config_mgr.get("target_browsers", [])
        popular_set = set(exe.lower() for _, exe in POPULAR_BROWSERS)
        custom_list = [b for b in targets if b.lower() not in popular_set]
        if not custom_list:
            return self.i18n.t("lbl_no_custom")
        return self.i18n.t("lbl_custom_list", list=", ".join(custom_list))

    def _add_custom_browser(self):
        text = self.entry_custom_exe.get().strip().lower()
        if not text:
            return
        if not text.endswith(".exe"):
            text += ".exe"
        targets = list(self.config_mgr.get("target_browsers", []))
        if text not in [t.lower() for t in targets]:
            targets.append(text)
            self.config_mgr.set("target_browsers", targets)
            self._save_and_apply_config(show_toast=False)
            self.lbl_custom_list.config(text=self._get_custom_browsers_display())
            self.entry_custom_exe.delete(0, tk.END)
            messagebox.showinfo(self.i18n.t("msg_add_success_title"), self.i18n.t("msg_add_success_text", proc=text))

    def _scan_running_browsers(self):
        try:
            cmd = 'tasklist /fo csv /nh'
            output = subprocess.check_output(cmd, shell=True, text=True, errors="ignore")
            running = set()
            for line in output.splitlines():
                parts = line.strip().split('","')
                if parts:
                    name = parts[0].replace('"', '').strip().lower()
                    running.add(name)

            detected = []
            for name, exe in POPULAR_BROWSERS:
                if exe.lower() in running:
                    self.browser_vars[exe].set(True)
                    detected.append(name)

            self._save_and_apply_config(show_toast=False)
            if detected:
                messagebox.showinfo(self.i18n.t("msg_scan_title"), self.i18n.t("msg_scan_found", list=', '.join(detected)))
            else:
                messagebox.showinfo(self.i18n.t("msg_scan_title"), self.i18n.t("msg_scan_none"))
        except Exception as e:
            messagebox.showerror(self.i18n.t("msg_scan_err_title"), self.i18n.t("msg_scan_err_text", err=str(e)))

    # ----------------- Gesture Engine Callbacks -----------------
    def _on_gesture_switched(self, direction, total_count, proc_name):
        self.after(0, self._update_ui_on_switch, direction, total_count, proc_name)

    def _update_ui_on_switch(self, direction, total_count, proc_name):
        self.lbl_counter.config(text=self.i18n.t("switched_count", count=total_count))
        self.lbl_current_proc.config(text=self.i18n.t("target_app", proc=proc_name or "browser"))

        # Visual Flash indicator
        if direction == "left":
            self.box_left.config(bg=THEME["primary"], fg="#ffffff")
            self.after(300, lambda: self.box_left.config(bg=THEME["input_bg"], fg=THEME["text_muted"]))
        else:
            self.box_right.config(bg=THEME["primary"], fg="#ffffff")
            self.after(300, lambda: self.box_right.config(bg=THEME["input_bg"], fg=THEME["text_muted"]))

    def _on_gesture_state_changed(self, is_down, proc_name):
        self.after(0, self._update_ui_on_state, is_down, proc_name)

    def _update_ui_on_state(self, is_down, proc_name):
        if is_down:
            self.lbl_rbutton_state.config(text=self.i18n.t("rbutton_pressed"), fg=THEME["warning"])
            if proc_name:
                self.lbl_current_proc.config(text=self.i18n.t("target_app", proc=proc_name))
        else:
            self.lbl_rbutton_state.config(text=self.i18n.t("rbutton_released"), fg=THEME["text_muted"])

    # ----------------- Service Management -----------------
    def _start_hook(self):
        success = self.hook_service.start()
        if not success:
            print("[TabFlowApp] Failed to start hook service")

    def _stop_hook(self):
        self.hook_service.stop()

    def _toggle_service(self):
        new_state = not self.var_enabled.get()
        self.var_enabled.set(new_state)
        self.config_mgr.set("enabled", new_state)
        self.engine.is_enabled = new_state
        self.tray.update_state(new_state)

        if new_state:
            self._start_hook()
            self.status_pill.config(text=self.i18n.t("status_running"), bg=THEME["success_bg"], fg=THEME["success"])
            self.btn_toggle.config(text=self.i18n.t("btn_pause"), bg=THEME["warning"])
        else:
            self._stop_hook()
            self.status_pill.config(text=self.i18n.t("status_paused"), bg=THEME["warning_bg"], fg=THEME["warning"])
            self.btn_toggle.config(text=self.i18n.t("btn_resume"), bg=THEME["success"])

    def _toggle_service_from_tray(self):
        self.after(0, self._toggle_service)

    def _on_toggle_autostart(self):
        self.config_mgr.set_autostart(self.var_autostart.get())

    def _save_and_apply_config(self, show_toast=True):
        # Assemble target browsers
        targets = []
        for exe, var in self.browser_vars.items():
            if var.get():
                targets.append(exe)

        # Include custom targets already stored
        current_stored = self.config_mgr.get("target_browsers", [])
        popular_set = set(exe.lower() for _, exe in POPULAR_BROWSERS)
        for t in current_stored:
            if t.lower() not in popular_set and t not in targets:
                targets.append(t)

        self.config_mgr.set("target_browsers", targets)
        self.config_mgr.set("shortcut_mode", self.var_shortcut_mode.get())
        self.config_mgr.set("reverse_scroll", self.var_reverse_scroll.get())
        self.config_mgr.set("wheel_sensitivity", self.var_sensitivity.get())
        self.config_mgr.set("all_apps_mode", self.var_all_apps.get())
        self.config_mgr.set("minimize_to_tray", self.var_min_tray.get())
        self.config_mgr.set("enabled", self.var_enabled.get())
        self.config_mgr.set("language", self.var_language.get())

        self.engine.update_config(self.config_mgr.config)
        self.lbl_custom_list.config(text=self._get_custom_browsers_display())

        if show_toast:
            messagebox.showinfo(self.i18n.t("msg_saved_title"), self.i18n.t("msg_saved_text"))

    # ----------------- Window & Tray -----------------
    def _on_close_window(self):
        if self.var_min_tray.get():
            self._hide_to_tray()
        else:
            self._exit_app()

    def _hide_to_tray(self):
        self.withdraw()

    def _show_window_from_tray(self):
        self.after(0, self._restore_window)

    def _restore_window(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def _exit_app(self):
        self.tray.stop()
        self._stop_hook()
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    import ctypes
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32

    # 1. 设置独立的 Windows AppUserModelID，确保任务栏、通知与进程树完美关联并展示专属图标
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("TabFlow.MouseSwitcher.App.1.0")
    except Exception:
        pass

    # 2. 启用 Windows 高分屏 (High-DPI) 支持，保证在缩放屏幕下字体与图标极致清晰
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass

    # 3. 单实例互斥体 (Mutex) 保护，防止多开冲突
    mutex_name = "Local\\TabFlow_SingleInstance_Mutex_2026"
    h_mutex = kernel32.CreateMutexW(None, False, mutex_name)
    if kernel32.GetLastError() == 183: # ERROR_ALREADY_EXISTS
        # Find existing TabFlow window and bring to front
        hwnd = user32.FindWindowW(None, "TabFlow - 浏览器标签页鼠标切换手势") or user32.FindWindowW(None, "TabFlow - Mouse Gesture Tab Switcher")
        if hwnd:
            user32.ShowWindow(hwnd, 9) # SW_RESTORE
            user32.SetForegroundWindow(hwnd)
        sys.exit(0)

    app = TabFlowApp()
    app.mainloop()
