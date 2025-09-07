### app/pages/login.py ###

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QListWidget, QListWidgetItem, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QPixmap, QFont, QDesktopServices
from PyQt6.QtCore import QUrl
import os

class LoginPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(40, 40, 40, 40)
        root.setSpacing(20)
        root.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Logo
        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_path = "../assets/orbitx_bg_dark_elegant.png"
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path)
            logo.setPixmap(pix.scaledToWidth(260, Qt.TransformationMode.SmoothTransformation))
        root.addWidget(logo)

        # Kullanıcı listesi (başta gizli)
        self.user_list = QListWidget()
        self.user_list.setVisible(False)
        root.addWidget(self.user_list)

        # Giriş butonu
        self.btn_login = QPushButton("Giriş")
        self.btn_login.clicked.connect(self.show_users)
        root.addWidget(self.btn_login)

        # Profil ekle & WhatsApp destek
        btn_row = QHBoxLayout()
        self.btn_add = QPushButton("Profil Ekle")
        self.btn_whatsapp = QPushButton("WhatsApp Destek")
        self.btn_whatsapp.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://wa.me/905551112233")))
        btn_row.addWidget(self.btn_add)
        btn_row.addWidget(self.btn_whatsapp)
        root.addLayout(btn_row)

        # Tarih - saat
        self.lbl_datetime = QLabel()
        self.lbl_datetime.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_datetime.setProperty("variant", "muted")
        root.addWidget(self.lbl_datetime)

        # Timer → her saniye güncellesin
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(1000)
        self.update_datetime()

    def show_users(self):
        # örnek kullanıcılar (bunu db'den alabilirsin)
        users = ["Ahmet", "Mehmet", "Zeynep"]
        self.user_list.clear()
        for u in users:
            QListWidgetItem(u, self.user_list)
        self.user_list.setVisible(True)

    def update_datetime(self):
        now = QDateTime.currentDateTime()
        self.lbl_datetime.setText(now.toString("dd MMMM yyyy — HH:mm:ss"))
