import threading
from PIL import Image, ImageDraw
import pystray

class TrayManager:
    def __init__(self, on_show=None, on_toggle=None, on_exit=None, is_enabled=True, i18n=None):
        self.on_show = on_show
        self.on_toggle = on_toggle
        self.on_exit = on_exit
        self.is_enabled = is_enabled
        self.i18n = i18n
        self.icon = None
        self._thread = None

    def _t(self, key, **kwargs):
        if self.i18n:
            return self.i18n.t(key, **kwargs)
        return key

    def _create_image(self, active=True):
        size = 64
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Background rounded rect
        bg_color = (30, 41, 59, 255) if active else (51, 65, 85, 255)
        draw.rounded_rectangle([4, 4, 60, 60], radius=14, fill=bg_color)

        # Draw Browser Tabs symbol
        tab1_color = (99, 102, 241, 255) if active else (148, 163, 184, 255)
        tab2_color = (14, 165, 233, 255) if active else (100, 116, 139, 255)
        
        # Left tab
        draw.rounded_rectangle([12, 16, 32, 48], radius=6, fill=tab1_color)
        # Right tab
        draw.rounded_rectangle([32, 20, 52, 48], radius=6, fill=tab2_color)

        # Status badge dot (Green if active, Amber if paused)
        badge_color = (16, 185, 129, 255) if active else (245, 158, 11, 255)
        draw.ellipse([44, 44, 58, 58], fill=badge_color, outline=(255, 255, 255, 220), width=2)

        return image

    def start(self):
        if self.icon:
            return
        img = self._create_image(self.is_enabled)
        menu = pystray.Menu(
            pystray.MenuItem(lambda text: self._t("tray_open"), self._handle_show, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                lambda text: self._t("tray_status_active") if self.is_enabled else self._t("tray_status_paused"),
                self._handle_toggle
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda text: self._t("tray_exit"), self._handle_exit)
        )
        self.icon = pystray.Icon("TabFlow", img, self._t("tray_tooltip"), menu)
        self._thread = threading.Thread(target=self.icon.run, daemon=True)
        self._thread.start()

    def update_state(self, is_enabled: bool):
        self.is_enabled = is_enabled
        if self.icon:
            self.icon.icon = self._create_image(is_enabled)
            self.icon.update_menu()

    def update_language(self):
        if self.icon:
            try:
                self.icon.title = self._t("tray_tooltip")
                self.icon.update_menu()
            except Exception:
                pass

    def stop(self):
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
            self.icon = None

    def _handle_show(self, icon=None, item=None):
        if self.on_show:
            self.on_show()

    def _handle_toggle(self, icon=None, item=None):
        if self.on_toggle:
            self.on_toggle()

    def _handle_exit(self, icon=None, item=None):
        if self.on_exit:
            self.on_exit()
