### app/dialogs.py ###

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QDoubleSpinBox, QSpinBox, QLabel, QFrame
)
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression, Qt, QLocale
from PyQt6.QtGui import QFont
from typing import Optional

TR = QLocale(QLocale.Language.Turkish, QLocale.Country.Turkey)

CATEGORIES = ["Bilezik", "Yüzük", "Kolye", "Külçe", "Gram"]
ISCILIK_TIPLERI = ["Milyem", "Gram", "TL"]

class NewStockDialog(QDialog):
    def __init__(self, parent=None, initial=None):
        super().__init__(parent)
        self.setWindowTitle("Stok Kaydı")
        self.setModal(True)
        self.setMinimumWidth(380)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(8)

        # Koyu kart gövde
        card = QFrame(self)
        card.setObjectName("Card")
        body = QVBoxLayout(card)
        body.setContentsMargins(16, 16, 16, 16)
        body.setSpacing(12)

        title = QLabel("Yeni Stok")
        title.setProperty("variant", "title")
        body.addWidget(title)

        # Form
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.in_kod = QLineEdit()
        self.in_kod.setPlaceholderText("Örn: STK0123")

        self.in_cat = QComboBox()
        self.in_cat.addItems(CATEGORIES)

        self.in_ad  = QLineEdit()
        self.in_ad.setPlaceholderText("Ürün adı")

        self.in_gram = QDoubleSpinBox()
        self.in_gram.setRange(0.01, 1_000_000.0)
        self.in_gram.setDecimals(2)
        self.in_gram.setSingleStep(0.10)

        self.in_adet = QSpinBox()
        self.in_adet.setRange(0, 1_000_000)

        self.in_alis_fiyat = QDoubleSpinBox()
        self.in_alis_fiyat.setRange(0.00, 1_000_000.00)
        self.in_alis_fiyat.setDecimals(2)
        self.in_alis_fiyat.setSingleStep(0.10)
        self.in_alis_fiyat.setSuffix(" ₺")

        self.in_satis_fiyat = QDoubleSpinBox()
        self.in_satis_fiyat.setRange(0.00, 1_000_000.00)
        self.in_satis_fiyat.setDecimals(2)
        self.in_satis_fiyat.setSingleStep(0.10)
        self.in_satis_fiyat.setSuffix(" ₺")

        self.in_kritik_stok = QSpinBox()
        self.in_kritik_stok.setRange(0, 1_000_000)
        self.in_kritik_stok.setValue(5)  # Varsayılan kritik seviye

        # === YENİ ALANLAR (DOS ekranındakiyle uyumlu) ===
        self.in_milyem = QDoubleSpinBox()
        self.in_milyem.setRange(0.00, 1000.00)
        self.in_milyem.setDecimals(2)
        self.in_milyem.setSingleStep(1.00)
        self.in_milyem.setValue(916.00)  # varsayılan: 22K ≈ 916

        self.in_ayar = QSpinBox()
        self.in_ayar.setRange(0, 24)
        self.in_ayar.setValue(22)

        self.in_isc_alinan = QDoubleSpinBox()
        self.in_isc_alinan.setRange(0.00, 1_000_000.00)
        self.in_isc_alinan.setDecimals(2)
        self.in_isc_alinan.setSingleStep(0.50)

        self.in_isc_verilen = QDoubleSpinBox()
        self.in_isc_verilen.setRange(0.00, 1_000_000.00)
        self.in_isc_verilen.setDecimals(2)
        self.in_isc_verilen.setSingleStep(0.50)

        self.in_isc_tip = QComboBox()
        self.in_isc_tip.addItems(ISCILIK_TIPLERI)

        self.in_kdv = QDoubleSpinBox()
        self.in_kdv.setRange(0.00, 100.00)
        self.in_kdv.setDecimals(2)
        self.in_kdv.setSingleStep(1.00)
        self.in_kdv.setSuffix(" %")
        self.in_kdv.setValue(20.00)

        form.addRow("Kod",   self.in_kod)
        form.addRow("Kategori", self.in_cat)
        form.addRow("Ad",    self.in_ad)
        form.addRow("Gram",  self.in_gram)
        form.addRow("Adet",  self.in_adet)
        form.addRow("Alış Fiyatı", self.in_alis_fiyat)
        form.addRow("Satış Fiyatı", self.in_satis_fiyat)
        form.addRow("Kritik Stok Seviyesi", self.in_kritik_stok)
        # --- yeni alanlar ---
        form.addRow("Milyem", self.in_milyem)
        form.addRow("Ayar", self.in_ayar)
        form.addRow("Alınan İşç.", self.in_isc_alinan)
        form.addRow("Verilen İşç.", self.in_isc_verilen)
        form.addRow("İşçilik Tipi", self.in_isc_tip)
        form.addRow("K.D.V.", self.in_kdv)
        body.addLayout(form)

        # Düzenleme modu
        if initial:
            self.in_kod.setText(initial.get("Kod",""))
            if initial.get("Kategori") in CATEGORIES:
                self.in_cat.setCurrentText(initial["Kategori"])
            self.in_ad.setText(initial.get("Ad",""))
            try:
                self.in_gram.setValue(float(initial.get("Gram", 0)))
            except Exception:
                pass
            self.in_adet.setValue(int(initial.get("Adet", 0)))
            try:
                self.in_alis_fiyat.setValue(float(initial.get("AlisFiyat", 0)))
            except Exception:
                pass
            try:
                self.in_satis_fiyat.setValue(float(initial.get("SatisFiyat", 0)))
            except Exception:
                pass
            self.in_kritik_stok.setValue(int(initial.get("KritikStok", 5)))
            # yeni alanlar için initial değerler
            self.in_milyem.setValue(float(initial.get("Milyem", 916)))
            self.in_ayar.setValue(int(initial.get("Ayar", 22)))
            self.in_isc_alinan.setValue(float(initial.get("IscAlinan", 0)))
            self.in_isc_verilen.setValue(float(initial.get("IscVerilen", 0)))
            if initial.get("IscTip") in ISCILIK_TIPLERI:
                self.in_isc_tip.setCurrentText(initial["IscTip"])
            self.in_kdv.setValue(float(initial.get("KDV", 20.0)))
            title.setText("Stok Düzenle")

        # Butonlar
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self._on_ok)
        self.buttons.rejected.connect(self.reject)
        body.addWidget(self.buttons)

        outer.addWidget(card)

        # Basit doğrulama: Kod + Ad zorunlu
        for w in (self.in_kod, self.in_ad):
            w.textChanged.connect(self._validate)
        self._validate()

    def _validate(self):
        ok = bool(self.in_kod.text().strip()) and bool(self.in_ad.text().strip())
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(ok)

    def _on_ok(self):
        if not self.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled():
            return
        self.accept()

    def data(self):
        return {
            "Kod": self.in_kod.text().strip(),
            "Kategori": self.in_cat.currentText(),
            "Ad": self.in_ad.text().strip(),
            "Gram": round(float(self.in_gram.value()), 2),
            "Adet": int(self.in_adet.value()),
            "AlisFiyat": round(float(self.in_alis_fiyat.value()), 2),
            "SatisFiyat": round(float(self.in_satis_fiyat.value()), 2),
            "KritikStok": int(self.in_kritik_stok.value()),
            # yeni alanlar
            "Milyem": round(float(self.in_milyem.value()), 2),
            "Ayar": int(self.in_ayar.value()),
            "IscAlinan": round(float(self.in_isc_alinan.value()), 2),
            "IscVerilen": round(float(self.in_isc_verilen.value()), 2),
            "IscTip": self.in_isc_tip.currentText(),
            "KDV": round(float(self.in_kdv.value()), 2),
        }

