### app/pages/stock.py ###
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QFrame,
    QAbstractItemView, QHeaderView, QDialog, QMessageBox   # <— QDialog ve QMessageBox eklendi
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QLinearGradient
from random import randint, uniform
from theme import elevate
from dialogs import NewStockDialog  # dialog

CATEGORIES = ["Tümü", "Bilezik", "Yüzük", "Kolye", "Külçe", "Gram"]


def generate_rows(n=60):
    rows = []
    cats = CATEGORIES[1:]
    for i in range(n):
        alis_fiyat = round(uniform(100, 5000), 2)
        satis_fiyat = round(alis_fiyat * uniform(1.1, 1.5), 2)  # %10-50 kar marjı
        rows.append({
            "Kod": f"STK{i+1:04}",
            "Kategori": cats[i % len(cats)],
            "Ad": f"Ürün {i+1}",
            "Gram": round(uniform(0.5, 50.0), 2),
            "Adet": randint(1, 25),
            "AlisFiyat": alis_fiyat,
            "SatisFiyat": satis_fiyat,
            "KritikStok": randint(2, 10),
        })
    return rows


class StockPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_rows = generate_rows(80)

        # === KOZMİK ARKA PLAN ===
        self._sky = QLabel(self)
        self._sky.lower()  # en arkada dursun
        self._sky.setScaledContents(True)
        self._sky.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

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
        card.setObjectName("Glass")  # Cam efektli kart
        elevate(card, scheme="dim", blur=32, y=10)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(10)

        # === KOZMİK TABLO ===
        self.table = QTableWidget(0, 8, self)
        self.table.setHorizontalHeaderLabels(["Kod", "Kategori", "Ürün Adı", "Gram", "Adet", "Alış Fiyat", "Satış Fiyat", "Toplam Değer"])
        self.table.verticalHeader().setVisible(False)
        self.table.setCornerButtonEnabled(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                background: rgba(10,16,32,0.3);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 12px;
                gridline-color: rgba(255,255,255,0.08);
            }
            QTableWidget::item {
                padding: 10px 8px;
                border-bottom: 1px solid rgba(255,255,255,0.04);
                background: transparent;
            }
            QTableWidget::item:selected {
                background: rgba(76,125,255,0.12);
                border-left: 3px solid #4C7DFF;
            }
            QTableWidget::item:hover {
                background: rgba(76,125,255,0.04);
            }
        """)

        pal = self.table.palette()
        pal.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0, 0))
        pal.setColor(QPalette.ColorRole.AlternateBase, QColor(255, 255, 255, 6))
        pal.setColor(QPalette.ColorRole.Text, QColor(241, 244, 248))
        pal.setColor(QPalette.ColorRole.Highlight, QColor(76, 125, 255, 120))
        pal.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.table.setPalette(pal)

        # Alternatif satır renklerini devre dışı bırakıp kendi stillerimizi kullan
        self.table.setAlternatingRowColors(False)

        self.header = self.table.horizontalHeader()
        self.header.setDefaultAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.header.setStretchLastSection(False)
        self.header.setMinimumSectionSize(60)
        self.header.setStyleSheet("""
            QHeaderView::section {
                background: rgba(20,26,48,0.9);
                border: 1px solid rgba(255,255,255,0.1);
                border-bottom: 2px solid rgba(76,125,255,0.4);
                border-right: 1px solid rgba(255,255,255,0.05);
                padding: 14px 12px;
                font-weight: 600;
                font-size: 13px;
                color: #E9EDF2;
                letter-spacing: 0.5px;
                text-align: center;
            }
            QHeaderView::section:hover {
                background: rgba(30,36,58,0.95);
                border-bottom-color: rgba(76,125,255,0.6);
                color: #F1F4F8;
            }
            QHeaderView::section:first {
                border-left: 1px solid rgba(255,255,255,0.1);
            }
            QHeaderView::section:last {
                border-right: 1px solid rgba(255,255,255,0.1);
            }
        """)
        self._apply_column_layout()

        card_layout.addWidget(self.table)

        # === KOZMİK ÖZET BAR ===
        summary_frame = QFrame()
        summary_frame.setObjectName("Glass")
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(16, 12, 16, 12)

        self.summary = QLabel("")
        self.summary.setProperty("variant", "muted")
        self.summary.setStyleSheet("""
            QLabel {
                color: #B7C0CC;
                font-size: 12px;
                font-weight: 500;
            }
        """)
        summary_layout.addWidget(self.summary)
        card_layout.addWidget(summary_frame)

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

        # İlk render sonrası arka planı çiz
        self.resizeEvent(None)

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
        for _ in range(int((w * h) / 15000)):  # yoğunluk
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

    # --- kolon düzeni
    def _apply_column_layout(self):
        self.header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed);   self.table.setColumnWidth(0, 100)
        self.header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed);   self.table.setColumnWidth(1, 130)
        self.header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Ürün adı esner
        self.header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed);   self.table.setColumnWidth(3, 90)
        self.header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed);   self.table.setColumnWidth(4, 80)
        self.header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed);   self.table.setColumnWidth(5, 120)
        self.header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed);   self.table.setColumnWidth(6, 120)
        self.header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed);   self.table.setColumnWidth(7, 120)

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
            "AlisFiyat": float(self.table.item(row, 5).text().replace(" ₺", "").replace(",", ".")),
            "SatisFiyat": float(self.table.item(row, 6).text().replace(" ₺", "").replace(",", ".")),
            "KritikStok": int(self.table.item(row, 4).text()),  # Kritik stok adet sütunundan alınacak
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
                    QMessageBox.information(self, "Başarılı", "Stok kaydı başarıyla güncellendi.")
                    break
            else:
                self._all_rows.insert(0, data)
                QMessageBox.information(self, "Başarılı", "Stok kaydı başarıyla eklendi.")
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
            QMessageBox.information(self, "Başarılı", "Stok kaydı başarıyla güncellendi.")

    # --- Sil
    def on_delete(self):
        row = self._selected_row_index()
        if row is None:
            return
        current = self._row_to_dict(row)
        reply = QMessageBox.question(self, "Onay",
                                     f"{current['Ad']} ürününü silmek istediğinizden emin misiniz?")
        if reply == QMessageBox.StandardButton.Yes:
            kod = self.table.item(row, 0).text()
            self._all_rows = [r for r in self._all_rows if r["Kod"] != kod]
            self.apply_filters()
            QMessageBox.information(self, "Başarılı", "Stok kaydı başarıyla silindi.")

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

            # Kritik stok kontrolü - adet kritik seviyenin altında ise kırmızı arka plan
            if r["Adet"] <= r.get("KritikStok", 5):
                adet_item.setBackground(QColor(244, 67, 54, 60))  # Kırmızı arka plan
                adet_item.setForeground(QColor(255, 255, 255))  # Beyaz yazı
            self.table.setItem(i, 4, adet_item)

            # Alış fiyatı
            alis_item = QTableWidgetItem(f"{r.get('AlisFiyat', 0):.2f} ₺")
            alis_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 5, alis_item)

            # Satış fiyatı
            satis_item = QTableWidgetItem(f"{r.get('SatisFiyat', 0):.2f} ₺")
            satis_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(i, 6, satis_item)

            # Toplam değer hesaplaması (Adet × Satış Fiyatı)
            toplam_deger = r["Adet"] * r.get('SatisFiyat', 0)
            deger_item = QTableWidgetItem(f"{toplam_deger:.2f} ₺")
            deger_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if r["Adet"] <= r.get("KritikStok", 5):
                deger_item.setBackground(QColor(244, 67, 54, 60))  # Kritik stok ise kırmızı
                deger_item.setForeground(QColor(255, 255, 255))
            self.table.setItem(i, 7, deger_item)

    def update_summary(self, rows):
        toplam_gram = sum(r["Gram"] for r in rows)
        toplam_adet = sum(r["Adet"] for r in rows)
        toplam_deger = sum(r["Adet"] * r.get('SatisFiyat', 0) for r in rows)
        toplam_alis_deger = sum(r["Adet"] * r.get('AlisFiyat', 0) for r in rows)
        kar_potential = toplam_deger - toplam_alis_deger
        kritik_stok_sayisi = sum(1 for r in rows if r["Adet"] <= r.get("KritikStok", 5))

        self.summary.setText(
            f"Toplam kayıt: {len(rows)} • Toplam Gram: {toplam_gram:.2f} • Toplam Adet: {toplam_adet} • "
            f"Stok Değeri: {toplam_deger:.2f} ₺ • Potansiyel Kâr: {kar_potential:.2f} ₺ • "
            f"Kritik Stok: {kritik_stok_sayisi} ürün"
        )
