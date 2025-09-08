### app/dialogs.py ###

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QDoubleSpinBox, QSpinBox, QLabel, QFrame
)
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Optional

CATEGORIES = ["Bilezik", "Yüzük", "Kolye", "Külçe", "Gram"]

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

        form.addRow("Kod",   self.in_kod)
        form.addRow("Kategori", self.in_cat)
        form.addRow("Ad",    self.in_ad)
        form.addRow("Gram",  self.in_gram)
        form.addRow("Adet",  self.in_adet)
        form.addRow("Alış Fiyatı", self.in_alis_fiyat)
        form.addRow("Satış Fiyatı", self.in_satis_fiyat)
        form.addRow("Kritik Stok Seviyesi", self.in_kritik_stok)
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

        # Telefon numarası için regex validator
        phone_regex = QRegularExpression(r"^05\d{2} \d{3} \d{2} \d{2}$")
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

        form.addRow("Ürün", self.cmb_prod)
        form.addRow("Gram", self.in_gram)
        form.addRow("Adet", self.in_adet)
        form.addRow("Birim Fiyat", self.in_price)
        form.addRow("Not", self.in_note)
        body.addLayout(form)

        # Düzenleme modu
        if initial:
            # ürün koduna göre seçim yap
            idx = 0
            for i in range(self.cmb_prod.count()):
                p = self.cmb_prod.itemData(i)
                if p and p["Kod"] == initial.get("Kod"):
                    idx = i; break
            self.cmb_prod.setCurrentIndex(idx)
            self.in_gram.setValue(float(initial.get("Gram", 0.0)))
            self.in_adet.setValue(int(initial.get("Adet", 1)))
            self.in_price.setValue(float(initial.get("BirimFiyat", 0.0)))
            self.in_note.setText(initial.get("Not",""))
            title.setText("Satır Düzenle")

        self.cmb_prod.currentIndexChanged.connect(self._fill_from_product)
        self._fill_from_product()

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
        p = self.cmb_prod.currentData()
        if not p: return
        self.in_gram.setValue(float(p.get("Gram", 0.0)))
        self.in_price.setValue(float(p.get("Fiyat", 0.0)))

    def data(self) -> dict:
        p = self.cmb_prod.currentData() or {}
        return {
            "Kod": p.get("Kod",""),
            "Ad":  p.get("Ad",""),
            "Gram": float(self.in_gram.value()),
            "Adet": int(self.in_adet.value()),
            "BirimFiyat": float(self.in_price.value()),
            "Not": self.in_note.text().strip(),
        }
