# app/sidebar.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import pyqtSignal

class Sidebar(QWidget):
    routeChanged = pyqtSignal(str)  # "dashboard", "stock" ...

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(200)

        v = QVBoxLayout(self)
        v.setContentsMargins(12, 12, 12, 12)
        v.setSpacing(8)

        title = QLabel("Kuyumcu ERP")
        title.setProperty("variant", "title")
        v.addWidget(title)
        v.addSpacing(6)

        self.buttons = {}
        for key, text in [("dashboard", "Dashboard"), ("stock", "Stok")]:
            b = QPushButton(text)
            b.setCheckable(True)
            b.setProperty("nav", True)
            b.clicked.connect(lambda checked, k=key: self._on_click(k))
            v.addWidget(b)
            self.buttons[key] = b

        v.addStretch(1)

        # Hafif highlight stili (temayı bozmadan)
        self.setStyleSheet("""
        QPushButton[nav="true"] {
            text-align: left;
            padding: 10px 12px;
            border-radius: 10px;
        }
        QPushButton[nav="true"]:checked {
            background: rgba(255,255,255,0.08);
            border-color: rgba(255,255,255,0.18);
        }
        """)

        self.set_active("dashboard")

    def _on_click(self, key: str):
        self.set_active(key)
        self.routeChanged.emit(key)

    def set_active(self, key: str):
        for k, b in self.buttons.items():
            b.setChecked(k == key)
