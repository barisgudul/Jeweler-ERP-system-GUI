# app/sidebar.py

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QPainter, QLinearGradient, QColor, QFont, QIcon
from random import randint
from theme import elevate
import os

class Sidebar(QWidget):
    routeChanged = pyqtSignal(str)  # "dashboard", "stock" ...

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(280)

        # === KOZMİK ARKA PLAN ===
        self._sky = QLabel(self)
        self._sky.lower()  # en arkada dursun
        self._sky.setScaledContents(True)
        self._sky.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Ana container - şeffaf
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # === ORBITX LOGO ===
        logo_frame = QFrame()
        logo_frame.setObjectName("Glass")
        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.setContentsMargins(20, 20, 20, 20)

        # Logo için QLabel oluştur (image için)
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # orbitx.png dosyasını yükle
        assets_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(assets_dir, "assets", "orbitx.png")

        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                # Logo'yu uygun boyuta ölçeklendir (sidebar genişliğine göre)
                scaled_pixmap = pixmap.scaledToWidth(200, Qt.TransformationMode.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
            else:
                # Pixmap yüklenemediyse fallback olarak text göster
                logo_label.setText("OrbitX")
                logo_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
                logo_label.setStyleSheet("""
                    QLabel {
                        color: #E9EDF2;
                        font-weight: 700;
                        text-align: center;
                        letter-spacing: 1px;
                    }
                """)
        else:
            # Dosya bulunamadıyse fallback olarak text göster
            logo_label.setText("OrbitX")
            logo_label.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
            logo_label.setStyleSheet("""
                QLabel {
                    color: #E9EDF2;
                    font-weight: 700;
                    text-align: center;
                    letter-spacing: 1px;
                }
            """)

        logo_layout.addWidget(logo_label)

        # Logo için gölge efekti
        elevate(logo_frame, scheme="dim", blur=20, y=6)
        main_layout.addWidget(logo_frame)

        # === NAVIGATION MENU ===
        nav_frame = QFrame()
        nav_frame.setObjectName("Glass")
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(16, 16, 16, 16)
        nav_layout.setSpacing(6)

        # Navigation başlık
        nav_title = QLabel("Navigasyon")
        nav_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        nav_title.setStyleSheet("""
            color: #9CA6B4;
            letter-spacing: 1px;
            text-align: center;
            padding: 4px 0px;
        """)
        nav_layout.addWidget(nav_title)
        nav_layout.addSpacing(16)

        # Navigation butonları
        self.buttons = {}

        nav_items = [
            ("dashboard", "Dashboard", "Ana gösterge paneli"),
            ("stock", "Stok Yönetimi", "Ürün ve envanter"),
            ("customers", "Cari Hesap", "Müşteri yönetimi"),
            ("sales", "Alış–Satış", "İşlemler ve makbuz"),
            ("finance", "Kasa & Finans", "Kasa defteri ve banka")
        ]

        for key, text, tooltip in nav_items:
            btn = self._create_nav_button(text, tooltip)
            btn.clicked.connect(lambda checked, k=key: self._on_click(k))
            nav_layout.addWidget(btn)
            self.buttons[key] = btn

        nav_layout.addStretch(1)
        elevate(nav_frame, scheme="dim", blur=16, y=4)
        main_layout.addWidget(nav_frame)

        # İlk render sonrası arka planı çiz
        self.resizeEvent(None)

        self.set_active("dashboard")

    def _create_nav_button(self, text: str, tooltip: str) -> QPushButton:
        """Zarif navigation butonu oluştur"""
        btn = QPushButton(text)
        btn.setCheckable(True)
        btn.setProperty("nav", True)
        btn.setToolTip(tooltip)

        # Zarif buton stilleri
        btn.setStyleSheet("""
            QPushButton[nav="true"] {
                text-align: left;
                padding: 16px 20px;
                border-radius: 16px;
                background: rgba(255,255,255,0.02);
                border: 1px solid rgba(255,255,255,0.03);
                color: #C7CCD1;
                font-size: 14px;
                font-weight: 500;
                min-height: 24px;
                letter-spacing: 0.5px;
                margin: 2px 0px;
            }
            QPushButton[nav="true"]:hover {
                border-color: #97B7FF;
                background: rgba(76,125,255,0.07);
                color: #F1F4F8;
                border-width: 1px;
            }
            QPushButton[nav="true"]:checked {
                border-color: #4C7DFF;
                border-width: 2px;
                background: rgba(76,125,255,0.10);
                color: #E9EDF2;
                font-weight: 600;
            }
            QPushButton[nav="true"]:pressed {
                background: rgba(76,125,255,0.15);
            }
        """)
        return btn

    def _on_click(self, key: str):
        self.set_active(key)
        self.routeChanged.emit(key)

    def set_active(self, key: str):
        for k, b in self.buttons.items():
            b.setChecked(k == key)

    # === Arkaya yıldızlı gökyüzü çiz ===
    def _paint_sky(self, w: int, h: int):
        if w <= 0 or h <= 0:
            return
        pm = QPixmap(w, h)
        pm.fill(Qt.GlobalColor.black)

        painter = QPainter(pm)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Gradient (nebula hissi)
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor(10, 16, 32))   # koyu lacivert
        grad.setColorAt(0.5, QColor(20, 26, 48))
        grad.setColorAt(1.0, QColor(12, 18, 36))
        painter.fillRect(0, 0, w, h, grad)

        # Yıldızlar (çok küçük, düşük opak)
        painter.setPen(Qt.PenStyle.NoPen)
        for _ in range(int((w * h) / 20000)):  # yoğunluk
            x = randint(0, w)
            y = randint(0, h)
            r = randint(1, 2)
            c = QColor(255, 255, 255, randint(60, 140))
            painter.setBrush(c)
            painter.drawEllipse(x, y, r, r)

        painter.end()
        self._sky.setPixmap(pm)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._sky.resize(self.size())
        self._paint_sky(self.width(), self.height())
