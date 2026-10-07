import ctypes
from ctypes import wintypes
import time
import os
import threading

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

LRESULT = ctypes.c_int64
HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, ctypes.c_void_p)

user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]
user32.SetWindowsHookExW.restype = wintypes.HANDLE
user32.UnhookWindowsHookEx.argtypes = [wintypes.HANDLE]
user32.UnhookWindowsHookEx.restype = wintypes.BOOL
user32.CallNextHookEx.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.WPARAM, ctypes.c_void_p]
user32.CallNextHookEx.restype = LRESULT
user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, ctypes.c_void_p]
user32.PostThreadMessageW.restype = wintypes.BOOL
user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, ctypes.c_void_p]
user32.PostMessageW.restype = wintypes.BOOL
user32.SetForegroundWindow.argtypes = [wintypes.HWND]
user32.SetForegroundWindow.restype = wintypes.BOOL
user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]
user32.AttachThreadInput.restype = wintypes.BOOL
user32.BringWindowToTop.argtypes = [wintypes.HWND]
user32.BringWindowToTop.restype = wintypes.BOOL
user32.GetWindow.argtypes = [wintypes.HWND, wintypes.UINT]
user32.GetWindow.restype = wintypes.HWND
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextLengthW.restype = ctypes.c_int
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.restype = ctypes.c_int
user32.IsWindow.argtypes = [wintypes.HWND]
user32.IsWindow.restype = wintypes.BOOL
user32.IsWindowVisible.argtypes = [wintypes.HWND]
user32.IsWindowVisible.restype = wintypes.BOOL

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
user32.EnumWindows.restype = wintypes.BOOL
user32.mouse_event.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ctypes.c_size_t]

MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MAGIC = 0x54414253 # 'TABS'

WH_MOUSE_LL = 14
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_MOUSEWHEEL = 0x020A
WM_MBUTTONDOWN = 0x0207
WM_CANCELMODE = 0x001F
WM_QUIT = 0x0012

VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_TAB = 0x09
VK_PRIOR = 0x21 # Page Up
VK_NEXT = 0x22  # Page Down
VK_ESCAPE = 0x1B
KEYEVENTF_KEYUP = 0x0002

class POINT(ctypes.Structure):
    _fields_ = [('x', wintypes.LONG), ('y', wintypes.LONG)]

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ('pt', POINT),
        ('mouseData', wintypes.DWORD),
        ('flags', wintypes.DWORD),
        ('time', wintypes.DWORD),
        ('dwExtraInfo', ctypes.c_size_t),
    ]

