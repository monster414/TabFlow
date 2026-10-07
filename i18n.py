import locale

TRANSLATIONS = {
    "zh": {
        "app_title": "TabFlow - 浏览器标签页鼠标切换手势",
        "header_title": "⚡ TabFlow",
        "header_subtitle": "鼠标右键 + 滚轮 顺畅切换浏览器标签页",
        "status_running": "🟢 服务运行中",
        "status_paused": "🟡 服务已暂停",
        "btn_pause": "暂停服务",
        "btn_resume": "启动服务",
        "card_monitor_title": "实时手势动态监视",
        "box_scroll_up": "◀ 向上滚轮：向左切换标签 (上一标签)",
        "box_scroll_down": "向下滚轮：向右切换标签 (下一标签) ▶",
        "rbutton_released": "右键状态: 未按下",
        "rbutton_pressed": "右键状态: 按住中 (监听中)",
        "target_none": "目标程序: 等待触发",
        "target_app": "目标程序: {proc}",
        "switched_count": "已切换: {count} 次",
        "tab_settings": " ⚙️ 手势与快捷键 ",
        "tab_browsers": " 🌐 目标程序列表 ",
        "tab_system": " 💻 运行与偏好 ",
        # Tab 1: Settings
        "group_shortcut_mode": "标签切换按键模式",
        "mode_ctrl_tab": "Ctrl + Shift + Tab (左) / Ctrl + Tab (右)  [所有浏览器通用标准，推荐]",
        "mode_ctrl_page": "Ctrl + PageUp (左) / Ctrl + PageDown (右)  [绝对方向切换]",
        "group_scroll": "滚轮方向与灵敏度",
        "chk_reverse_scroll": "反转滚轮方向（向上滚动切换至右侧标签，向下至左侧）",
        "lbl_sensitivity": "单次切换滚轮刻度：",
        "lbl_sens_tip": "(默认 120 = 拨动一格切换 1 次)",
        "group_scope": "生效范围模式",
        "chk_all_apps": "全局应用模式（不仅限浏览器，在 VS Code、文件管理器等所有软件均生效）",
        # Tab 2: Browsers
        "lbl_browser_list": "勾选允许手势生效的浏览器：",
        "btn_scan": "🔍 扫描运行中的浏览器",
        "lbl_custom_proc": "添加自定义进程 (例如 mybrowser.exe 或 code.exe):",
        "btn_add": "+ 添加",
        "lbl_no_custom": "当前暂无自定义进程",
        "lbl_custom_list": "已添加的自定义程序: {list}",
        "msg_add_success_title": "添加成功",
        "msg_add_success_text": "已成功添加并启用进程: {proc}",
        "msg_scan_title": "扫描完成",
        "msg_scan_found": "检测到正在运行的浏览器并已自动勾选：\n{list}",
        "msg_scan_none": "未检测到已知的运行中浏览器。",
        "msg_scan_err_title": "扫描失败",
        "msg_scan_err_text": "扫描进程出错: {err}",
        # Tab 3: System & Preferences
        "group_preference": "后台运行与系统偏好",
        "chk_minimize_tray": "关闭主窗口时自动最小化到系统托盘 (在后台持续监听手势)",
        "chk_autostart": "开机自动启动 TabFlow",
        "lbl_language": "界面语言 / Language：",
        "guide_title": "💡 使用说明与手势操作技巧：",
        "tip_1": "1. 在浏览器网页任意空白或页面区域，按住鼠标【右键】不松开；",
        "tip_2": "2. 向上滚动滚轮：标签页向左切换；向下滚动滚轮：标签页向右切换；",
        "tip_3": "3. 滚轮滚动几次，就对应切换几次标签页；",
        "tip_4": "4. 松开右键即可结束手势，完全不会误弹右键菜单！",
        "tip_5": "5. 普通单击右键：右键菜单依然秒出，100% 不受任何干扰影响。",
        # Bottom Bar
        "btn_min_tray": "最小化到托盘",
        "btn_exit": "退出程序",
        "btn_save": "✔ 保存并应用配置",
        "msg_saved_title": "提示",
        "msg_saved_text": "配置已成功保存并立即生效！",
        # Tray Menu
        "tray_open": "打开 TabFlow 主界面",
        "tray_status_active": "状态: 已启用 (点击暂停)",
        "tray_status_paused": "状态: 已暂停 (点击启用)",
        "tray_exit": "退出程序",
        "tray_tooltip": "TabFlow - 浏览器标签页鼠标切换手势",
    },
    "en": {
        "app_title": "TabFlow - Mouse Gesture Tab Switcher",
        "header_title": "⚡ TabFlow",
        "header_subtitle": "Right-click + Scroll wheel to switch browser tabs smoothly",
        "status_running": "🟢 Service Running",
        "status_paused": "🟡 Service Paused",
        "btn_pause": "Pause",
        "btn_resume": "Resume",
        "card_monitor_title": "Live Gesture Monitor",
        "box_scroll_up": "◀ Scroll Up: Switch Left (Previous Tab)",
        "box_scroll_down": "Scroll Down: Switch Right (Next Tab) ▶",
        "rbutton_released": "Right Button: Released",
        "rbutton_pressed": "Right Button: Pressed (Listening)",
        "target_none": "Target App: Waiting",
        "target_app": "Target App: {proc}",
        "switched_count": "Switched: {count} times",
        "tab_settings": " ⚙️ Gestures & Hotkeys ",
        "tab_browsers": " 🌐 Target Apps ",
        "tab_system": " 💻 Preferences ",
        # Tab 1: Settings
        "group_shortcut_mode": "Tab Switching Shortcut Mode",
        "mode_ctrl_tab": "Ctrl + Shift + Tab (Left) / Ctrl + Tab (Right)  [Standard, Recommended]",
        "mode_ctrl_page": "Ctrl + PageUp (Left) / Ctrl + PageDown (Right)  [Directional]",
        "group_scroll": "Scroll Direction & Sensitivity",
        "chk_reverse_scroll": "Reverse scroll direction (Up switches Right, Down switches Left)",
        "lbl_sensitivity": "Wheel ticks per switch: ",
        "lbl_sens_tip": "(Default 120 = 1 notch per switch)",
        "group_scope": "Scope of Application",
        "chk_all_apps": "Global App Mode (Enable across all software, e.g. VS Code, Explorer)",
        # Tab 2: Browsers
        "lbl_browser_list": "Enable gestures for selected browsers:",
        "btn_scan": "🔍 Scan Running Browsers",
        "lbl_custom_proc": "Add custom process (e.g. mybrowser.exe or code.exe):",
        "btn_add": "+ Add",
        "lbl_no_custom": "No custom processes added",
        "lbl_custom_list": "Custom processes: {list}",
        "msg_add_success_title": "Added Successfully",
        "msg_add_success_text": "Successfully added and enabled process: {proc}",
        "msg_scan_title": "Scan Complete",
        "msg_scan_found": "Detected running browsers and enabled them:\n{list}",
        "msg_scan_none": "No known running browsers detected.",
        "msg_scan_err_title": "Scan Error",
        "msg_scan_err_text": "Failed to scan processes: {err}",
        # Tab 3: System & Preferences
        "group_preference": "Background & System Preferences",
        "chk_minimize_tray": "Minimize to system tray when closing window",
        "chk_autostart": "Launch TabFlow automatically on Windows startup",
        "lbl_language": "Language / 界面语言: ",
        "guide_title": "💡 Instructions & Tips:",
        "tip_1": "1. Hold down the [Right Mouse Button] on any web page or window;",
        "tip_2": "2. Scroll UP to switch Left; Scroll DOWN to switch Right;",
        "tip_3": "3. Continuous scrolling will switch multiple tabs accordingly;",
        "tip_4": "4. Release right button to finish — context menu will NOT popup!",
        "tip_5": "5. Normal right-click: native context menu pops up instantly as usual.",
        # Bottom Bar
        "btn_min_tray": "Minimize to Tray",
        "btn_exit": "Exit",
        "btn_save": "✔ Save & Apply",
        "msg_saved_title": "Saved",
        "msg_saved_text": "Settings saved and applied successfully!",
        # Tray Menu
        "tray_open": "Open TabFlow",
        "tray_status_active": "Status: Active (Click to pause)",
        "tray_status_paused": "Status: Paused (Click to resume)",
        "tray_exit": "Exit",
        "tray_tooltip": "TabFlow - Mouse Gesture Tab Switcher",
    }
}

class I18nManager:
    def __init__(self, lang="zh"):
        self.lang = lang if lang in TRANSLATIONS else "zh"

    def set_language(self, lang):
        if lang in TRANSLATIONS:
            self.lang = lang

    def t(self, key, **kwargs):
        lang_dict = TRANSLATIONS.get(self.lang, TRANSLATIONS["zh"])
        text = lang_dict.get(key, TRANSLATIONS["zh"].get(key, key))
        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text
        return text

def detect_system_language():
    try:
        lang, _ = locale.getdefaultlocale()
        if lang and lang.lower().startswith("zh"):
            return "zh"
    except Exception:
        pass
    return "en"
