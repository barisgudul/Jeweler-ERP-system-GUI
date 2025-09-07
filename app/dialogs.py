### app/dialogs.py ###

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QDoubleSpinBox, QSpinBox, QLabel, QFrame
)
from PyQt6.QtCore import Qt

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

        form.addRow("Kod",   self.in_kod)
        form.addRow("Kategori", self.in_cat)
        form.addRow("Ad",    self.in_ad)
        form.addRow("Gram",  self.in_gram)
        form.addRow("Adet",  self.in_adet)
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
        }
