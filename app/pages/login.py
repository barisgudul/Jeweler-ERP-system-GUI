### app/pages/login.py ###
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit, QFrame,
    QScrollArea, QGridLayout, QToolButton, QSizePolicy, QFileDialog, QDialog,
    QFormLayout, QDialogButtonBox, QMessageBox, QStyle
)
from PyQt6.QtCore import Qt, QTimer, QDateTime, pyqtSignal, QLocale, QSize, QUrl
from PyQt6.QtGui import QPixmap, QFont, QDesktopServices, QIcon, QPainter, QColor, QLinearGradient, QBrush
import os, shutil, random
from typing import List, Optional
from theme import elevate

# --- yardımcılar --------------------------------------------------------------

def _asset_path(*parts: str) -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, "..", "assets", *parts))

def _ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

# Basit “kafa+gövde” silueti çizen circular avatar (88x88)
def _profile_placeholder_icon() -> QIcon:
    size = 88
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)

    # dış daire (soft)
    p.setBrush(QColor(255, 255, 255, 22))
    p.setPen(QColor(255, 255, 255, 60))
    p.drawEllipse(2, 2, size-4, size-4)

    # iç siluet
    cx, cy = size//2, size//2
    # kafa
    p.setBrush(QColor(255, 255, 255, 140))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(cx-14, cy-18, 28, 28)
    # gövde (yarım elips)
    body = QPixmap(size, size)
    body.fill(Qt.GlobalColor.transparent)
    p2 = QPainter(body); p2.setRenderHint(QPainter.RenderHint.Antialiasing)
    p2.setBrush(QColor(255, 255, 255, 120))
    p2.setPen(Qt.PenStyle.NoPen)
    p2.drawRoundedRect(cx-24, cy-2, 48, 34, 16, 16)
    p2.end()
    p.drawPixmap(0, 0, body)

    p.end()
    return QIcon(pm)

#  Fotoğrafı dairesel kırp + 88x88’e ölçekle
def _circular_avatar_from_file(path: str) -> Optional[QIcon]:
    pm = QPixmap(path)
    if pm.isNull():
        return None
    pm = pm.scaled(88, 88, Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                   Qt.TransformationMode.SmoothTransformation)

    mask = QPixmap(88, 88); mask.fill(Qt.GlobalColor.transparent)
    p = QPainter(mask); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(Qt.GlobalColor.white); p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(0, 0, 88, 88); p.end()

    final = QPixmap(88, 88); final.fill(Qt.GlobalColor.transparent)
    p = QPainter(final); p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setClipRegion(mask.createHeuristicMask().region())
    p.drawPixmap(0, 0, pm); p.end()
    return QIcon(final)

# --- Profil Ekle diyaloğu ----------------------------------------------------

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Profil Ekle")
        self._photo_path: Optional[str] = None

        v = QVBoxLayout(self)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.in_name = QLineEdit()
        self.in_name.setPlaceholderText("Örn: Ahmet")
        form.addRow("Ad", self.in_name)

        self.lbl_photo = QLabel("Fotoğraf seçilmedi")
        self.btn_pick = QPushButton("Fotoğraf Seç…")
        self.btn_pick.clicked.connect(self.pick_photo)

        hl = QHBoxLayout()
        hl.addWidget(self.lbl_photo)
        hl.addStretch(1)
        hl.addWidget(self.btn_pick)
        v.addLayout(form)
        v.addLayout(hl)

        self.btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok |
                                     QDialogButtonBox.StandardButton.Cancel)
        self.btns.accepted.connect(self.accept)
        self.btns.rejected.connect(self.reject)
        v.addWidget(self.btns)

        self.in_name.textChanged.connect(self._validate)
        self._validate()

    def _validate(self):
        ok = bool(self.in_name.text().strip())
        self.btns.button(QDialogButtonBox.StandardButton.Ok).setEnabled(ok)

    def pick_photo(self):
        path, _ = QFileDialog.getOpenFileName(self, "Fotoğraf Seç",
                                              "", "Görseller (*.png *.jpg *.jpeg *.webp)")
        if path:
            self._photo_path = path
            self.lbl_photo.setText(os.path.basename(path))

    def data(self):
        return {
            "name": self.in_name.text().strip(),
            "photo": self._photo_path
        }

# --- Login sayfası -----------------------------------------------------------

