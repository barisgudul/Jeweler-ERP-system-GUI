### app/pages/login.py ###
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit, QFrame,
    QScrollArea, QGridLayout, QToolButton, QSizePolicy, QFileDialog, QDialog,
    QFormLayout, QDialogButtonBox, QMessageBox, QStyle, QGraphicsOpacityEffect, QGraphicsDropShadowEffect,
    QInputDialog
)
from PyQt6.QtCore import Qt, QTimer, QDateTime, pyqtSignal, QLocale, QSize, QUrl, QPropertyAnimation, QEasingCurve, QByteArray
from PyQt6.QtGui import QPixmap, QFont, QDesktopServices, QIcon, QPainter, QColor, QLinearGradient, QBrush
try:
    from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest
    _HAS_NET = True
except Exception:
    _HAS_NET = False
import os, shutil, random
from typing import List, Optional
from theme import elevate, style_button

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

# --- dönen görsel paneli ----------------------------------------------------

class RotatingBanner(QFrame):
    def __init__(self, parent=None, interval_ms=4000):
        super().__init__(parent)
        self.setObjectName("Banner")
        self.setMinimumWidth(240)
        self.setMaximumWidth(500)
        self.setMinimumHeight(350)
        self.setMaximumHeight(750)

        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)

        self.lbl = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.lbl.setScaledContents(True)
        self.lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        v.addWidget(self.lbl)

        # opaklık efekti ve animasyon - daha zarif geçiş
        self.fx = QGraphicsOpacityEffect(self.lbl)
        self.lbl.setGraphicsEffect(self.fx)
        self.anim = QPropertyAnimation(self.fx, b"opacity", self)
        self.anim.setDuration(800)  # biraz daha yavaş ve zarif
        self.anim.setEasingCurve(QEasingCurve.Type.InOutCubic)  # daha yumuşak eğri

        self._items: List[str] = []
        self._idx = -1
        self._timer = QTimer(self); self._timer.timeout.connect(self.next)
        self._timer.start(interval_ms)

        # çerçeve (daha zarif ve yumuşak)
        self.setStyleSheet("""
            QFrame#Banner {
                background: rgba(15,20,35,0.12);
                border: 1px solid rgba(100,150,255,0.15);
                border-radius: 12px;
                padding: 6px;
            }
        """)

        self._nam = QNetworkAccessManager(self) if _HAS_NET else None

    def set_sources(self, paths_or_urls: List[str]):
        self._items = [p for p in paths_or_urls if p]
        self._idx = -1
        self.next(initial=True)

    def _set_pixmap(self, pm: QPixmap):
        # kenarlara doğru çok hafif vignette
        if not pm.isNull():
            self.lbl.setPixmap(pm.scaled(self.lbl.size(), Qt.AspectRatioMode.KeepAspectRatio,
                                         Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self.lbl.pixmap():
            self._set_pixmap(self.lbl.pixmap())

    def next(self, initial=False):
        if not self._items: return
        self._idx = (self._idx + 1) % len(self._items)
        src = self._items[self._idx]

        def _show(pm: QPixmap):
            # fade out -> set -> fade in
            self.anim.stop()
            self.anim.setStartValue(1.0); self.anim.setEndValue(0.0); self.anim.start()
            self.anim.finished.connect(lambda: self._after_fade_out(pm))

        if src.startswith("http"):
            if self._nam:
                reply = self._nam.get(QNetworkRequest(QUrl(src)))
                reply.finished.connect(lambda: _show(QPixmap().loadFromData(reply.readAll()) or QPixmap()))
            else:
                # ağ modülü yoksa atla
                self.next()
        else:
            pm = QPixmap(src)
            _show(pm)

    def _after_fade_out(self, pm: QPixmap):
        self._set_pixmap(pm if isinstance(pm, QPixmap) else QPixmap())
        self.anim.finished.disconnect()
        self.anim.setStartValue(0.0); self.anim.setEndValue(1.0); self.anim.start()

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

        # TR locale - Türkçe ay isimleri için
        tr = QLocale(QLocale.Language.Turkish, QLocale.Country.Turkey)
        QLocale.setDefault(tr)
        # Türkçe ay formatı için
        self.date_format = "dd MMMM yyyy  •  HH:mm:ss"

        # Kullanıcı butonu/ikon boyutları ve görünür satır adedi
        self._USER_BTN_SIZE  = QSize(104, 104)   # önce 120x120 idi → küçülttük
        self._USER_ICON_SIZE = QSize(64, 64)
        self._VISIBLE_ROWS   = 1                 # 1 satır görünsün; fazlası scroll

        # === kozmik arka plan ===
        self._sky = QLabel(self)
        self._sky.lower()
        self._sky.setScaledContents(True)
        self._sky.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # === KÖK GRID (sol banner + sağ içerik) ===
        page = QGridLayout(self)
        page.setContentsMargins(24, 24, 24, 24)
        page.setHorizontalSpacing(16)
        page.setVerticalSpacing(16)

        # Sol: dönen görsel paneli
        self.banner = RotatingBanner(interval_ms=6000)
        self.banner.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        page.addWidget(self.banner, 0, 0, 6, 1)  # 6 satırı kaplasın (logo+boşluk+kart+butonlar+zaman)

        # Sağ: içerik sütunu da GRID
        right = QWidget()
        right_grid = QGridLayout(right)
        right_grid.setContentsMargins(8, 8, 8, 8)
        right_grid.setHorizontalSpacing(12)
        right_grid.setVerticalSpacing(16)
        page.addWidget(right, 0, 1, 6, 1)  # 0'dan başlat, tüm yüksekliği kapsasın

        # Sağ grid'in satırlarına nefes verelim ki kart gerçekten genişleyebilsin
        right_grid.setRowStretch(0, 0)  # logo satırı sabit kalsın
        right_grid.setRowStretch(1, 1)  # kullanıcı kartı büyüsün
        right_grid.setRowStretch(2, 0)  # şifre bar
        right_grid.setRowStretch(3, 0)  # hata etiketi
        right_grid.setRowStretch(4, 0)  # buton bar
        right_grid.setRowStretch(5, 0)  # tarih/saat

        # === logo ===
        self.logo_lbl = QLabel(alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)  # sola yasla, dikey ortala
        logo_file = _asset_path("logo.png")
        if os.path.exists(logo_file):
            pix = QPixmap(logo_file)
            if not pix.isNull():
                TARGET_W = 500  # daha da büyütülmüş logo
                scaled = pix.scaledToWidth(TARGET_W, Qt.TransformationMode.SmoothTransformation)
                self.logo_lbl.setPixmap(scaled)
                self.logo_lbl.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
                self.logo_lbl.setMinimumHeight(scaled.height())
        else:
            t = QLabel("OrbitX", alignment=Qt.AlignmentFlag.AlignHCenter)
            t.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))  # yazı logosunu da büyüttük
            self.logo_lbl = t
        # Logoyu küçük bir kap içine alıp spacing ver
        logo_row = QWidget()
        hl = QHBoxLayout(logo_row)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(0)
        hl.addSpacing(100)  # sola offset
        hl.addWidget(self.logo_lbl, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        hl.addStretch(1)

        # Logoyu sağ kolonun içine koy (z-order sorunu çözüldü)
        right_grid.addWidget(logo_row, 0, 0)

        # --- Kullanıcı Seçim Kartı ---
        self.user_selection_card = QFrame(objectName="Glass")
        elevate(self.user_selection_card, "dim", blur=24, y=6)
        self.user_selection_card.setStyleSheet("""
            QFrame#Glass { background: rgba(25,30,45,0.08);
                           border: 1px solid rgba(80,100,150,0.12);
                           border-radius: 16px; }
        """)
        self.user_selection_card.setMinimumHeight(0)   # daha esnek olsun
        right_grid.addWidget(self.user_selection_card, 1, 0)  # kart 1. satıra

        # === ŞİFRE BAR — KARTIN DIŞINDA, HER ZAMAN GÖRÜNÜR ===
        pw_bar = QFrame()
        pw_bar.setObjectName("Glass")
        pw_bar.setStyleSheet("QFrame#Glass { background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12); border-radius: 12px; }")
        pw = QHBoxLayout(pw_bar); pw.setContentsMargins(8,8,8,8); pw.setSpacing(8)

        self.pass_edit = QLineEdit(placeholderText="Şifre")
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_edit.setMinimumHeight(36)

        self.btn_toggle_pass = QPushButton()
        self.btn_toggle_pass.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarShadeButton))
        self.btn_toggle_pass.setToolTip("Şifreyi göster/gizle")
        self.btn_toggle_pass.setFixedSize(40, 30)
        self.btn_toggle_pass.setFlat(True)
        self.btn_toggle_pass.setStyleSheet("""
            QPushButton { border: none; background: rgba(255,255,255,0.05);
                          border-radius: 6px; color: #B7C0CC; font-size: 12px; padding: 2px; }
            QPushButton:hover { background: rgba(76,125,255,0.1); color: #E9EDF2; }
            QPushButton:pressed { background: rgba(76,125,255,0.2); }
        """)
        self.btn_toggle_pass.clicked.connect(self.toggle_password_visibility)

        self.btn_login = QPushButton("Giriş Yap")
        self.btn_login.setMinimumHeight(36)
        self.btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_login.clicked.connect(self.do_login)
        style_button(self.btn_login, "primary")
        fx = QGraphicsDropShadowEffect(self.btn_login); fx.setBlurRadius(12); fx.setXOffset(0); fx.setYOffset(2); fx.setColor(QColor(0,0,0,60))
        self.btn_login.setGraphicsEffect(fx)

        pw.addWidget(self.pass_edit, 1)
        pw.addWidget(self.btn_toggle_pass, 0)
        pw.addWidget(self.btn_login, 0)

        right_grid.addWidget(pw_bar, 2, 0)    # şifre bar 2. satıra
        self.pass_edit.returnPressed.connect(self.do_login)

        # Hata etiketi hemen altına
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #ff6b6b; font-size: 12px; margin-top: 2px;")
        self.error_label.setVisible(False)
        right_grid.addWidget(self.error_label, 3, 0)  # hata etiketi 3. satıra

        # ❗ GRID YERİNE DİKEY LAYOUT
        self._card_layout = QVBoxLayout(self.user_selection_card)
        self._card_layout.setContentsMargins(20, 16, 20, 16)
        self._card_layout.setSpacing(12)

        # Scroll'lu kullanıcı ızgarası
        self.user_wrap = QWidget()
        self.grid = QGridLayout(self.user_wrap)
        self.grid.setContentsMargins(8, 8, 8, 8)
        self.grid.setHorizontalSpacing(12)
        self.grid.setVerticalSpacing(12)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.scroll = QScrollArea(frameShape=QFrame.Shape.NoFrame)
        self.scroll.setWidget(self.user_wrap)
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea, QScrollArea * { background: transparent; }")
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Üste ekle ve büyüyebilir yap
        self._card_layout.addWidget(self.scroll, 1)   # stretch=1

        # Sağ kolon buton barı (şimdilik oluştur, sonra yerleştir)
        btn_bar = QFrame()
        btn_lay = QHBoxLayout(btn_bar)
        btn_lay.setContentsMargins(0, 0, 0, 0)
        btn_lay.setSpacing(6)

        self.btn_edit_user = QPushButton("Profil Düzenle"); self.btn_edit_user.setEnabled(False)
        self.btn_del_user  = QPushButton("Profil Sil");     self.btn_del_user.setEnabled(False)
        self.btn_add       = QPushButton("Profil Ekle")
        self.btn_whatsapp  = QPushButton("WhatsApp Destek")

        style_button(self.btn_edit_user, "neutral")
        style_button(self.btn_del_user,  "danger")
        style_button(self.btn_add,       "primary")
        style_button(self.btn_whatsapp,  "success")
        for b in (self.btn_edit_user, self.btn_del_user, self.btn_add, self.btn_whatsapp):
            b.setMinimumHeight(36); b.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_lay.addWidget(self.btn_edit_user)
        btn_lay.addWidget(self.btn_del_user)
        btn_lay.addWidget(self.btn_add)
        btn_lay.addStretch(1)
        btn_lay.addWidget(self.btn_whatsapp)
        right_grid.addWidget(btn_bar, 4, 0)       # buton bar 4. satıra

        # Tarih/saat
        self.lbl_datetime = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.lbl_datetime.setProperty("variant", "muted")
        right_grid.addWidget(self.lbl_datetime, 5, 0)  # tarih/saat 5. satıra

        # ROW/COL STRETCH: banner ve kart nefes alsın
        page.setColumnStretch(0, 4)  # sol (banner'ı biraz küçült)
        page.setColumnStretch(1, 8)  # sağ (logo için daha geniş alan)
        page.setColumnMinimumWidth(1, 620)  # 500 logo + 100 offset + pay

        # --- veriler ---
        self._users = ["Barış", "Mehmet", "Hakan"]
        self._user_buttons = []
        self._selected_user: Optional[str] = None
        self.placeholder_icon = _profile_placeholder_icon()

        # banner görselleri
        assets_dir = _asset_path()
        sources = [p for p in [os.path.join(assets_dir, "kalp.png"), _asset_path("logo.png")] if os.path.exists(p)]
        self.banner.set_sources(sources or [])

        # kullanıcı ızgarası
        self._cols_current = 5  # başlangıç
        self.show_users()
        self._update_profiles_viewport_height()
        self.pass_edit.returnPressed.connect(self.do_login)

        # buton aksiyonları
        self.btn_edit_user.clicked.connect(self.edit_user)
        self.btn_del_user.clicked.connect(self.delete_user)
        self.btn_add.clicked.connect(self.add_profile)
        self.btn_whatsapp.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://wa.me/905551112233")))

        # saat
        t = QTimer(self); t.timeout.connect(self.update_datetime); t.start(1000)
        self.update_datetime()


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

    # --- responsive kullanıcı ızgarası (en çok 5 sütun)
    def _calc_cols(self) -> int:
        # Kullanıcı kartı içine göre yaklaşık buton genişliği 120 + boşluklar ≈ 140
        wrap_w = max(0, self.user_selection_card.width() - 80)
        guess = max(1, min(5, wrap_w // 140))
        return guess

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._sky.resize(self.size())
        self._paint_sky(self.width(), self.height())

        # 1 satırda en çok 5 kullanıcı hesabı kuralını koruyalım
        new_cols = self._calc_cols()
        if new_cols != self._cols_current:
            self._cols_current = new_cols
            self._reflow_users()

        self._update_profiles_viewport_height()

        # LOGO'nun görünür kalması için dinamik üst boşluk (ekranın ~%20'si)
        if hasattr(self, "logo_gap"):
            gap = max(180, min(340, int(self.height() * 0.20)))  # %20 oran, 180–340 aralığı
            self.logo_gap.setFixedHeight(gap)

    def _reflow_users(self):
        # seçili kişi korunarak grid'i yeniden diz
        sel = self._selected_user
        self.show_users()
        if sel and sel in self._users:
            for b in self._user_buttons:
                if b.text() == sel:
                    b.setChecked(True); break
        self._update_profiles_viewport_height()

    # --- Scroll yüksekliğini senkronlayan yardımcı
    def _update_profiles_viewport_height(self):
        # Grid içi marjin/spacing değerlerine göre tam 1 satır yüksekliği hesapla
        m   = self.grid.contentsMargins()          # (8,8,8,8)
        vsp = self.grid.verticalSpacing()          # 12
        btn_h = self._USER_BTN_SIZE.height()       # 104
        rows  = self._VISIBLE_ROWS                 # 1

        h = m.top() + m.bottom() + rows*btn_h + (rows-1)*vsp
        # Scroll penceresini kilitle
        self.scroll.setFixedHeight(h)

        # Kartın dış marjinlerini de ekleyip kartın büyümesini sınırla
        cm = self._card_layout.contentsMargins()   # (20,16,20,16)
        self.user_selection_card.setMaximumHeight(h + cm.top() + cm.bottom())

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
        self._clear_grid()
        cols = self._cols_current  # ⬅️ responsive, 1..5
        for i, name in enumerate(self._users):
            btn = QToolButton()
            btn.setCheckable(True); btn.setAutoExclusive(True)
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setIcon(self._user_icon_for(name))
            btn.setIconSize(self._USER_ICON_SIZE)      # 64x64
            btn.setText(name)
            btn.setFixedSize(self._USER_BTN_SIZE)      # 104x104
            btn.setProperty("role", "usercard")
            btn.clicked.connect(lambda checked, n=name: self._select_user(n))
            r, c = divmod(i, cols)
            self.grid.addWidget(btn, r, c, Qt.AlignmentFlag.AlignCenter)
            self._user_buttons.append(btn)
        if self._user_buttons:
            self._user_buttons[0].setChecked(True)
            self._selected_user = self._users[0]
            self.pass_edit.setFocus()

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
        # Türkçe ay isimleri ile tarih gösterimi
        turkish_locale = QLocale(QLocale.Language.Turkish, QLocale.Country.Turkey)
        self.lbl_datetime.setText(turkish_locale.toString(now, self.date_format))

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

        # listemize ekleyip varsa grid'i güncelle
        self._users.append(name)
        if self.scroll.isVisible():
            self.show_users()  # yeniden çiz
            # Yeni eklenen kullanıcı görünürde en alttaysa otomatik olarak aşağı kaydır
            QTimer.singleShot(0, lambda: self.scroll.verticalScrollBar().setValue(
                self.scroll.verticalScrollBar().maximum()))

    def delete_user(self):
        if not self._selected_user:
            return

        # Kullanıcı listede var mı kontrol et
        if self._selected_user not in self._users:
            QMessageBox.warning(self, "Uyarı", "Seçili kullanıcı bulunamadı.")
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
