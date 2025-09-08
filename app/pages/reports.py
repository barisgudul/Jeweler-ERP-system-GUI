# app/pages/reports.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QSplitter, QFormLayout,
    QDateEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QFileDialog, QMessageBox, QSizePolicy, QSpacerItem,
    QAbstractItemView
)
from PyQt6.QtCore import Qt, QDate, QLocale, QTimer
from PyQt6.QtGui import QFont, QTextDocument, QPixmap, QPainter, QLinearGradient, QColor, QPalette
from PyQt6.QtPrintSupport import QPrinter
from random import randint
from theme import elevate

TR = QLocale(QLocale.Language.Turkish, QLocale.Country.Turkey)

class ReportsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # === KOZMİK ARKA PLAN ===
        self._sky = QLabel(self)
        self._sky.lower()  # en arkada dursun
        self._sky.setScaledContents(True)
        self._sky.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(16)

        # — başlık
        header = QHBoxLayout()
        title = QLabel("Alım / Satım Raporları")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #E9EDF2; font-weight: 700;")
        header.addWidget(title, 0, Qt.AlignmentFlag.AlignLeft)

        hint = QLabel("Tarih, tür, cari ve kategoriye göre filtreleyin; CSV/PDF alın.")
        hint.setProperty("variant", "muted")
        hint.setStyleSheet("font-size: 12px;")
        header.addWidget(hint, 0, Qt.AlignmentFlag.AlignRight)
        root.addLayout(header)

        split = QSplitter(Qt.Orientation.Horizontal)
        split.setChildrenCollapsible(False)
        root.addWidget(split, 1)

        # Sol: Filtre paneli
        filter_card = QFrame(objectName="Glass")
        elevate(filter_card, "dim", blur=20, y=6)
        filter_card.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        filter_card.setFixedWidth(320)

        form = QFormLayout(filter_card)
        form.setContentsMargins(14, 14, 14, 14)
        form.setSpacing(10)

        # Tarih widget'ları için özel stil
        date_input_css = """
            padding: 8px 10px;
            border-radius: 8px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.12);
            color: #E9EDF2;
            font-size: 12px;
        """

        self.dt_start = QDateEdit(calendarPopup=True)
        self.dt_start.setDate(QDate.currentDate().addMonths(-1))
        self.dt_start.setStyleSheet(f"QDateEdit{{{date_input_css}}}"
                                   "QDateEdit::drop-down{border:none;width:16px;}")

        self.dt_end = QDateEdit(calendarPopup=True)
        self.dt_end.setDate(QDate.currentDate())
        self.dt_end.setStyleSheet(f"QDateEdit{{{date_input_css}}}"
                                 "QDateEdit::drop-down{border:none;width:16px;}")

        self.cmb_type = QComboBox(); self.cmb_type.addItems(["Hepsi","Alım","Satım"])
        self.cmb_cari = QComboBox(); self.cmb_cari.setEditable(True); self.cmb_cari.setPlaceholderText("Cari ara…")
        self.cmb_cat  = QComboBox(); self.cmb_cat.addItems(["Tümü","Altın Takı","Külçe","Gümüş","Aksesuar"])

        form.addRow("Başlangıç", self.dt_start)
        form.addRow("Bitiş", self.dt_end)
        form.addRow("Tür", self.cmb_type)
        form.addRow("Cari", self.cmb_cari)
        form.addRow("Kategori", self.cmb_cat)

        btn_row = QHBoxLayout()
        self.btn_apply = QPushButton("Uygula");  self.btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear = QPushButton("Temizle"); self.btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_row.addWidget(self.btn_apply); btn_row.addWidget(self.btn_clear)
        form.addRow(btn_row)

        form.addItem(QSpacerItem(1, 1, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        split.addWidget(filter_card)

        # Sağ: Araç çubuğu + tablo
        right_card = QFrame(objectName="Glass")
        elevate(right_card, "dim", blur=24, y=6)
        r = QVBoxLayout(right_card); r.setContentsMargins(16, 12, 16, 12); r.setSpacing(8)

        toolbar = QHBoxLayout()
        self.lbl_summary = QLabel(""); self.lbl_summary.setProperty("variant","muted")
        toolbar.addWidget(self.lbl_summary, 0, Qt.AlignmentFlag.AlignLeft)
        toolbar.addStretch(1)
        self.btn_export_csv = QPushButton("Excel (CSV)")
        self.btn_export_pdf = QPushButton("PDF")
        self.btn_export_csv.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_export_pdf.setCursor(Qt.CursorShape.PointingHandCursor)
        toolbar.addWidget(self.btn_export_csv); toolbar.addWidget(self.btn_export_pdf)
        r.addLayout(toolbar)

        # === KOZMİK TABLO ===
        self.table = QTableWidget(0, 10, self)
        self.table.setHorizontalHeaderLabels(["Tarih","Tür","Belge No","Cari","Ürün","Miktar/Gr","Birim Fiyat","Tutar","Kasa","Not"])
        self.table.verticalHeader().setVisible(False)
        self.table.setCornerButtonEnabled(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Kozmik tablo stilleri
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

        # Palette ayarları
        pal = self.table.palette()
        pal.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0, 0))
        pal.setColor(QPalette.ColorRole.AlternateBase, QColor(255, 255, 255, 6))
        pal.setColor(QPalette.ColorRole.Text, QColor(241, 244, 248))
        pal.setColor(QPalette.ColorRole.Highlight, QColor(76, 125, 255, 120))
        pal.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.table.setPalette(pal)

        # Alternatif satır renklerini devre dışı bırakıp kendi stillerimizi kullan
        self.table.setAlternatingRowColors(False)

        # Header stilleri
        self.header = self.table.horizontalHeader()
        self.header.setDefaultAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        self.header.setStretchLastSection(False)
        self.header.setMinimumSectionSize(80)
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

        r.addWidget(self.table, 1)

        split.addWidget(right_card)
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)

        # Sinyaller
        self.btn_apply.clicked.connect(self.apply_filters)
        self.btn_clear.clicked.connect(self.clear_filters)
        self.btn_export_csv.clicked.connect(self.export_csv)
        self.btn_export_pdf.clicked.connect(self.export_pdf)

        # Demo veri + cari listesi
        self._seed_demo()
        self._fill_cari_list()
        self.apply_filters()

        # render sonrası kolon düzenini tekrar sabitle
        QTimer.singleShot(0, self._apply_column_layout)

        # İlk render sonrası arka planı çiz
        self.resizeEvent(None)

    # --- kolon düzeni
    def _apply_column_layout(self):
        self.header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed); self.table.setColumnWidth(0, 100)  # Tarih
        self.header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed); self.table.setColumnWidth(1, 80)   # Tür
        self.header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed); self.table.setColumnWidth(2, 120)  # Belge No
        self.header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed); self.table.setColumnWidth(3, 140)  # Cari
        self.header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Ürün adı esner
        self.header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed); self.table.setColumnWidth(5, 100)  # Miktar/Gr
        self.header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed); self.table.setColumnWidth(6, 120)  # Birim Fiyat
        self.header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed); self.table.setColumnWidth(7, 120)  # Tutar
        self.header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed); self.table.setColumnWidth(8, 90)   # Kasa
        self.header.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed); self.table.setColumnWidth(9, 150)  # Not

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

    # --- Demo veri ---
    def _seed_demo(self):
        self._data = [
            {"dt":"2025-08-15","typ":"Satım","doc":"SAT-000123","cari":"Ahmet Yılmaz","product":"Bilezik 22K","qty":7.90,"unit":32000.00,"amount":252800.00,"cash":"Nakit","note":"","cat":"Altın Takı"},
            {"dt":"2025-08-13","typ":"Alım","doc":"ALM-000077","cari":"XYZ Altın","product":"Külçe 24K","qty":50.00,"unit":2400.00,"amount":120000.00,"cash":"Banka","note":"Vade 7g","cat":"Külçe"},
        ]

    def _fill_cari_list(self):
        seen = sorted({row["cari"] for row in self._data})
        self.cmb_cari.clear(); self.cmb_cari.addItems(seen)
        self.cmb_cari.setCurrentIndex(-1); self.cmb_cari.setEditText("")

    # --- Filtreleme ---
    def _current_filters(self):
        start = self.dt_start.date().toPyDate()
        end   = self.dt_end.date().toPyDate()
        typ   = self.cmb_type.currentText()
        cari  = self.cmb_cari.currentText().strip()
        cat   = self.cmb_cat.currentText()
        return start, end, typ, cari, cat

    def apply_filters(self):
        start, end, typ, cari, cat = self._current_filters()
        self.table.setRowCount(0)
        total_qty = 0.0; total_amt = 0.0

        for row in self._data:
            y,m,d = map(int, row["dt"].split("-"))
            dt = QDate(y,m,d).toPyDate()
            if dt < start or dt > end: continue
            if typ != "Hepsi" and row["typ"] != typ: continue
            if cat != "Tümü" and row["cat"] != cat: continue
            if cari and cari.lower() not in row["cari"].lower(): continue

            self._append_row([row["dt"], row["typ"], row["doc"], row["cari"], row["product"],
                              row["qty"], row["unit"], row["amount"], row["cash"], row["note"]])
            total_qty += float(row["qty"]); total_amt += float(row["amount"])

        self.lbl_summary.setText(f"Toplam Miktar: {TR.toString(total_qty,'f',3)}   •   Toplam Tutar: {TR.toString(total_amt,'f',2)}")

    def clear_filters(self):
        self.dt_start.setDate(QDate.currentDate().addMonths(-1))
        self.dt_end.setDate(QDate.currentDate())
        self.cmb_type.setCurrentIndex(0)
        self.cmb_cat.setCurrentIndex(0)
        self.cmb_cari.setCurrentIndex(-1); self.cmb_cari.setEditText("")
        self.apply_filters()

    # --- Tablo yardımcı ---
    def _append_row(self, values):
        r = self.table.rowCount(); self.table.insertRow(r)
        for c, val in enumerate(values):
            if isinstance(val, float):
                prec = 3 if c == 5 else 2
                text = TR.toString(val, 'f', prec)
            else:
                text = str(val)
            item = QTableWidgetItem(text)
            if c >= 5 and isinstance(val, (int,float)):
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(r, c, item)

    # --- Dışa aktarma ---
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "CSV olarak kaydet", "rapor.csv", "CSV (*.csv)")
        if not path: return
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
            w.writerow(headers)
            for r in range(self.table.rowCount()):
                row = [self.table.item(r, c).text() if self.table.item(r, c) else "" for c in range(self.table.columnCount())]
                w.writerow(row)
        QMessageBox.information(self, "Dışa aktarıldı", "CSV dosyası kaydedildi.")

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "PDF olarak kaydet", "rapor.pdf", "PDF (*.pdf)")
        if not path: return
        from PyQt6.QtCore import QSettings
        s = QSettings("OrbitX", "KuyumcuERP")
        company = s.value("company/name", "Şirket Adı")
        period  = f"{self.dt_start.date().toString('dd.MM.yyyy')} – {self.dt_end.date().toString('dd.MM.yyyy')}"
        headers = [self.table.horizontalHeaderItem(i).text() for i in range(self.table.columnCount())]
        body = []
        for r in range(self.table.rowCount()):
            cells = [self.table.item(r, c).text() if self.table.item(r, c) else "" for c in range(self.table.columnCount())]
            body.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
        html = f"""
        <h2 style='margin:0'>{company}</h2>
        <div style='margin-bottom:10px;'>Alım / Satım Raporu — Dönem: {period}</div>
        <table border='1' cellspacing='0' cellpadding='3' style='border-collapse:collapse;font-size:10pt;'>
            <thead><tr>{"".join(f"<th>{h}</th>" for h in headers)}</tr></thead>
            <tbody>{"".join(body)}</tbody>
        </table>
        """
        doc = QTextDocument(); doc.setHtml(html)
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(path)
        doc.print(printer)
        QMessageBox.information(self, "Dışa aktarıldı", "PDF dosyası kaydedildi.")