class LoginPage(QWidget):
    loggedIn = pyqtSignal(dict)  # {"user": "Ahmet"}

    def __init__(self, parent=None):
        super().__init__(parent)

        # TR locale
        tr = QLocale(QLocale.Language.Turkish, QLocale.Country.Turkey)
        QLocale.setDefault(tr)

        # === kozmik arka plan ===
        self._sky = QLabel(self)
        self._sky.lower()
        self._sky.setScaledContents(True)
        self._sky.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 32, 32, 32)
        root.setSpacing(16)
        root.setAlignment(Qt.AlignmentFlag.AlignTop)

        # === logo ===
        logo_lbl = QLabel(alignment=Qt.AlignmentFlag.AlignHCenter)
        logo_file = _asset_path("logo.png")
        if os.path.exists(logo_file):
            pix = QPixmap(logo_file)
            if not pix.isNull():
                logo_lbl.setPixmap(pix.scaledToWidth(340, Qt.TransformationMode.SmoothTransformation))
        else:
            t = QLabel("OrbitX", alignment=Qt.AlignmentFlag.AlignHCenter)
            t.setFont(QFont("Segoe UI", 28, QFont.Weight.Black))
            logo_lbl = t
        root.addWidget(logo_lbl)

        subtitle = QLabel("Kuyumcu ERP • Güvenli Giriş", alignment=Qt.AlignmentFlag.AlignHCenter)
        subtitle.setProperty("variant", "muted")
        root.addWidget(subtitle)

        # --- 1. Karşılama Kartı (Başlangıçta Görünür) ---
        self.welcome_card = QFrame(objectName="Glass")
        elevate(self.welcome_card, "dim", blur=8, y=2)
        # Şık ve dengeli tasarım - hafif görünür kart
        self.welcome_card.setStyleSheet("""
            QFrame#Glass {
                background: rgba(20,26,48,0.3);
                border: 1px solid rgba(76,125,255,0.2);
                border-radius: 20px;
            }
        """)
        welcome_layout = QVBoxLayout(self.welcome_card)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_layout.setContentsMargins(60, 60, 60, 60)
        welcome_layout.setSpacing(25)

        # Kartın minimum boyutunu ayarla
        self.welcome_card.setMinimumWidth(500)
        self.welcome_card.setMinimumHeight(300)

        welcome_text = QLabel("OrbitX ERP'ye Hoş Geldiniz")
        welcome_text.setFont(QFont("Segoe UI", 24, QFont.Weight.Black))
        welcome_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Daha şık ve tıklanmaz görünen tasarım
        welcome_text.setStyleSheet("""
            color: #FFFFFF;
            background-color: rgba(0, 0, 0, 0.15);
            font-weight: 900;
            padding: 15px 20px;
            border-radius: 12px;
            border: 1px solid rgba(76,125,255,0.1);
            margin: 8px;
        """)
        welcome_layout.addWidget(welcome_text)

        welcome_subtext = QLabel("Devam etmek için lütfen aşağıdaki 'Kullanıcıları Göster' butonuna tıklayın.")
        welcome_subtext.setProperty("variant", "muted") # Bu satır kalabilir ama stil baskın olacak
        welcome_subtext.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_subtext.setWordWrap(True)
        welcome_subtext.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        # Daha şık ve tıklanmaz görünen tasarım
        welcome_subtext.setStyleSheet("""
            color: #FFFFFF;
            background-color: rgba(0, 0, 0, 0.1);
            font-weight: 700;
            padding: 12px 18px;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.05);
            margin: 6px;
        """)
        welcome_layout.addWidget(welcome_subtext)

        root.addWidget(self.welcome_card)

        # --- 2. Kullanıcı Seçim Kartı (Başlangıçta Gizli) ---
        self.user_selection_card = QFrame(objectName="Glass")
        self.user_selection_card.setVisible(False)
        elevate(self.user_selection_card, "dim", blur=24, y=6)
        card_lay = QVBoxLayout(self.user_selection_card); card_lay.setContentsMargins(20, 20, 20, 20); card_lay.setSpacing(12)

        self.user_wrap = QWidget()
        self.grid = QGridLayout(self.user_wrap)
        self.grid.setContentsMargins(8, 8, 8, 8)
        self.grid.setHorizontalSpacing(12)
        self.grid.setVerticalSpacing(12)

        self.scroll = QScrollArea(frameShape=QFrame.Shape.NoFrame)
        self.scroll.setWidget(self.user_wrap); self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea, QScrollArea * { background: transparent; }")
        self.scroll.setVisible(False)
        card_lay.addWidget(self.scroll)

        self.pass_edit = QLineEdit(placeholderText="Şifre")
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_edit.setVisible(False)

        # Şifre göster/gizle butonu - Daha anlaşılır tasarım
        pass_layout = QHBoxLayout()
        pass_layout.setContentsMargins(0, 0, 0, 0)
        pass_layout.addWidget(self.pass_edit)

        self.btn_toggle_pass = QPushButton()
        self.btn_toggle_pass.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarShadeButton))  # Göz ikonu yerine standart ikon
        self.btn_toggle_pass.setToolTip("Şifreyi göster/gizle")
        self.btn_toggle_pass.setFixedSize(40, 30)
        self.btn_toggle_pass.setFlat(True)
        self.btn_toggle_pass.setStyleSheet("""
            QPushButton {
                border: none;
                background: rgba(255,255,255,0.05);
                border-radius: 6px;
                color: #B7C0CC;
                font-size: 12px;
                padding: 2px;
            }
            QPushButton:hover {
                background: rgba(76,125,255,0.1);
                color: #E9EDF2;
            }
            QPushButton:pressed {
                background: rgba(76,125,255,0.2);
            }
        """)
        self.btn_toggle_pass.clicked.connect(self.toggle_password_visibility)
        pass_layout.addWidget(self.btn_toggle_pass)

        card_lay.addLayout(pass_layout)

        # Hatalı giriş uyarısı için label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ff6b6b; font-size: 12px; margin-top: 4px;")
        self.error_label.setVisible(False)
        card_lay.addWidget(self.error_label)

        root.addWidget(self.user_selection_card)

        # === butonlar ===
        buttons = QHBoxLayout()
        self.btn_show = QPushButton("Kullanıcıları Göster"); self.btn_show.clicked.connect(self.show_users)
        self.btn_login = QPushButton("Giriş Yap"); self.btn_login.clicked.connect(self.do_login); self.btn_login.setVisible(False)
        self.btn_add = QPushButton("Profil Ekle"); self.btn_add.clicked.connect(self.add_profile)
        self.btn_whatsapp = QPushButton("WhatsApp Destek")
        self.btn_whatsapp.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://wa.me/905551112233")))

        self.btn_del_user = QPushButton("Profil Sil")
        self.btn_del_user.setEnabled(False)
        self.btn_del_user.clicked.connect(self.delete_user)
        self.btn_edit_user = QPushButton("Profil Düzenle")
        self.btn_edit_user.setEnabled(False)
        self.btn_edit_user.clicked.connect(self.edit_user)

        buttons.addWidget(self.btn_show)
        buttons.addWidget(self.btn_login)
        buttons.addWidget(self.btn_edit_user)
        buttons.addWidget(self.btn_del_user)
        buttons.addStretch(1)
        buttons.addWidget(self.btn_add)
        buttons.addWidget(self.btn_whatsapp)
        root.addLayout(buttons)

        # === tarih/saat ===
        self.lbl_datetime = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.lbl_datetime.setProperty("variant", "muted")
        t = QTimer(self); t.timeout.connect(self.update_datetime); t.start(1000)
        self.update_datetime()
        root.addWidget(self.lbl_datetime)

        # veri
        self._users: List[str] = ["Ahmet", "Mehmet", "Zeynep"]
        self._user_buttons: List[QToolButton] = []
        self._selected_user: Optional[str] = None

        # ikonlar
        self.placeholder_icon = _profile_placeholder_icon()

    # --- gökyüzü çizimi
    def _paint_sky(self, w: int, h: int):
        if w <= 0 or h <= 0: return
        pm = QPixmap(w, h); pm.fill(Qt.GlobalColor.black)
        p = QPainter(pm); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor(10,16,32)); grad.setColorAt(0.5, QColor(20,26,48)); grad.setColorAt(1.0, QColor(12,18,36))
        p.fillRect(0, 0, w, h, grad)
        p.setPen(Qt.PenStyle.NoPen)
        for _ in range(int((w*h)/12000)):
            x, y = random.randint(0,w), random.randint(0,h)
            r = random.choice([1,1,2])
            p.setBrush(QColor(255,255,255, random.randint(70,160)))
            p.drawEllipse(x, y, r, r)
        p.end()
        self._sky.setPixmap(pm)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._sky.resize(self.size())
        self._paint_sky(self.width(), self.height())

    # --- grid helpers
    def _clear_grid(self):
        for b in self._user_buttons: b.setParent(None)
        self._user_buttons.clear()
        while self.grid.count():
            it = self.grid.takeAt(0); w = it.widget()
            if w: w.deleteLater()

    def _user_icon_for(self, name: str) -> QIcon:
        fn = _asset_path("users", f"{name}.png")
        if os.path.exists(fn):
            ic = _circular_avatar_from_file(fn)
            if ic: return ic
        return self.placeholder_icon

    def show_users(self):
        self.welcome_card.setVisible(False)      # Karşılama kartını gizle
        self.user_selection_card.setVisible(True) # Kullanıcı kartını göster
        self._clear_grid()
        cols = 6
        for i, name in enumerate(self._users):
            btn = QToolButton()
            btn.setCheckable(True); btn.setAutoExclusive(True)
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setIcon(self._user_icon_for(name)); btn.setIconSize(QSize(72, 72))
            btn.setText(name)
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            btn.setFixedSize(120, 120)
            btn.setProperty("role", "usercard")
            btn.clicked.connect(lambda checked, n=name: self._select_user(n))
            r, c = divmod(i, cols)
            self.grid.addWidget(btn, r, c, Qt.AlignmentFlag.AlignCenter)
            self._user_buttons.append(btn)
        self.scroll.setVisible(True); self.pass_edit.setVisible(True); self.btn_login.setVisible(True)
        if self._user_buttons:
            self._user_buttons[0].setChecked(True); self._selected_user = self._users[0]; self.pass_edit.setFocus()

    def _select_user(self, name: str):
        self._selected_user = name
        # Hata mesajını gizle
        self.error_label.setVisible(False)
        # Kullanıcı yönetimi butonlarını etkinleştir
        self.btn_edit_user.setEnabled(True)
        self.btn_del_user.setEnabled(True)

    def toggle_password_visibility(self):
        if self.pass_edit.echoMode() == QLineEdit.EchoMode.Password:
            self.pass_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_toggle_pass.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarUnshadeButton))
            self.btn_toggle_pass.setToolTip("Şifreyi gizle")
        else:
            self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_toggle_pass.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarShadeButton))
            self.btn_toggle_pass.setToolTip("Şifreyi göster")

    def do_login(self):
        if not self._selected_user:
            return

        # Basit şifre kontrolü (mock)
        entered_password = self.pass_edit.text().strip()
        if entered_password == "1234":  # Mock şifre
            self.error_label.setVisible(False)
            self.loggedIn.emit({"user": self._selected_user})
        else:
            self.error_label.setText("Kullanıcı adı veya şifre hatalı.")
            self.error_label.setVisible(True)
            self.pass_edit.setFocus()
            self.pass_edit.selectAll()

    def update_datetime(self):
        now = QDateTime.currentDateTime()
        self.lbl_datetime.setText(now.toString("dd MMMM yyyy  •  HH:mm:ss"))

    # --- Profil Ekle akışı
    def add_profile(self):
        dlg = AddUserDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted: return
        data = dlg.data()
        name = data["name"]
        photo = data["photo"]

        # isim benzersiz kalsın
        if name in self._users:
            base, k = name, 2
            while f"{base}{k}" in self._users:
                k += 1
            name = f"{base}{k}"

        # fotoğrafı assets/users/<name>.png olarak kaydet
        users_dir = _asset_path("users")
        _ensure_dir(users_dir)
        if photo:
            # hedef yol
            dst = os.path.join(users_dir, f"{name}.png")
            try:
                # PNG'e dönüştürmek için QPixmap üzerinden kaydedelim (her formatı kabul etsin)
                pm = QPixmap(photo)
                if not pm.isNull():
                    pm.save(dst, "PNG")
                else:
                    shutil.copyfile(photo, dst)
            except Exception:
                pass

        # listemize ekleyip varsa grid’i güncelle
        self._users.append(name)
        if self.scroll.isVisible():
            self.show_users()  # yeniden çiz

    def delete_user(self):
        if not self._selected_user:
            return

        reply = QMessageBox.question(self, "Onay",
                                     f"{self._selected_user} profilini silmek istediğinizden emin misiniz?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            # Fotoğraf dosyasını da sil
            photo_path = _asset_path("users", f"{self._selected_user}.png")
            if os.path.exists(photo_path):
                try:
                    os.remove(photo_path)
                except Exception:
                    pass

            # Kullanıcıyı listeden çıkar
            self._users.remove(self._selected_user)
            self._selected_user = None

            # Butonları devre dışı bırak
            self.btn_edit_user.setEnabled(False)
            self.btn_del_user.setEnabled(False)

            # Grid'i yeniden çiz
            if self.scroll.isVisible():
                self.show_users()

            QMessageBox.information(self, "Başarılı", "Profil başarıyla silindi.")

    def edit_user(self):
        if not self._selected_user:
            return

        # Düzenleme diyaloğu (şimdilik basit isim değişikliği)
        from PyQt6.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(self, "Profil Düzenle",
                                           "Yeni ad:", text=self._selected_user)
        if ok and new_name.strip() and new_name.strip() != self._selected_user:
            new_name = new_name.strip()

            # İsim çakışması kontrolü
            if new_name in self._users:
                QMessageBox.warning(self, "Uyarı", "Bu isim zaten kullanılıyor.")
                return

            # Eski fotoğrafı yeni isme taşı
            old_photo = _asset_path("users", f"{self._selected_user}.png")
            new_photo = _asset_path("users", f"{new_name}.png")
            if os.path.exists(old_photo):
                try:
                    os.rename(old_photo, new_photo)
                except Exception:
                    pass

            # Listeyi güncelle
            idx = self._users.index(self._selected_user)
            self._users[idx] = new_name
            self._selected_user = new_name

            # Grid'i yeniden çiz
            if self.scroll.isVisible():
                self.show_users()

            QMessageBox.information(self, "Başarılı", "Profil başarıyla güncellendi.")