class GestureEngine:
    def __init__(self, config=None):
        self.config = config or {}
        self.target_browsers = set(b.lower() for b in self.config.get("target_browsers", []))
        self.all_apps_mode = self.config.get("all_apps_mode", False)
        self.shortcut_mode = self.config.get("shortcut_mode", "ctrl_tab")
        self.reverse_scroll = self.config.get("reverse_scroll", False)
        self.wheel_sensitivity = self.config.get("wheel_sensitivity", 120)
        self.is_enabled = self.config.get("enabled", True)

        self.rbutton_down = False
        self.has_switched = False
        self.is_replaying = False
        self.wheel_accum = 0
        self.target_root_hwnd = 0
        self.current_proc_name = ""
        self.total_switches = 0

        self.cache = {} # root_hwnd -> (is_browser, proc_name, expire_time)
        self.on_switch_callback = None
        self.on_state_callback = None

    def update_config(self, config):
        self.config = config
        self.target_browsers = set(b.lower() for b in self.config.get("target_browsers", []))
        self.all_apps_mode = self.config.get("all_apps_mode", False)
        self.shortcut_mode = self.config.get("shortcut_mode", "ctrl_tab")
        self.reverse_scroll = self.config.get("reverse_scroll", False)
        self.wheel_sensitivity = max(30, int(self.config.get("wheel_sensitivity", 120)))
        self.is_enabled = self.config.get("enabled", True)
        self.cache.clear()

    def _get_main_root(self, hwnd):
        if not hwnd or not user32.IsWindow(hwnd):
            return 0
        # 1. Walk up to root owner (handles popup menus / dialogs)
        root = user32.GetAncestor(hwnd, 3) # GA_ROOTOWNER = 3
        if not root:
            root = user32.GetAncestor(hwnd, 2) or hwnd # GA_ROOT = 2

        # 2. If root has a non-empty title, it is a main application window
        if user32.GetWindowTextLengthW(root) > 0:
            return root

        # 3. If root has no title (like Chromium popup widgets), check GW_OWNER
        owner = user32.GetWindow(root, 4) # GW_OWNER = 4
        if owner and user32.IsWindow(owner):
            owner_root = user32.GetAncestor(owner, 3) or owner
            if user32.GetWindowTextLengthW(owner_root) > 0:
                return owner_root

        # 4. Fallback: Find visible top-level window with a title for this PID
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(root, ctypes.byref(pid))
        if pid.value:
            found = [0]
            def _cb(h, l):
                h_pid = wintypes.DWORD()
                user32.GetWindowThreadProcessId(h, ctypes.byref(h_pid))
                if h_pid.value == pid.value and user32.IsWindowVisible(h):
                    if user32.GetWindowTextLengthW(h) > 0:
                        found[0] = h
                        return False
                return True
            user32.EnumWindows(WNDENUMPROC(_cb), 0)
            if found[0]:
                return found[0]

        return root

    def force_foreground(self, hwnd):
        if not hwnd or not user32.IsWindow(hwnd):
            return
        fg = user32.GetForegroundWindow()
        if fg == hwnd:
            return
        cur_tid = kernel32.GetCurrentThreadId()
        fg_tid = user32.GetWindowThreadProcessId(fg, None) if fg else 0
        target_tid = user32.GetWindowThreadProcessId(hwnd, None)

        try:
            if fg_tid and cur_tid != fg_tid:
                user32.AttachThreadInput(cur_tid, fg_tid, True)
            if target_tid and cur_tid != target_tid:
                user32.AttachThreadInput(cur_tid, target_tid, True)

            user32.BringWindowToTop(hwnd)
            user32.SetForegroundWindow(hwnd)
        except Exception:
            pass
        finally:
            if fg_tid and cur_tid != fg_tid:
                user32.AttachThreadInput(cur_tid, fg_tid, False)
            if target_tid and cur_tid != target_tid:
                user32.AttachThreadInput(cur_tid, target_tid, False)

    def _is_target_window(self, pt):
        if self.all_apps_mode:
            hwnd = user32.WindowFromPoint(pt)
            root = self._get_main_root(hwnd) if hwnd else 0
            return True, root or hwnd, "all_apps"

        # Check window under cursor, and also check active foreground window
        candidates = []
        hwnd = user32.WindowFromPoint(pt)
        if hwnd:
            candidates.append(hwnd)
        fg = user32.GetForegroundWindow()
        if fg and fg not in candidates:
            candidates.append(fg)

        now = time.time()
        for h in candidates:
            root = self._get_main_root(h)
            cached = self.cache.get(root)
            if cached and (now < cached[2]):
                if cached[0]:
                    return True, root, cached[1]
                continue

            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(root, ctypes.byref(pid))
            if not pid.value:
                continue

            hProc = kernel32.OpenProcess(0x1000, False, pid.value) # PROCESS_QUERY_LIMITED_INFORMATION
            if not hProc:
                continue

            buf = ctypes.create_unicode_buffer(512)
            size = wintypes.DWORD(512)
            res = kernel32.QueryFullProcessImageNameW(hProc, 0, buf, ctypes.byref(size))
            kernel32.CloseHandle(hProc)

            if not res:
                continue

            proc_name = os.path.basename(buf.value).lower()
            is_target = proc_name in self.target_browsers
            self.cache[root] = (is_target, proc_name, now + 10.0)
            if is_target:
                return True, root, proc_name

        return False, 0, ""

    def dismiss_popup(self):
        user32.keybd_event(VK_ESCAPE, 0, 0, 0)
        user32.keybd_event(VK_ESCAPE, 0, KEYEVENTF_KEYUP, 0)

    def release_modifiers(self):
        scan_ctrl = user32.MapVirtualKeyW(VK_CONTROL, 0)
        scan_shift = user32.MapVirtualKeyW(VK_SHIFT, 0)
        user32.keybd_event(VK_CONTROL, scan_ctrl, KEYEVENTF_KEYUP, 0)
        user32.keybd_event(VK_SHIFT, scan_shift, KEYEVENTF_KEYUP, 0)

    def trigger_switch(self, go_left: bool):
        # Ensure browser window receives keyboard shortcuts
        if self.target_root_hwnd:
            self.force_foreground(self.target_root_hwnd)

        if self.shortcut_mode == "ctrl_page":
            key = VK_PRIOR if go_left else VK_NEXT
            scan_ctrl = user32.MapVirtualKeyW(VK_CONTROL, 0)
            scan_key = user32.MapVirtualKeyW(key, 0)
            user32.keybd_event(VK_CONTROL, scan_ctrl, 0, 0)
            user32.keybd_event(key, scan_key, 0, 0)
            user32.keybd_event(key, scan_key, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(VK_CONTROL, scan_ctrl, KEYEVENTF_KEYUP, 0)
        else: # "ctrl_tab"
            scan_ctrl = user32.MapVirtualKeyW(VK_CONTROL, 0)
            scan_tab = user32.MapVirtualKeyW(VK_TAB, 0)
            scan_shift = user32.MapVirtualKeyW(VK_SHIFT, 0)
            if go_left: # Ctrl + Shift + Tab
                user32.keybd_event(VK_CONTROL, scan_ctrl, 0, 0)
                user32.keybd_event(VK_SHIFT, scan_shift, 0, 0)
                user32.keybd_event(VK_TAB, scan_tab, 0, 0)
                user32.keybd_event(VK_TAB, scan_tab, KEYEVENTF_KEYUP, 0)
                user32.keybd_event(VK_SHIFT, scan_shift, KEYEVENTF_KEYUP, 0)
                user32.keybd_event(VK_CONTROL, scan_ctrl, KEYEVENTF_KEYUP, 0)
            else: # Ctrl + Tab
                user32.keybd_event(VK_CONTROL, scan_ctrl, 0, 0)
                user32.keybd_event(VK_TAB, scan_tab, 0, 0)
                user32.keybd_event(VK_TAB, scan_tab, KEYEVENTF_KEYUP, 0)
                user32.keybd_event(VK_CONTROL, scan_ctrl, KEYEVENTF_KEYUP, 0)

        self.total_switches += 1
        if self.on_switch_callback:
            try:
                self.on_switch_callback("left" if go_left else "right", self.total_switches, self.current_proc_name)
            except Exception:
                pass

    def hook_proc(self, nCode, wParam, lParam):
        # 1. Zero-latency path: Mouse movements pass through instantly
        if wParam == WM_MOUSEMOVE or nCode < 0:
            return user32.CallNextHookEx(None, nCode, wParam, lParam)

        if not self.is_enabled:
            return user32.CallNextHookEx(None, nCode, wParam, lParam)

        info = ctypes.cast(lParam, ctypes.POINTER(MSLLHOOKSTRUCT)).contents

        # 2. Allow our synthetic replay events to pass straight through to the browser
        if self.is_replaying or info.dwExtraInfo == MAGIC:
            return user32.CallNextHookEx(None, nCode, wParam, lParam)

        if wParam == WM_RBUTTONDOWN:
            is_target, root, proc_name = self._is_target_window(info.pt)
            if is_target:
                self.rbutton_down = True
                self.has_switched = False
                self.target_root_hwnd = root
                self.current_proc_name = proc_name
                self.wheel_accum = 0

                # If an open popup / context menu currently has focus instead of main window,
                # dismiss it immediately and restore focus to the browser main window.
                fg = user32.GetForegroundWindow()
                if fg and fg != root:
                    self.dismiss_popup()
                    self.force_foreground(root)

                if self.on_state_callback:
                    try:
                        self.on_state_callback(True, proc_name)
                    except Exception:
                        pass
                # Intercept WM_RBUTTONDOWN so the browser NEVER enters right-button down state!
                # Because the browser never receives WM_RBUTTONDOWN, subsequent left-click text
                # selections and drags will NEVER get stuck or affected!
                return 1
            else:
                self.rbutton_down = False
            return user32.CallNextHookEx(None, nCode, wParam, lParam)

        elif wParam == WM_MOUSEWHEEL:
            if self.rbutton_down:
                # Ensure foreground focus is on the browser window
                fg = user32.GetForegroundWindow()
                if fg != self.target_root_hwnd and self.target_root_hwnd:
                    self.dismiss_popup()
                    self.force_foreground(self.target_root_hwnd)

                delta = ctypes.c_short(info.mouseData >> 16).value
                self.wheel_accum += delta
                threshold = self.wheel_sensitivity

                while self.wheel_accum >= threshold:
                    # Wheel Up (Positive) -> Switch Left (default)
                    go_left = not self.reverse_scroll
                    self.trigger_switch(go_left=go_left)
                    self.wheel_accum -= threshold
                    self.has_switched = True

                while self.wheel_accum <= -threshold:
                    # Wheel Down (Negative) -> Switch Right (default)
                    go_left = self.reverse_scroll
                    self.trigger_switch(go_left=go_left)
                    self.wheel_accum += threshold
                    self.has_switched = True

                return 1 # Swallow wheel event so page does not scroll!

        elif wParam == WM_RBUTTONUP:
            if self.rbutton_down:
                self.rbutton_down = False
                if self.on_state_callback:
                    try:
                        self.on_state_callback(False, "")
                    except Exception:
                        pass

                if self.has_switched:
                    self.has_switched = False
                    # Gesture was executed!
                    # 1. Cleanly release modifier keys so left-click works 100% normally
                    self.release_modifiers()
                    # 2. Dismiss any lingering menu
                    self.dismiss_popup()
                    # 3. Swallow WM_RBUTTONUP!
                    # Because browser never received DOWN and never receives UP,
                    # browser's mouse state is 100% CLEAN. Left-click/drag will NEVER glitch!
                    return 1
                else:
                    # Normal right-click: user clicked without scrolling.
                    # Replay realistic DOWN + UP click so browser gets native context menu:
                    def _replay():
                        self.is_replaying = True
                        try:
                            user32.mouse_event(MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, MAGIC)
                            time.sleep(0.04) # 40ms realistic human tap duration
                            user32.mouse_event(MOUSEEVENTF_RIGHTUP, 0, 0, 0, MAGIC)
                        finally:
                            time.sleep(0.02)
                            self.is_replaying = False

                    threading.Thread(target=_replay, daemon=True).start()
                    return 1 # Swallow original physical UP

        elif wParam in (WM_LBUTTONDOWN, WM_MBUTTONDOWN):
            if self.rbutton_down:
                self.rbutton_down = False
                self.has_switched = False
                if self.on_state_callback:
                    try:
                        self.on_state_callback(False, "")
                    except Exception:
                        pass
            # Force release Ctrl/Shift so any left-click is 100% clean
            self.release_modifiers()

        return user32.CallNextHookEx(None, nCode, wParam, lParam)

class HookService:
    def __init__(self, engine: GestureEngine):
        self.engine = engine
        self._thread = None
        self._hook_handle = None
        self._thread_id = None
        self._ready_event = threading.Event()
        self._stop_event = threading.Event()
        self._cb_ref = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return True
        self._stop_event.clear()
        self._ready_event.clear()
        self._thread = threading.Thread(target=self._run_hook_loop, name="TabFlow_HookThread", daemon=True)
        self._thread.start()
        success = self._ready_event.wait(timeout=2.0)
        return success and bool(self._hook_handle)

    def stop(self):
        self._stop_event.set()
        if self._thread_id:
            user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
        if self._thread:
            self._thread.join(timeout=1.5)
            self._thread = None
        self._hook_handle = None
        self._thread_id = None

    def _run_hook_loop(self):
        hdesk = user32.OpenInputDesktop(0, False, 0x01FF)
        if hdesk:
            user32.SetThreadDesktop(hdesk)

        self._thread_id = kernel32.GetCurrentThreadId()
        self._cb_ref = HOOKPROC(self.engine.hook_proc)
        self._hook_handle = user32.SetWindowsHookExW(WH_MOUSE_LL, self._cb_ref, 0, 0)
        self._ready_event.set()

        if not self._hook_handle:
            print("[HookService] Failed to install WH_MOUSE_LL hook")
            return

        msg = wintypes.MSG()
        while not self._stop_event.is_set():
            ret = user32.GetMessageW(ctypes.byref(msg), 0, 0, 0)
            if ret <= 0: # WM_QUIT (0) or error (-1)
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        if self._hook_handle:
            user32.UnhookWindowsHookEx(self._hook_handle)
            self._hook_handle = None
