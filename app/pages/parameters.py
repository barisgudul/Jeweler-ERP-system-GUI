# app/pages/parameters.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt, QLocale, QSettings
from PyQt6.QtGui import QFont, QPixmap, QPainter, QLinearGradient, QColor
from random import randint
from theme import elevate

TR = QLocale(QLocale.Language.Turkish, QLocale.Country.Turkey)

class ParametersPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # — kozmik arka plan
        self._sky = QLabel(self)
        self._sky.lower()  # en arkada dursun
        self._sky.setScaledContents(True)
        self._sky.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # — başlık
        header = QHBoxLayout()
        title = QLabel("Parametreler")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #E9EDF2; font-weight: 700;")
        header.addWidget(title, 0, Qt.AlignmentFlag.AlignLeft)

        hint = QLabel("Sistem ayarları ve yapılandırma")
        hint.setProperty("variant", "muted")
        hint.setStyleSheet("font-size: 12px;")
        header.addWidget(hint, 0, Qt.AlignmentFlag.AlignRight)
        root.addLayout(header)

        # Ana kart
        card = QFrame(objectName="Glass")
        elevate(card, "dim", blur=24, y=6)
        root.addWidget(card)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(8)

        # Kart başlığı
        card_title = QLabel("Sistem Parametreleri")
        card_title.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))
        card_title.setStyleSheet("color: #E9EDF2; margin-bottom: 2px;")
        card_layout.addWidget(card_title)

        # Form container
        form_container = QWidget()
        form = QFormLayout(form_container)
        form.setContentsMargins(0, 0, 0, 0)
        form.setSpacing(10)
        card_layout.addWidget(form_container)

        # ortak küçük input stili
        small_input_css = """
            padding: 8px 10px;
            border-radius: 8px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.12);
            color: #E9EDF2;
            font-size: 12px;
        """

        self.ed_company = QLineEdit()
        self.ed_company.setStyleSheet(small_input_css)

        self.ed_taxno = QLineEdit()
        self.ed_taxno.setStyleSheet(small_input_css)

        self.ed_addr = QLineEdit()
        self.ed_addr.setStyleSheet(small_input_css)

        self.ed_phone = QLineEdit()
        self.ed_phone.setStyleSheet(small_input_css)

        self.ed_prefix = QLineEdit()
        self.ed_prefix.setPlaceholderText("SAT-")
        self.ed_prefix.setStyleSheet(small_input_css)

        self.sp_digits = QSpinBox()
        self.sp_digits.setRange(3,10)
        self.sp_digits.setValue(6)
        self.sp_digits.setStyleSheet(f"QSpinBox{{{small_input_css}}}")

        self.cmb_reset = QComboBox()
        self.cmb_reset.addItems(["Sıfırlama yok","Yıllık","Aylık"])
        self.cmb_reset.setStyleSheet(f"QComboBox{{{small_input_css}}}")

        self.cmb_curr = QComboBox()
        self.cmb_curr.addItems(["TRY","USD","EUR"])
        self.cmb_curr.setStyleSheet(f"QComboBox{{{small_input_css}}}")

        self.sp_dec = QSpinBox()
        self.sp_dec.setRange(0,4)
        self.sp_dec.setValue(2)
        self.sp_dec.setStyleSheet(f"QSpinBox{{{small_input_css}}}")

        self.cmb_theme = QComboBox()
        self.cmb_theme.addItems(["dark","dim","light"])
        self.cmb_theme.setStyleSheet(f"QComboBox{{{small_input_css}}}")

        form.addRow("Şirket Adı", self.ed_company)
        form.addRow("VKN/TCKN", self.ed_taxno)
        form.addRow("Adres", self.ed_addr)
        form.addRow("Telefon", self.ed_phone)
        form.addRow("Belge Prefix", self.ed_prefix)
        form.addRow("Sıra No Hane", self.sp_digits)
        form.addRow("Sıfırlama", self.cmb_reset)
        form.addRow("Para Birimi", self.cmb_curr)
        form.addRow("Ondalık", self.sp_dec)
        form.addRow("Tema", self.cmb_theme)

        # Butonlar
        buttons_layout = QHBoxLayout()
        self.btn_save = QPushButton("Kaydet")
        self.btn_reset = QPushButton("Varsayılanlara Dön")
        buttons_layout.addWidget(self.btn_save)
        buttons_layout.addWidget(self.btn_reset)
        card_layout.addLayout(buttons_layout)

        # Stretch ekleyelim
        card_layout.addStretch(1)

        # Load
        self._load()
        # Save
        self.btn_save.clicked.connect(self._save)
        self.btn_reset.clicked.connect(self._reset_defaults)

    def _settings(self):
        return QSettings("OrbitX", "KuyumcuERP")

    def _load(self):
        s = self._settings()
        self.ed_company.setText(s.value("company/name",""))
        self.ed_taxno.setText(s.value("company/taxno",""))
        self.ed_addr.setText(s.value("company/address",""))
        self.ed_phone.setText(s.value("company/phone",""))
        self.ed_prefix.setText(s.value("doc/prefix","SAT-"))
        self.sp_digits.setValue(int(s.value("doc/digits",6)))
        self.cmb_reset.setCurrentText(s.value("doc/reset","Sıfırlama yok"))
        self.cmb_curr.setCurrentText(s.value("format/currency","TRY"))
        self.sp_dec.setValue(int(s.value("format/decimals",2)))
        self.cmb_theme.setCurrentText(s.value("ui/theme","dim"))

    def _save(self):
        s = self._settings()
        s.setValue("company/name", self.ed_company.text())
        s.setValue("company/taxno", self.ed_taxno.text())
        s.setValue("company/address", self.ed_addr.text())
        s.setValue("company/phone", self.ed_phone.text())
        s.setValue("doc/prefix", self.ed_prefix.text() or "SAT-")
        s.setValue("doc/digits", self.sp_digits.value())
        s.setValue("doc/reset", self.cmb_reset.currentText())
        s.setValue("format/currency", self.cmb_curr.currentText())
        s.setValue("format/decimals", self.sp_dec.value())
        s.setValue("ui/theme", self.cmb_theme.currentText())
        QMessageBox.information(self, "Kaydedildi", "Parametreler kaydedildi.\n(Temayı değiştirmek için uygulamayı yeniden başlatın.)")

    def _reset_defaults(self):
        self._settings().clear()
        self._load()
        QMessageBox.information(self, "Sıfırlandı", "Varsayılan değerlere dönüldü.")

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
            x, y = randint(0,w), randint(0,h)
            r = randint(1,2)
            p.setBrush(QColor(255,255,255, randint(70,160)))
            p.drawEllipse(x, y, r, r)
        p.end()
        self._sky.setPixmap(pm)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._sky.resize(self.size())
        self._paint_sky(self.width(), self.height())
