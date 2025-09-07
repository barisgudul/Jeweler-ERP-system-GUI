### app/pages/stock.py ###
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QAbstractItemView, QHeaderView, QDialog   # <— QDialog eklendi
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
from random import randint, uniform
from theme import elevate
from dialogs import NewStockDialog  # dialog

CATEGORIES = ["Tümü", "Bilezik", "Yüzük", "Kolye", "Külçe", "Gram"]


def generate_rows(n=60):
    rows = []
    cats = CATEGORIES[1:]
    for i in range(n):
        rows.append({
            "Kod": f"STK{i+1:04}",
            "Kategori": cats[i % len(cats)],
            "Ad": f"Ürün {i+1}",
            "Gram": round(uniform(0.5, 50.0), 2),
            "Adet": randint(1, 25),
        })
    return rows


class StockPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_rows = generate_rows(80)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        # Başlık
        header = QHBoxLayout()
        title = QLabel("Stok Yönetimi")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.addWidget(title, 0, Qt.AlignmentFlag.AlignLeft)

        hint = QLabel("Arama, kategori filtresi ve özet • mock veri")
        hint.setProperty("variant", "muted")
        header.addWidget(hint, 0, Qt.AlignmentFlag.AlignRight)
        root.addLayout(header)

        # Toolbar
        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Ara: kod, ad…")
        self.search.textChanged.connect(self.apply_filters)

        self.filter = QComboBox()
        self.filter.addItems(CATEGORIES)
        self.filter.currentIndexChanged.connect(self.apply_filters)

        # Açılır liste paleti (koyu)
        view_palette = self.filter.view().palette()
        view_palette.setColor(QPalette.ColorRole.Base, QColor(28, 34, 44))
        view_palette.setColor(QPalette.ColorRole.Text, QColor(241, 244, 248))
        view_palette.setColor(QPalette.ColorRole.Highlight, QColor(76, 125, 255))
        view_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.filter.view().setPalette(view_palette)

        self.btn_new = QPushButton("Yeni Stok")
        self.btn_edit = QPushButton("Düzenle")
        self.btn_del = QPushButton("Sil")
        self.btn_edit.setEnabled(False)
        self.btn_del.setEnabled(False)

        toolbar.addWidget(self.search, 2)
        toolbar.addWidget(self.filter, 1)
        toolbar.addStretch(1)
        toolbar.addWidget(self.btn_new)
        toolbar.addWidget(self.btn_edit)
        toolbar.addWidget(self.btn_del)
        root.addLayout(toolbar)

        # Kart
        card = QFrame()
        card.setObjectName("Card")
        elevate(card, scheme="dim", blur=28, y=8)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(10)

        # Tablo
        self.table = QTableWidget(0, 5, self)
        self.table.setHorizontalHeaderLabels(["Kod", "Kategori", "Ad", "Gram", "Adet"])
        self.table.verticalHeader().setVisible(False)
        self.table.setCornerButtonEnabled(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        pal = self.table.palette()
        pal.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0, 0))
        pal.setColor(QPalette.ColorRole.AlternateBase, QColor(255, 255, 255, 10))
        self.table.setPalette(pal)

        self.header = self.table.horizontalHeader()
        self.header.setDefaultAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.header.setStretchLastSection(False)
        self.header.setMinimumSectionSize(50)
        self._apply_column_layout()

        card_layout.addWidget(self.table)

        # Özet bar
        self.summary = QLabel("")
        self.summary.setProperty("variant", "muted")
        card_layout.addWidget(self.summary)

        root.addWidget(card)

        # Veri yükle
        self.apply_filters()

        # render sonrası sütun düzenini tekrar sabitle
        QTimer.singleShot(0, self._apply_column_layout)

        # olaylar
        self.btn_new.clicked.connect(self.on_new)
        self.btn_del.clicked.connect(self.on_delete)
        self.btn_edit.clicked.connect(self.on_edit)
        self.table.selectionModel().selectionChanged.connect(self._toggle_row_actions)

    # --- kolon düzeni
    def _apply_column_layout(self):
        self.header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed);   self.table.setColumnWidth(0, 90)
        self.header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed);   self.table.setColumnWidth(1, 110)
        self.header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Ad esner
        self.header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed);   self.table.setColumnWidth(3, 80)
        self.header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed);   self.table.setColumnWidth(4, 70)

    # --- satır seçim durumuna göre butonlar
    def _toggle_row_actions(self):
        has = len(self.table.selectedItems()) > 0
        self.btn_edit.setEnabled(has)
        self.btn_del.setEnabled(has)

    # --- yardımcı: seçili kaydı oku
    def _selected_row_index(self):
        idxs = self.table.selectionModel().selectedRows()
        return idxs[0].row() if idxs else None

    def _row_to_dict(self, row):
        return {
            "Kod": self.table.item(row, 0).text(),
            "Kategori": self.table.item(row, 1).text(),
            "Ad": self.table.item(row, 2).text(),
            "Gram": float(self.table.item(row, 3).text().replace(",", ".")),
            "Adet": int(self.table.item(row, 4).text()),
        }

    # --- Yeni
    def on_new(self):
        dlg = NewStockDialog(self)
        # PyQt6: exec() -> QDialog.DialogCode
        if dlg.exec() == QDialog.DialogCode.Accepted:   # <— düzeltme
            data = dlg.data()
            # aynı kod varsa güncelle, yoksa ekle
            for r in self._all_rows:
                if r["Kod"] == data["Kod"]:
                    r.update(data)
                    break
            else:
                self._all_rows.insert(0, data)
            self.apply_filters()

    # --- Düzenle
    def on_edit(self):
        row = self._selected_row_index()
        if row is None:
            return
        current = self._row_to_dict(row)
        dlg = NewStockDialog(self, initial=current)
        if dlg.exec() == QDialog.DialogCode.Accepted:   # <— düzeltme
            data = dlg.data()
            for r in self._all_rows:
                if r["Kod"] == current["Kod"]:
                    r.update(data)
                    break
            self.apply_filters()

    # --- Sil
    def on_delete(self):
        row = self._selected_row_index()
        if row is None:
            return
        kod = self.table.item(row, 0).text()
        self._all_rows = [r for r in self._all_rows if r["Kod"] != kod]
        self.apply_filters()

    # --- filtreleme & tablo doldurma
    def apply_filters(self):
        text = (self.search.text() or "").strip().lower()
        cat = self.filter.currentText()

        filtered = []
        for r in self._all_rows:
            if cat != "Tümü" and r["Kategori"] != cat:
                continue
            if text and (text not in r["Kod"].lower() and text not in r["Ad"].lower()):
                continue
            filtered.append(r)

        self.populate_table(filtered)
        self.update_summary(filtered)
        self._toggle_row_actions()

    def populate_table(self, rows):
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(r["Kod"]))
            self.table.setItem(i, 1, QTableWidgetItem(r["Kategori"]))
            self.table.setItem(i, 2, QTableWidgetItem(r["Ad"]))

            gram_item = QTableWidgetItem(f"{r['Gram']:.2f}")
            gram_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 3, gram_item)

            adet_item = QTableWidgetItem(str(r["Adet"]))
            adet_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 4, adet_item)

    def update_summary(self, rows):
        toplam_gram = sum(r["Gram"] for r in rows)
        toplam_adet = sum(r["Adet"] for r in rows)
        self.summary.setText(
            f"Toplam kayıt: {len(rows)} • Toplam Gram: {toplam_gram:.2f} • Toplam Adet: {toplam_adet}"
        )