# --- Yeni: Müşteri diyalogu ---------------------------------------------------

class NewCustomerDialog(QDialog):
    def __init__(self, parent=None, initial: Optional[dict] = None):
        super().__init__(parent)

        # Normal dialog ayarları

        self.setWindowTitle("Müşteri Kaydı")
        self.setModal(True)
        self.setMinimumWidth(450)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)

        # Cam efektli kart
        card = QFrame(self)
        card.setObjectName("Glass")
        body = QVBoxLayout(card)
        body.setContentsMargins(20, 20, 20, 20)
        body.setSpacing(16)

        title = QLabel("Yeni Müşteri")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #E9EDF2; margin-bottom: 8px;")
        body.addWidget(title)

        # Form
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(12)

        self.in_kod = QLineEdit()
        self.in_kod.setPlaceholderText("Örn: CAR0123")
        self.in_kod.setStyleSheet("""
            QLineEdit {
                padding: 10px 12px;
                border-radius: 8px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                color: #E9EDF2;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4C7DFF;
                background: rgba(76,125,255,0.06);
            }
        """)

        self.in_ad = QLineEdit()
        self.in_ad.setPlaceholderText("Ad Soyad")
        self.in_ad.setStyleSheet("""
            QLineEdit {
                padding: 10px 12px;
                border-radius: 8px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                color: #E9EDF2;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4C7DFF;
                background: rgba(76,125,255,0.06);
            }
        """)

        self.in_tel = QLineEdit()
        self.in_tel.setPlaceholderText("05xx xxx xx xx")

        # Telefon numarası için daha esnek regex validator (sayılar ve boşluklar)
        phone_regex = QRegularExpression(r"^[0-9\s]{0,15}$")
        phone_validator = QRegularExpressionValidator(phone_regex)
        self.in_tel.setValidator(phone_validator)

        self.in_tel.setStyleSheet("""
            QLineEdit {
                padding: 10px 12px;
                border-radius: 8px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                color: #E9EDF2;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4C7DFF;
                background: rgba(76,125,255,0.06);
            }
        """)

        self.in_durum = QComboBox()
        self.in_durum.addItems(["Aktif", "Pasif"])
        self.in_durum.setStyleSheet("""
            QComboBox {
                padding: 10px 12px;
                border-radius: 8px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                color: #E9EDF2;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: rgba(28,34,44,0.98);
                color: #E9EDF2;
                border: 1px solid rgba(255,255,255,0.08);
                selection-background-color: #4C7DFF;
            }
        """)

        form.addRow("Kod", self.in_kod)
        form.addRow("Ad Soyad", self.in_ad)
        form.addRow("Telefon", self.in_tel)
        form.addRow("Durum", self.in_durum)
        body.addLayout(form)

        # Düzenleme modu
        if initial:
            self.in_kod.setText(initial.get("Kod", ""))
            self.in_ad.setText(initial.get("AdSoyad", ""))
            self.in_tel.setText(initial.get("Telefon", ""))
            if initial.get("Durum") in ["Aktif", "Pasif"]:
                self.in_durum.setCurrentText(initial["Durum"])
            title.setText("Müşteri Düzenle")

        # Butonlar
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self._on_ok)
        self.buttons.rejected.connect(self.reject)

        # Buton stilleri
        self.buttons.setStyleSheet("""
            QDialogButtonBox QPushButton {
                padding: 10px 20px;
                border-radius: 8px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                color: #E9EDF2;
                font-size: 14px;
                font-weight: 500;
                min-width: 80px;
            }
            QDialogButtonBox QPushButton:hover {
                border-color: #97B7FF;
                background: rgba(76,125,255,0.06);
                color: #F1F4F8;
            }
            QDialogButtonBox QPushButton:pressed {
                background: rgba(76,125,255,0.12);
            }
        """)

        body.addWidget(self.buttons)
        outer.addWidget(card)

        # Doğrulama
        for w in (self.in_kod, self.in_ad):
            w.textChanged.connect(self._validate)
        self._validate()

    def _validate(self):
        ok = bool(self.in_kod.text().strip()) and bool(self.in_ad.text().strip())
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(ok)

    def _on_ok(self):
        if not self.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled():
            return
        self.accept()

    def data(self):
        return {
            "Kod": self.in_kod.text().strip(),
            "AdSoyad": self.in_ad.text().strip(),
            "Telefon": self.in_tel.text().strip(),
            "Bakiye": 0.0,  # Başlangıçta borç yok
            "Son İşlem": "—",
            "Durum": self.in_durum.currentText(),
        }

