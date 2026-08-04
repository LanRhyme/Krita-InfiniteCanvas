try:
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
        QCheckBox, QPushButton, QGroupBox, QFormLayout
    )
except ImportError:
    from PyQt5.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox,
        QCheckBox, QPushButton, QGroupBox, QFormLayout
    )

from .config import load_config, save_config

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("无限画布首选项设置")
        self.resize(380, 260)
        self.config = load_config()

        self._init_ui()
        self._load_values()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)

        # 1. 扩充算法与安全限制
        alg_group = QGroupBox("画布自动扩充与安全设置")
        alg_layout = QFormLayout(alg_group)

        self.margin_spin = QSpinBox()
        self.margin_spin.setRange(30, 1000)
        self.margin_spin.setSuffix(" px")
        alg_layout.addRow("边缘触发安全防线:", self.margin_spin)

        self.step_spin = QSpinBox()
        self.step_spin.setRange(100, 5000)
        self.step_spin.setSingleStep(100)
        self.step_spin.setSuffix(" px")
        alg_layout.addRow("单次扩充步长像素:", self.step_spin)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(50, 2000)
        self.interval_spin.setSingleStep(50)
        self.interval_spin.setSuffix(" ms")
        alg_layout.addRow("检测轮询轮训间隔:", self.interval_spin)

        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(3000, 50000)
        self.max_size_spin.setSingleStep(1000)
        self.max_size_spin.setSuffix(" px")
        alg_layout.addRow("画布扩展安全上限:", self.max_size_spin)

        main_layout.addWidget(alg_group)

        # 2. 行为首选项
        behavior_group = QGroupBox("自动行为")
        behavior_layout = QFormLayout(behavior_group)

        self.auto_enable_cb = QCheckBox("新建或打开文档时自动激活无限画布")
        behavior_layout.addRow(self.auto_enable_cb)

        main_layout.addWidget(behavior_group)

        # 3. 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_cancel = QPushButton("取消")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("保存设置")
        btn_ok.setDefault(True)
        btn_ok.clicked.connect(self._save_and_accept)

        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)
        main_layout.addLayout(btn_layout)

    def _load_values(self):
        self.margin_spin.setValue(self.config.get("margin", 150))
        self.step_spin.setValue(self.config.get("expand_step", 600))
        self.interval_spin.setValue(self.config.get("check_interval", 200))
        self.max_size_spin.setValue(self.config.get("max_canvas_size", 20000))
        self.auto_enable_cb.setChecked(self.config.get("auto_enable", False))

    def _save_and_accept(self):
        self.config["margin"] = self.margin_spin.value()
        self.config["expand_step"] = self.step_spin.value()
        self.config["check_interval"] = self.interval_spin.value()
        self.config["max_canvas_size"] = self.max_size_spin.value()
        self.config["auto_enable"] = self.auto_enable_cb.isChecked()

        save_config(self.config)
        self.accept()
