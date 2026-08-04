import os
try:
    from PyQt6.QtCore import QTimer, QRect
    from PyQt6.QtGui import QAction
    from PyQt6.QtWidgets import QMenu, QMainWindow
except ImportError:
    from PyQt5.QtCore import QTimer, QRect
    from PyQt5.QtWidgets import QMenu, QMainWindow, QAction

from krita import Extension, Krita
from .config import load_config
from .settings_dialog import SettingsDialog

class InfiniteCanvasExtension(Extension):
    def __init__(self, parent):
        super().__init__(parent)
        self.is_active = False
        self.config = load_config()

        self.timer = QTimer()
        self.timer.setInterval(self.config.get("check_interval", 200))
        self.timer.timeout.connect(self._check_canvas_expansion)
        
        self.top_menu = None
        self.action_toggle = None
        self.action_fit = None
        self.action_settings = None
        self.action_exp_left = None
        self.action_exp_right = None
        self.action_exp_top = None
        self.action_exp_bottom = None

    def setup(self):
        notifier = Krita.instance().notifier()
        notifier.windowCreated.connect(self._on_window_created)
        notifier.imageCreated.connect(self._on_image_created)

    def createActions(self, window):
        # 1. 主开关
        self.action_toggle = window.createAction("toggle_infinite_canvas", "开启无限画布", "tools/scripts")
        self.action_toggle.setCheckable(True)
        self.action_toggle.toggled.connect(self.toggle_mode)

        # 2. 四向手动拓展
        self.action_exp_left = window.createAction("exp_left_infinite_canvas", "向左手动扩充", "tools/scripts")
        self.action_exp_left.triggered.connect(lambda: self.expand_direction("left"))

        self.action_exp_right = window.createAction("exp_right_infinite_canvas", "向右手动扩充", "tools/scripts")
        self.action_exp_right.triggered.connect(lambda: self.expand_direction("right"))

        self.action_exp_top = window.createAction("exp_top_infinite_canvas", "向上手动扩充", "tools/scripts")
        self.action_exp_top.triggered.connect(lambda: self.expand_direction("top"))

        self.action_exp_bottom = window.createAction("exp_bottom_infinite_canvas", "向下手动扩充", "tools/scripts")
        self.action_exp_bottom.triggered.connect(lambda: self.expand_direction("bottom"))

        # 3. 紧贴内容裁切
        self.action_fit = window.createAction("fit_infinite_canvas", "精准裁切紧贴图层内容", "tools/scripts")
        self.action_fit.triggered.connect(self.fit_content)

        # 4. 设置
        self.action_settings = window.createAction("settings_infinite_canvas", "无限画布设置...", "tools/scripts")
        self.action_settings.triggered.connect(self.open_settings)

        # 挂载顶层导航栏
        self._attach_top_menu(window)

    def _on_window_created(self):
        window = Krita.instance().activeWindow()
        if window:
            self._attach_top_menu(window)

    def _attach_top_menu(self, window):
        qwin = window.qwindow()
        if not qwin or not isinstance(qwin, QMainWindow):
            return

        menu_bar = qwin.menuBar()
        if not menu_bar:
            return

        # 防重复挂载
        for child in menu_bar.children():
            if isinstance(child, QMenu) and child.title() == "无限画布":
                return

        self.top_menu = QMenu("无限画布", menu_bar)
        
        # 挂载菜单项
        if self.action_toggle:
            self.top_menu.addAction(self.action_toggle)

        self.top_menu.addSeparator()

        if self.action_exp_left:
            self.top_menu.addAction(self.action_exp_left)
        if self.action_exp_right:
            self.top_menu.addAction(self.action_exp_right)
        if self.action_exp_top:
            self.top_menu.addAction(self.action_exp_top)
        if self.action_exp_bottom:
            self.top_menu.addAction(self.action_exp_bottom)

        self.top_menu.addSeparator()

        if self.action_fit:
            self.top_menu.addAction(self.action_fit)

        self.top_menu.addSeparator()

        if self.action_settings:
            self.top_menu.addAction(self.action_settings)

        menu_bar.addMenu(self.top_menu)

    def _on_image_created(self, image):
        if self.config.get("auto_enable", False) and self.action_toggle:
            if not self.action_toggle.isChecked():
                self.action_toggle.setChecked(True)

    def toggle_mode(self, checked):
        self.is_active = checked
        if checked:
            self.timer.setInterval(self.config.get("check_interval", 200))
            self.timer.start()
        else:
            self.timer.stop()

    def expand_direction(self, direction):
        doc = Krita.instance().activeDocument()
        if not doc:
            return
        step = self.config.get("expand_step", 600)
        max_size = self.config.get("max_canvas_size", 20000)

        w = doc.width()
        h = doc.height()

        if direction == "left" and w + step <= max_size:
            doc.crop(-step, 0, w + step, h)
        elif direction == "right" and w + step <= max_size:
            doc.crop(0, 0, w + step, h)
        elif direction == "top" and h + step <= max_size:
            doc.crop(0, -step, w, h + step)
        elif direction == "bottom" and h + step <= max_size:
            doc.crop(0, 0, w, h + step)
        doc.refreshProjection()

    def open_settings(self):
        qwin = Krita.instance().activeWindow().qwindow() if Krita.instance().activeWindow() else None
        dlg = SettingsDialog(qwin)
        res = dlg.exec() if hasattr(dlg, 'exec') else dlg.exec_()
        if res:
            self.config = load_config()
            self.timer.setInterval(self.config.get("check_interval", 200))

    def fit_content(self):
        doc = Krita.instance().activeDocument()
        if not doc:
            return

        root = doc.rootNode()
        if not root:
            return

        doc_w = doc.width()
        doc_h = doc.height()

        def _get_paint_rects(node):
            rects = []
            if node.visible():
                node_type = node.type()
                name = node.name().lower()
                # 过滤掉背景图层与填充图层
                is_bg = "background" in name or "背景" in name or "底色" in name or node_type == "filllayer"
                if not is_bg and node_type in ("paintlayer", "vectorlayer", "filelayer"):
                    bounds = node.bounds()
                    if not bounds.isEmpty():
                        rects.append(bounds)
                for child in node.childNodes():
                    rects.extend(_get_paint_rects(child))
            return rects

        rects = _get_paint_rects(root)

        # 回退逻辑：如果未找到非背景图层，则尝试当前活动图层
        if not rects:
            active = doc.activeNode()
            if active and not active.bounds().isEmpty():
                rects = [active.bounds()]

        if not rects:
            return

        union_rect = rects[0]
        for r in rects[1:]:
            union_rect = union_rect.united(r)

        if union_rect.isEmpty():
            return

        padding = 40
        new_x = union_rect.x() - padding
        new_y = union_rect.y() - padding
        new_w = union_rect.width() + 2 * padding
        new_h = union_rect.height() + 2 * padding

        # 只有在有效缩小或重定位时裁剪
        if new_w < doc_w or new_h < doc_h or new_x != 0 or new_y != 0:
            doc.crop(new_x, new_y, new_w, new_h)
            doc.refreshProjection()

    def _check_canvas_expansion(self):
        if not self.is_active:
            return
        doc = Krita.instance().activeDocument()
        if not doc:
            return
        node = doc.activeNode()
        if not node:
            return

        bounds = node.bounds()
        if bounds.isEmpty():
            return

        margin = self.config.get("margin", 150)
        expand_step = self.config.get("expand_step", 600)
        max_size = self.config.get("max_canvas_size", 20000)

        doc_w = doc.width()
        doc_h = doc.height()

        nb_l = bounds.x()
        nb_t = bounds.y()
        nb_r = bounds.x() + bounds.width()
        nb_b = bounds.y() + bounds.height()

        exp_l = expand_step if nb_l < margin and doc_w + expand_step <= max_size else 0
        exp_t = expand_step if nb_t < margin and doc_h + expand_step <= max_size else 0
        exp_r = expand_step if nb_r > doc_w - margin and doc_w + expand_step <= max_size else 0
        exp_b = expand_step if nb_b > doc_h - margin and doc_h + expand_step <= max_size else 0

        if exp_l or exp_t or exp_r or exp_b:
            new_x = -exp_l
            new_y = -exp_t
            new_w = doc_w + exp_l + exp_r
            new_h = doc_h + exp_t + exp_b
            doc.crop(new_x, new_y, new_w, new_h)
            doc.refreshProjection()