# === Satır Ekle/Düzenle (Alış–Satış) =========================================
class NewSaleItemDialog(QDialog):
    def __init__(self, parent, products: list[dict], initial: dict|None = None):
        super().__init__(parent)
        self.setWindowTitle("Satır")
        self.setModal(True)
        self.setMinimumWidth(450)

        v = QVBoxLayout(self)
        v.setContentsMargins(16,16,16,16)
        v.setSpacing(10)

        # Cam efektli kart
        card = QFrame(self)
        card.setObjectName("Glass")
        body = QVBoxLayout(card)
        body.setContentsMargins(20, 20, 20, 20)
        body.setSpacing(16)

        title = QLabel("Yeni Satır")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: #E9EDF2; margin-bottom: 8px;")
        body.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(12)

        self.cmb_prod = QComboBox()
        for p in products:
            self.cmb_prod.addItem(f"{p['Kod']} — {p['Ad']}", p)
        self.cmb_prod.setStyleSheet("""
            QComboBox {
                padding: 10px 12px;
                border-radius: 8px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                color: #E9EDF2;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: rgba(28,34,44,0.98);
                color: #E9EDF2;
                border: 1px solid rgba(255,255,255,0.08);
                selection-background-color: #4C7DFF;
            }
        """)

        self.in_gram = QDoubleSpinBox()
        self.in_gram.setRange(0.00, 1_000_000)
        self.in_gram.setDecimals(2)
        self.in_gram.setStyleSheet("""
            QDoubleSpinBox {
                padding: 10px 12px;
                border-radius: 8px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                color: #E9EDF2;
                font-size: 14px;
            }
            QDoubleSpinBox:focus {
                border-color: #4C7DFF;
                background: rgba(76,125,255,0.06);
            }
        """)

        self.in_adet = QSpinBox()
        self.in_adet.setRange(1, 9999)
        self.in_adet.setValue(1)
        self.in_adet.setStyleSheet("""
            QSpinBox {
                padding: 10px 12px;
                border-radius: 8px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                color: #E9EDF2;
                font-size: 14px;
            }
            QSpinBox:focus {
                border-color: #4C7DFF;
                background: rgba(76,125,255,0.06);
            }
        """)

        self.in_price = QDoubleSpinBox()
        self.in_price.setRange(0.00, 1_000_000)
        self.in_price.setDecimals(2)
        self.in_price.setStyleSheet("""
            QDoubleSpinBox {
                padding: 10px 12px;
                border-radius: 8px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                color: #E9EDF2;
                font-size: 14px;
            }
            QDoubleSpinBox:focus {
                border-color: #4C7DFF;
                background: rgba(76,125,255,0.06);
            }
        """)

        self.in_note = QLineEdit()
        self.in_note.setStyleSheet("""
            QLineEdit {
                padding: 10px 12px;
                border-radius: 8px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                color: #E9EDF2;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #4C7DFF;
                background: rgba(76,125,255,0.06);
            }
        """)

        # >>> EK: Milyem & İşçilik alanları
        self.cmb_milyem = QComboBox()
        self.cmb_milyem.addItems(["995","916","900","875","835","750","585","375"])
        self.cmb_milyem.setStyleSheet("""
            QComboBox {
                padding: 10px 12px;
                border-radius: 8px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                color: #E9EDF2;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background: rgba(28,34,44,0.98);
                color: #E9EDF2;
                border: 1px solid rgba(255,255,255,0.08);
                selection-background-color: #4C7DFF;
            }
        """)

        self.sp_iscilik = QDoubleSpinBox()
        self.sp_iscilik.setRange(0, 1_000_000)
        self.sp_iscilik.setDecimals(2)
        self.sp_iscilik.setSuffix(" ₺")
        self.sp_iscilik.setStyleSheet("""
            QDoubleSpinBox {
                padding: 10px 12px;
                border-radius: 8px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                color: #E9EDF2;
                font-size: 14px;
            }
            QDoubleSpinBox:focus {
                border-color: #4C7DFF;
                background: rgba(76,125,255,0.06);
            }
        """)

        form.addRow("Ürün", self.cmb_prod)
        form.addRow("Gram", self.in_gram)
        form.addRow("Adet", self.in_adet)
        form.addRow("Birim Fiyat", self.in_price)
        form.addRow("Milyem", self.cmb_milyem)
        form.addRow("İşçilik", self.sp_iscilik)
        form.addRow("Not", self.in_note)
        body.addLayout(form)

        # Düzenleme modu
        if initial:
            title.setText("Satır Düzenle")
            # Initial değerler artık PREFILL bölümünde yükleniyor

        # --- PREFILL ---
        self._init_loading = False
        if initial:
            self._init_loading = True  # açılışta slotlar çalışmasın
            try:
                # 1) ürünü seç (signals kapalı)
                idx = -1
                code = initial.get("Kod", "")
                if code:
                    for i in range(self.cmb_prod.count()):
                        p = self.cmb_prod.itemData(i)
                        if p and p["Kod"] == code:
                            idx = i; break

                self.cmb_prod.blockSignals(True)
                if idx >= 0:
                    self.cmb_prod.setCurrentIndex(idx)
                self.cmb_prod.blockSignals(False)

                # 2) ÜRÜNÜN DEFAULTLARINI DEĞİL, INITIAL'İ YAZ
                self.in_gram.setValue(float(initial.get("Gram", self.in_gram.value())))
                self.in_adet.setValue(int(initial.get("Adet", self.in_adet.value())))
                # Birim fiyatı siz tabloda formülle hesaplıyorsunuz ama dialogda alan varsa:
                if "BirimFiyat" in initial:
                    self.in_price.setValue(float(initial["BirimFiyat"]))
                if initial.get("Milyem"):
                    self.cmb_milyem.setCurrentText(str(initial["Milyem"]))
                self.sp_iscilik.setValue(float(initial.get("Iscilik", 0.0)))
            finally:
                self._init_loading = False

        self.cmb_prod.currentIndexChanged.connect(self._fill_from_product)

        self.btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.btns.accepted.connect(self.accept)
        self.btns.rejected.connect(self.reject)

        # Buton stilleri
        self.btns.setStyleSheet("""
            QDialogButtonBox QPushButton {
                padding: 10px 20px;
                border-radius: 8px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                color: #E9EDF2;
                font-size: 14px;
                font-weight: 500;
                min-width: 80px;
            }
            QDialogButtonBox QPushButton:hover {
                border-color: #97B7FF;
                background: rgba(76,125,255,0.06);
                color: #F1F4F8;
            }
            QDialogButtonBox QPushButton:pressed {
                background: rgba(76,125,255,0.12);
            }
        """)

        body.addWidget(self.btns)
        v.addWidget(card)

    def _fill_from_product(self):
        # Açılışta veya prefill sırasında tetiklendiyse hiçbir şeyi ezme
        if getattr(self, "_init_loading", False):
            return
        # … burada ürün seçilince default gram/fiyat yazıyorsanız onlar kalsın …
        p = self.cmb_prod.currentData()
        if not p: return
        self.in_gram.setValue(float(p.get("Gram", 0.0)))
        self.in_price.setValue(float(p.get("SatisFiyat", p.get("Fiyat", 0.0))))

    def data(self) -> dict:
        p = self.cmb_prod.currentData() or {}
        return {
            "Kod": p.get("Kod",""),
            "Ad":  p.get("Ad",""),
            "Gram": float(self.in_gram.value()),
            "Adet": int(self.in_adet.value()),
            "BirimFiyat": float(self.in_price.value()),
            "Milyem": self.cmb_milyem.currentText(),
            "Iscilik": float(self.sp_iscilik.value()),
            "Not": self.in_note.text().strip(),
        }

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QDateEdit, QDoubleSpinBox, QComboBox, QPushButton, QLabel, QFrame,
    QFileDialog
)
from PyQt6.QtCore import Qt, QDate, QLocale, QSettings
from PyQt6.QtGui import QFont, QTextDocument
from PyQt6.QtPrintSupport import QPrinter


TR = QLocale(QLocale.Language.Turkish, QLocale.Country.Turkey)

class ExpenseVoucherDialog(QDialog):
    """
    DOS'taki Gider Pusulası alanlarının modern karşılığı:
    İşlem No, İşlem Tarihi, Cari No, Cari Adı, İşin Maliyeti, Cinsi,
    Adet, Birim Fiyat, Tutar (+ Not). PDF çıktısı üretir.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gider Pusulası")
        self.setModal(True)
        self.setMinimumWidth(820)

        # Tema (varsa uygula)
        try:
            from theme import apply_dialog_theme
            apply_dialog_theme(self)
        except Exception:
            pass

        root = QVBoxLayout(self); root.setContentsMargins(14,14,14,14); root.setSpacing(10)

        title = QLabel("Gider Pusulası")
        f = QFont("Segoe UI", 16); f.setWeight(QFont.Weight.DemiBold)
        title.setFont(f)
        root.addWidget(title)

        row = QHBoxLayout(); row.setSpacing(12); root.addLayout(row)

        # Sol kart: belge + cari
        left = QFrame(objectName="Card"); left.setContentsMargins(12,12,12,12)
        lf = QFormLayout(left); lf.setSpacing(8)

        self.ed_doc  = QLineEdit(self._suggest_docno())      # İşlem No
        self.ed_date = QDateEdit(calendarPopup=True)         # İşlem Tarihi
        self.ed_date.setDate(QDate.currentDate())
        self.ed_cari_no  = QLineEdit()                       # Cari No
        self.ed_cari_adi = QLineEdit()                       # Cari Adı

        lf.addRow("İşlem No", self.ed_doc)
        lf.addRow("İşlem Tarihi", self.ed_date)
        lf.addRow("Cari No", self.ed_cari_no)
        lf.addRow("Cari Adı", self.ed_cari_adi)

        row.addWidget(left, 1)

        # Sağ kart: mahiyet + kalem
        right = QFrame(objectName="Card"); right.setContentsMargins(12,12,12,12)
        rf = QFormLayout(right); rf.setSpacing(8)

        self.ed_mahi = QLineEdit()                           # İşin Mahiyeti
        self.cmb_cins = QComboBox(); self.cmb_cins.setEditable(True)
        self.cmb_cins.addItems(["", "Bilezik 22K", "Külçe 24K", "Çeyrek", "Gümüş", "Aksesuar"])

        self.sp_adet = QDoubleSpinBox(); self.sp_adet.setRange(0, 1_000_000); self.sp_adet.setDecimals(3)
        self.sp_birim = QDoubleSpinBox(); self.sp_birim.setRange(0, 1_000_000); self.sp_birim.setDecimals(2); self.sp_birim.setSuffix(" ₺")
        self.ed_tutar = QLineEdit(); self.ed_tutar.setReadOnly(True)          # Tutar = adet*birim (otomatik)

        rf.addRow("İşin Mahiyeti", self.ed_mahi)
        rf.addRow("Cinsi", self.cmb_cins)
        rf.addRow("Adet", self.sp_adet)
        rf.addRow("Birim Fiyat", self.sp_birim)
        rf.addRow("Tutar", self.ed_tutar)

        row.addWidget(right, 1)

        # Not + butonlar
        bottom = QHBoxLayout(); bottom.setSpacing(12); root.addLayout(bottom)

        note_card = QFrame(objectName="Card"); note_card.setContentsMargins(12,12,12,12)
        self.ed_note = QTextEdit(); self.ed_note.setPlaceholderText("Not...")
        nv = QVBoxLayout(note_card); nv.setContentsMargins(0,0,0,0); nv.addWidget(self.ed_note)
        bottom.addWidget(note_card, 1)

        btns = QFrame(objectName="Card"); btns.setContentsMargins(12,12,12,12)
        bl = QVBoxLayout(btns); bl.setSpacing(8)
        self.btn_pdf = QPushButton("PDF Yazdır")
        self.btn_ok  = QPushButton("Kaydet ve Kapat")
        self.btn_cancel = QPushButton("Vazgeç")
        bl.addWidget(self.btn_pdf); bl.addWidget(self.btn_ok); bl.addWidget(self.btn_cancel)
        bottom.addWidget(btns)

        # Hesaplamalar
        self.sp_adet.valueChanged.connect(self._recalc)
        self.sp_birim.valueChanged.connect(self._recalc)
        self._recalc()

        # Sinyaller
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok.clicked.connect(self._accept_and_inc_seq)
        self.btn_pdf.clicked.connect(self._export_pdf)

    # --- yardımcılar ---
    def _settings(self) -> QSettings:
        return QSettings("OrbitX","KuyumcuERP")

    def _suggest_docno(self) -> str:
        s = self._settings()
        yyyymm = QDate.currentDate().toString("yyMM")
        n = int(s.value(f"expense/seq/{yyyymm}", 0))
        return f"GDR-{yyyymm}-{n+1:04d}"

    def _inc_seq(self):
        s = self._settings()
        yyyymm = QDate.currentDate().toString("yyMM")
        n = int(s.value(f"expense/seq/{yyyymm}", 0)) + 1
        s.setValue(f"expense/seq/{yyyymm}", n)

    def _recalc(self):
        tutar = float(self.sp_adet.value()) * float(self.sp_birim.value())
        self.ed_tutar.setText(TR.toString(tutar, 'f', 2))

    def _accept_and_inc_seq(self):
        self._inc_seq()
        self.accept()

    # --- PDF ---
    def _export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "PDF olarak kaydet", "gider_pusulasi.pdf", "PDF (*.pdf)")
        if not path: return

        s = self._settings()
        company = s.value("company/name", "Şirket Adı")
        addr    = s.value("company/address","")
        phone   = s.value("company/phone","")
        taxno   = s.value("company/taxno","")

        html = f"""
        <style>
            body {{ font-family: -apple-system, Segoe UI, Roboto, Arial; font-size: 11pt; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border:1px solid #999; padding:6px; text-align:left; }}
            .r {{ text-align:right; }}
        </style>

        <h2 style="margin:0 0 6px 0;">{company}</h2>
        <div style="margin-bottom:10px;">{addr} &nbsp;&nbsp; {phone} &nbsp;&nbsp; VKN/TCKN: {taxno}</div>

        <h3 style="margin:12px 0 6px 0;">Gider Pusulası</h3>
        <table>
            <tr><td><b>İşlem No</b></td><td>{self.ed_doc.text()}</td>
                <td><b>İşlem Tarihi</b></td><td>{self.ed_date.date().toString('dd.MM.yyyy')}</td></tr>
            <tr><td><b>Cari No</b></td><td>{self.ed_cari_no.text()}</td>
                <td><b>Cari Adı</b></td><td>{self.ed_cari_adi.text()}</td></tr>
            <tr><td><b>İşin Mahiyeti</b></td><td>{self.ed_mahi.text()}</td>
                <td><b>Cinsi</b></td><td>{self.cmb_cins.currentText()}</td></tr>
        </table>

        <table style="margin-top:8px;">
            <thead><tr><th>Adet</th><th>Birim Fiyat</th><th class="r">Tutar</th></tr></thead>
            <tbody>
                <tr>
                    <td>{TR.toString(self.sp_adet.value(),'f',3)}</td>
                    <td>{TR.toString(self.sp_birim.value(),'f',2)}</td>
                    <td class="r"><b>{self.ed_tutar.text()}</b></td>
                </tr>
            </tbody>
        </table>

        <div style="margin-top:12px;"><b>Not:</b> {self.ed_note.toPlainText()}</div>
        """

        doc = QTextDocument(); doc.setHtml(html)
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(path)
        doc.print(printer)

    def data(self) -> dict:
        return {
            "doc_no": self.ed_doc.text(),
            "date": self.ed_date.date().toString("dd.MM.yyyy"),
            "cari_no": self.ed_cari_no.text().strip(),
            "cari_ad": self.ed_cari_adi.text().strip(),
            "mahi": self.ed_mahi.text().strip(),
            "cins": self.cmb_cins.currentText().strip(),
            "adet": float(self.sp_adet.value()),
            "birim": float(self.sp_birim.value()),
            "tutar": float(self.sp_adet.value() * self.sp_birim.value()),
            "note": self.ed_note.toPlainText().strip(),
        }