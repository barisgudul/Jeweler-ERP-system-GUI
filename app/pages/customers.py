### app/pages/customers.py ###
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QTableWidget, QTableWidgetItem, QFrame, QAbstractItemView,
    QHeaderView, QTextEdit, QSplitter, QMessageBox
)
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtCore import Qt, QLocale, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QLinearGradient
from random import randint, choice
import os

from theme import elevate
from dialogs import NewCustomerDialog

# TR yerel para
TR = QLocale(QLocale.Language.Turkish, QLocale.Country.Turkey)
def tl(x: float) -> str:
    try:
        return TR.toCurrencyString(x, "₺")
    except Exception:
        return f"{x:,.2f} ₺"

MOCK_NAMES = [
    "Ahmet Yılmaz","Mehmet Demir","Zeynep Arslan","Ayşe Kaya","Ali Çelik",
    "Emre Korkmaz","Elif Öztürk","Merve Aydın","Mustafa Şahin","Gizem Yıldız"
]
STATUSES = ["Aktif","Pasif"]

def generate_customers(n=24):
    rows = []
    for i in range(n):
        ad = MOCK_NAMES[i % len(MOCK_NAMES)]
        rows.append({
            "Kod": f"CAR{i+1:04}",
            "AdSoyad": ad,
            "Telefon": f"05{randint(10,99)} {randint(100,999)} {randint(10,99)} {randint(10,99)}",
            "Bakiye": float(randint(-5000, 15000)),
            "Son İşlem": f"{randint(1,28):02}.0{choice([6,7,8,9])}.2025",
            "Durum": choice(STATUSES),
        })
    return rows

class CustomersPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._all_rows = generate_customers()
        self._filtered = list(self._all_rows)

        # === KOZMİK ARKA PLAN ===
        self._sky = QLabel(self)
        self._sky.lower()
        self._sky.setScaledContents(True)
        self._sky.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        # Başlık
        header = QHBoxLayout()
        title = QLabel("Cari Hesap Yönetimi")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.addWidget(title, 0, Qt.AlignmentFlag.AlignLeft)

        hint = QLabel("Müşteri listesi, arama/filtre ve dışa aktarma • mock veri")
        hint.setProperty("variant", "muted")
        header.addWidget(hint, 0, Qt.AlignmentFlag.AlignRight)
        root.addLayout(header)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.search = QLineEdit(placeholderText="Ara: kod, ad, telefon…")
        self.search.setMinimumWidth(300)
        self.search.textChanged.connect(self.apply_filters)

        self.filter = QComboBox()
        self.filter.addItems(["Tümü"] + STATUSES)
        self.filter.setFixedWidth(120)
        self.filter.currentIndexChanged.connect(self.apply_filters)

        self.btn_new  = QPushButton("Yeni Müşteri")
        self.btn_edit = QPushButton("Düzenle"); self.btn_edit.setEnabled(False)
        self.btn_del  = QPushButton("Sil");     self.btn_del.setEnabled(False)
        self.btn_xls  = QPushButton("Excel'e Aktar")
        self.btn_pdf  = JButton = QPushButton("PDF'e Aktar")

        toolbar.addWidget(self.search)
        toolbar.addWidget(self.filter)
        toolbar.addStretch(1)
        for b in (self.btn_new, self.btn_edit, self.btn_del, self.btn_xls, JButton):
            toolbar.addWidget(b)
        root.addLayout(toolbar)

        # === İçerik: Sol tablo / Sağ çekmece
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(8)

        # Sol kart (tablo)
        table_card = QFrame(objectName="Glass")
        elevate(table_card, "dim", blur=28, y=8)
        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(16, 16, 16, 16)
        table_layout.setSpacing(8)

        table_title = QLabel("Müşteri Listesi")
        table_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        table_layout.addWidget(table_title)

        self.table = QTableWidget(0, 6, self)
        self.table.setHorizontalHeaderLabels(["Kod","Ad Soyad","Telefon","Bakiye","Son İşlem","Durum"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setCornerButtonEnabled(False)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._toggle_row_actions)
        self.table.itemDoubleClicked.connect(self._open_drawer)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        pal = self.table.palette()
        pal.setColor(QPalette.ColorRole.Base, QColor(0,0,0,0))
        pal.setColor(QPalette.ColorRole.AlternateBase, QColor(255,255,255,10))
        self.table.setPalette(pal)

        hdr = self.table.horizontalHeader()
        hdr.setDefaultAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        hdr.setStretchLastSection(False)
        hdr.setMinimumSectionSize(60)
        hdr.setDefaultSectionSize(120)
        # Kolon oranları: Ad Soyad esner; diğerleri sabit
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed);   self.table.setColumnWidth(0, 90)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed);   self.table.setColumnWidth(2, 130)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed);   self.table.setColumnWidth(3, 110)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed);   self.table.setColumnWidth(4, 110)
        hdr.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed);   self.table.setColumnWidth(5, 90)

        # Header stilleri - İyileştirilmiş tasarım
        hdr.setStyleSheet("""
            QHeaderView::section {
                background: rgba(20,26,48,0.95);
                border: none; /* Önce tüm kenarlıkları sıfırla */
                border-bottom: 3px solid rgba(76,125,255,0.5);
                border-right: 1px solid rgba(255,255,255,0.08); /* Dikey ayraç */
                padding: 16px 12px;
                font-weight: 700;
                font-size: 13px;
                color: #F1F4F8;
                letter-spacing: 0.5px;
                text-align: center;
            }
            QHeaderView::section:hover {
                background: rgba(30,36,58,0.98);
                border-bottom-color: rgba(76,125,255,0.7);
                color: #FFFFFF;
            }
            QHeaderView::section:first {
                border-top-left-radius: 10px; /* Sadece ilk bölümün solu yuvarlak */
            }
            QHeaderView::section:last {
                border-top-right-radius: 10px; /* Sadece son bölümün sağı yuvarlak */
                border-right: none; /* Son bölümde sağ ayraç olmasın */
            }
        """)

        # Tablo stilleri - Daha belirgin ve büyük
        self.table.setStyleSheet("""
            QTableWidget {
                background: rgba(10,16,32,0.4);
                border: 2px solid rgba(255,255,255,0.12);
                border-radius: 12px;
                gridline-color: rgba(255,255,255,0.08);
                selection-background-color: rgba(76,125,255,0.15);
            }
            QTableWidget::item {
                padding: 12px 16px;
                border-bottom: 1px solid rgba(255,255,255,0.06);
                background: transparent;
                color: #E9EDF2;
                font-size: 13px;
                border-radius: 4px;
            }
            QTableWidget::item:selected {
                background: rgba(76,125,255,0.2);
                color: #F1F4F8;
                border: 1px solid rgba(76,125,255,0.4);
            }
            QTableWidget::item:hover {
                background: rgba(76,125,255,0.08);
            }
            QTableWidget::item:alternate {
                background: rgba(255,255,255,0.02);
            }
        """)

        pal = self.table.palette()
        pal.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0, 0))
        pal.setColor(QPalette.ColorRole.AlternateBase, QColor(255, 255, 255, 8))
        pal.setColor(QPalette.ColorRole.Text, QColor(241, 244, 248))
        pal.setColor(QPalette.ColorRole.Highlight, QColor(76, 125, 255, 150))
        pal.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.table.setPalette(pal)

        # Alternatif satır rengi aktif
        self.table.setAlternatingRowColors(True)

        table_layout.addWidget(self.table)

        self.summary = QLabel()
        self.summary.setProperty("variant","muted")
        self.summary.setStyleSheet("""
            QLabel {
                color: #B7C0CC;
                font-size: 13px;
                font-weight: 500;
                padding: 12px 16px;
                background: rgba(20,26,48,0.6);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 8px;
                margin-top: 8px;
            }
        """)
        table_layout.addWidget(self.summary)

        splitter.addWidget(table_card)
        splitter.setStretchFactor(0, 1)  # sol taraf büyüsün

        # Sağ kart (çekmece)
        drawer_card = QFrame(objectName="Glass")
        drawer_card.setMinimumWidth(320)
        drawer_card.setMaximumWidth(360)
        elevate(drawer_card, "dim", blur=28, y=8)
        self.drawer_layout = QVBoxLayout(drawer_card)
        self.drawer_layout.setContentsMargins(16, 16, 16, 16)
        self.drawer_layout.setSpacing(8)

        self.drawer_title = QLabel("Müşteri Hareketleri")
        self.drawer_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.drawer_layout.addWidget(self.drawer_title)

        # Müşteri hareketleri için gerçek tablo
        self.transactions_table = QTableWidget(0, 3, self)
        self.transactions_table.setHorizontalHeaderLabels(["Tarih", "İşlem", "Tutar"])
        self.transactions_table.verticalHeader().setVisible(False)
        self.transactions_table.setCornerButtonEnabled(False)
        self.transactions_table.setAlternatingRowColors(True)
        self.transactions_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.transactions_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.transactions_table.setMaximumHeight(300)  # Sınırlı yükseklik

        # Tablo stilleri
        self.transactions_table.setStyleSheet("""
            QTableWidget {
                background: rgba(10,16,32,0.3);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 8px;
                gridline-color: rgba(255,255,255,0.08);
            }
            QTableWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid rgba(255,255,255,0.04);
                background: transparent;
                color: #E9EDF2;
            }
            QTableWidget::item:selected {
                background: rgba(76,125,255,0.12);
                color: #F1F4F8;
            }
            QTableWidget::item:hover {
                background: rgba(76,125,255,0.06);
            }
        """)

        # Palette ayarı
        pal = self.transactions_table.palette()
        pal.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0, 0))
        pal.setColor(QPalette.ColorRole.AlternateBase, QColor(255, 255, 255, 6))
        pal.setColor(QPalette.ColorRole.Text, QColor(241, 244, 248))
        pal.setColor(QPalette.ColorRole.Highlight, QColor(76, 125, 255, 120))
        pal.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.transactions_table.setPalette(pal)

        # Header stilleri
        hdr = self.transactions_table.horizontalHeader()
        hdr.setDefaultAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        hdr.setStretchLastSection(False)
        hdr.setMinimumSectionSize(80)
        hdr.setStyleSheet("""
            QHeaderView::section {
                background: rgba(20,26,48,0.9);
                border: 1px solid rgba(255,255,255,0.1);
                border-bottom: 2px solid rgba(76,125,255,0.4);
                border-right: 1px solid rgba(255,255,255,0.05);
                padding: 12px 8px;
                font-weight: 600;
                font-size: 12px;
                color: #E9EDF2;
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

        # Kolon genişlikleri
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.transactions_table.setColumnWidth(0, 100)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.transactions_table.setColumnWidth(1, 120)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.drawer_layout.addWidget(self.transactions_table)

        # Özet bilgi için genişletilmiş label
        self.transaction_summary = QLabel("")
        self.transaction_summary.setStyleSheet("""
            QLabel {
                color: #E9EDF2;
                font-size: 11px;
                font-weight: 500;
                padding: 12px 16px;
                background: rgba(20,26,48,0.6);
                border: 1px solid rgba(76,125,255,0.2);
                border-radius: 8px;
                text-align: left;
                margin-top: 8px;
                line-height: 1.4;
            }
        """)
        self.transaction_summary.setMinimumHeight(120)  # Çok satırlı için yeterli yükseklik
        self.drawer_layout.addWidget(self.transaction_summary)

        splitter.addWidget(drawer_card)
        splitter.setStretchFactor(1, 0)

        root.addWidget(splitter, 1)  # içerik tüm yüksekliği kullansın

        # Eventler
        self.btn_new.clicked.connect(self.on_new)
        self.btn_edit.clicked.connect(self.on_edit)
        self.btn_del.clicked.connect(self.on_delete)
        self.btn_xls.clicked.connect(self.export_excel)
        JButton.clicked.connect(self.export_pdf)

        # Veri
        self.apply_filters()

        # İlk render’da kozmik bg ve splitter oranı
        QTimer.singleShot(0, lambda: splitter.setSizes([self.width()-380, 360]))
        QTimer.singleShot(0, lambda: self._paint_sky(self.width(), self.height()))

    # === Kozmik arka plan ===
    def _paint_sky(self, w: int, h: int):
        if w <= 0 or h <= 0:
            return
        pm = QPixmap(w, h); pm.fill(Qt.GlobalColor.black)
        painter = QPainter(pm); painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor(10,16,32))
        grad.setColorAt(0.5, QColor(20,26,48))
        grad.setColorAt(1.0, QColor(12,18,36))
        painter.fillRect(0, 0, w, h, grad)

        painter.setPen(Qt.PenStyle.NoPen)
        for _ in range(int((w * h) / 20000)):
            x = randint(0, w); y = randint(0, h)
            r = randint(1, 2)
            c = QColor(255, 255, 255, randint(60, 140))
            painter.setBrush(c)
            painter.drawEllipse(x, y, r, r)

        painter.end()
        self._sky.setPixmap(pm)

    def resizeEvent(self, e=None):
        super().resizeEvent(e)
        if hasattr(self, "_sky"):
            self._sky.resize(self.size())
            self._paint_sky(self.width(), self.height())

    # === Davranışlar
    def _toggle_row_actions(self):
        has = len(self.table.selectedItems()) > 0
        self.btn_edit.setEnabled(has)
        self.btn_del.setEnabled(has)

    def apply_filters(self):
        text = (self.search.text() or "").strip().lower()
        f = self.filter.currentText()

        self._filtered = []
        for r in self._all_rows:
            if f != "Tümü" and r["Durum"] != f:
                continue
            blob = f"{r['Kod']} {r['AdSoyad']} {r['Telefon']}".lower()
            if text and text not in blob:
                continue
            self._filtered.append(r)

        self.populate(self._filtered)
        self.update_summary(self._filtered)

    def populate(self, rows):
        self.table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(r["Kod"]))
            self.table.setItem(i, 1, QTableWidgetItem(r["AdSoyad"]))
            self.table.setItem(i, 2, QTableWidgetItem(r["Telefon"]))

            # Bakiye sütunu - renklendirme ile
            bakiye_item = QTableWidgetItem(tl(r["Bakiye"]))
            bakiye_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            if r["Bakiye"] > 0:
                bakiye_item.setForeground(QColor(76, 175, 80))  # Yeşil - alacaklı
            elif r["Bakiye"] < 0:
                bakiye_item.setForeground(QColor(244, 67, 54))  # Kırmızı - borçlu
            self.table.setItem(i, 3, bakiye_item)

            self.table.setItem(i, 4, QTableWidgetItem(r["Son İşlem"]))
            self.table.setItem(i, 5, QTableWidgetItem(r["Durum"]))

    def update_summary(self, rows):
        self.summary.setText(f"Toplam müşteri: {len(rows)} adet")

    def _create_balance_card(self, balance: float, parent=None) -> QFrame:
        """Müşterinin bakiye durumunu gösteren profesyonel kart"""
        card = QFrame(parent)
        card.setObjectName("BalanceCard")
        layout = QVBoxLayout(card)
        layout.setSpacing(6)
        layout.setContentsMargins(16, 14, 16, 14)

        bakiye_durum = "Alacaklı" if balance > 0 else "Borçlu" if balance < 0 else "Bakiye Yok"

        lbl_title = QLabel("Genel Bakiye")
        lbl_title.setStyleSheet("color: #B7C0CC; font-size: 12px; font-weight: 600;")

        lbl_balance = QLabel(tl(abs(balance)))
        lbl_balance.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))

        lbl_status = QLabel(bakiye_durum)
        lbl_status.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))

        # Renklendirme
        if balance > 0:
            card.setStyleSheet("background: rgba(76, 175, 80, 0.1); border: 1px solid rgba(76, 175, 80, 0.3); border-radius: 12px;")
            lbl_balance.setStyleSheet("color: #4CAF50;")
            lbl_status.setStyleSheet("color: #4CAF50;")
        elif balance < 0:
            card.setStyleSheet("background: rgba(244, 67, 54, 0.1); border: 1px solid rgba(244, 67, 54, 0.3); border-radius: 12px;")
            lbl_balance.setStyleSheet("color: #F44336;")
            lbl_status.setStyleSheet("color: #F44336;")
        else:
            card.setStyleSheet("background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px;")
            lbl_balance.setStyleSheet("color: #E9EDF2;")
            lbl_status.setStyleSheet("color: #B7C0CC;")

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_balance)
        layout.addWidget(lbl_status)
        return card

    def _open_drawer(self):
        row = self.table.currentRow()
        if row < 0:
            return

        # Eski drawer'ı temizle
        for i in reversed(range(self.drawer_layout.count())):
            widget = self.drawer_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()

        kod = self.table.item(row,0).text()
        ad  = self.table.item(row,1).text()

        # Müşteri verisini bul
        current_customer = None
        for customer in self._all_rows:
            if customer["Kod"] == kod:
                current_customer = customer
                break

        if not current_customer:
            return

        # 1. Başlık
        drawer_title = QLabel(f"{ad} — {kod}")
        drawer_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        drawer_title.setStyleSheet("color: #E9EDF2;")
        self.drawer_layout.addWidget(drawer_title)

        # 2. Bakiye Kartı
        balance_card = self._create_balance_card(current_customer.get("Bakiye", 0.0))
        self.drawer_layout.addWidget(balance_card)

        # 3. Hareketler Başlığı
        transactions_title = QLabel("Son Hareketler")
        transactions_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        transactions_title.setStyleSheet("color: #E9EDF2; margin-top: 12px;")
        self.drawer_layout.addWidget(transactions_title)

        # 4. Hareketler Tablosu
        self.transactions_table = QTableWidget(0, 3, self)
        self.transactions_table.setHorizontalHeaderLabels(["Tarih", "İşlem", "Tutar"])
        self.transactions_table.verticalHeader().setVisible(False)
        self.transactions_table.setCornerButtonEnabled(False)
        self.transactions_table.setAlternatingRowColors(True)
        self.transactions_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.transactions_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.transactions_table.setMaximumHeight(250)

        # Tablo stilleri
        self.transactions_table.setStyleSheet("""
            QTableWidget {
                background: rgba(10,16,32,0.3);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 8px;
                gridline-color: rgba(255,255,255,0.08);
            }
            QTableWidget::item {
                padding: 8px 12px;
                border-bottom: 1px solid rgba(255,255,255,0.04);
                background: transparent;
                color: #E9EDF2;
            }
            QTableWidget::item:selected {
                background: rgba(76,125,255,0.12);
                color: #F1F4F8;
            }
            QTableWidget::item:hover {
                background: rgba(76,125,255,0.06);
            }
        """)

        # Header stilleri
        hdr = self.transactions_table.horizontalHeader()
        hdr.setDefaultAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        hdr.setStretchLastSection(False)
        hdr.setStyleSheet("""
            QHeaderView::section {
                background: rgba(20,26,48,0.9);
                border: 1px solid rgba(255,255,255,0.1);
                border-bottom: 2px solid rgba(76,125,255,0.4);
                border-right: 1px solid rgba(255,255,255,0.05);
                padding: 10px 8px;
                font-weight: 600;
                font-size: 11px;
                color: #E9EDF2;
                text-align: center;
            }
            QHeaderView::section:hover {
                background: rgba(30,36,58,0.95);
                border-bottom-color: rgba(76,125,255,0.6);
                color: #F1F4F8;
            }
        """)

        # Kolon genişlikleri
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.transactions_table.setColumnWidth(0, 80)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.transactions_table.setColumnWidth(2, 100)

        # Mock hareket verisi
        transactions = []
        for i in range(1, 11):  # Daha fazla veri için
            t = f"{i:02}.09.2025"
            tutar = randint(-1800, 2500)
            tur = "Satış" if tutar > 0 else "Alış"
            transactions.append((t, tur, tutar))

        # Tabloya ekle
        self.transactions_table.setRowCount(len(transactions))
        for i, (tarih, tur, tutar) in enumerate(transactions):
            # Tarih
            tarih_item = QTableWidgetItem(tarih)
            tarih_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.transactions_table.setItem(i, 0, tarih_item)

            # İşlem türü (finansal olarak daha anlamlı)
            tur_item = QTableWidgetItem(tur)
            tur_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
            # Renk kodlaması: Satış kırmızı, alış yeşil
            if tur == "Satış":
                tur_item.setBackground(QColor(244, 67, 54, 60))  # Kırmızı - satış
            else:
                tur_item.setBackground(QColor(76, 175, 80, 60))  # Yeşil - alış
            self.transactions_table.setItem(i, 1, tur_item)

            # Tutar
            tutar_str = tl(abs(tutar))
            tutar_item = QTableWidgetItem(tutar_str)
            tutar_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            # Renk kodlaması: Satış kırmızı, alış yeşil
            if tur == "Satış":
                tutar_item.setForeground(QColor(244, 67, 54))  # Kırmızı - satış
            else:
                tutar_item.setForeground(QColor(76, 175, 80))  # Yeşil - alış
            self.transactions_table.setItem(i, 2, tutar_item)

        self.drawer_layout.addWidget(self.transactions_table)

        # 5. Özet bilgileri
        summary_frame = QFrame()
        summary_frame.setStyleSheet("""
            QFrame {
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 8px;
                padding: 12px;
                margin-top: 8px;
            }
        """)
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setSpacing(6)

        # Özet bilgileri
        satis_toplam_30gun = sum(t[2] for t in transactions if t[2] > 0)
        alis_toplam_30gun = sum(abs(t[2]) for t in transactions if t[2] < 0)
        hareket_sayisi = len(transactions)

        lbl_summary_title = QLabel("Son 30 Gün Özeti")
        lbl_summary_title.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        lbl_summary_title.setStyleSheet("color: #E9EDF2; margin-bottom: 4px;")

        lbl_satis = QLabel(f"Satış: {tl(satis_toplam_30gun)}")
        lbl_satis.setStyleSheet("color: #F44336; font-size: 12px;")

        lbl_alis = QLabel(f"Alış: {tl(alis_toplam_30gun)}")
        lbl_alis.setStyleSheet("color: #4CAF50; font-size: 12px;")

        lbl_count = QLabel(f"Hareket Sayısı: {hareket_sayisi}")
        lbl_count.setStyleSheet("color: #B7C0CC; font-size: 12px;")

        lbl_phone = QLabel(f"Telefon: {current_customer.get('Telefon', '-')}")
        lbl_phone.setStyleSheet("color: #B7C0CC; font-size: 12px;")

        summary_layout.addWidget(lbl_summary_title)
        summary_layout.addWidget(lbl_satis)
        summary_layout.addWidget(lbl_alis)
        summary_layout.addWidget(lbl_count)
        summary_layout.addWidget(lbl_phone)

        self.drawer_layout.addWidget(summary_frame)
        self.drawer_layout.addStretch(1)  # Boşluğu alta iter

    # CRUD (mock)
    def on_new(self):
        dlg = NewCustomerDialog(self)
        if dlg.exec():
            self._all_rows.insert(0, dlg.data())
            self.apply_filters()
            QMessageBox.information(self, "Başarılı", "Müşteri başarıyla eklendi.")

    def on_edit(self):
        row = self.table.currentRow()
        if row < 0:
            return
        current = self._filtered[row]
        dlg = NewCustomerDialog(self, current)
        if dlg.exec():
            new = dlg.data()
            for r in self._all_rows:
                if r["Kod"] == current["Kod"]:
                    r.update(new)
                    break
            self.apply_filters()
            QMessageBox.information(self, "Başarılı", "Müşteri başarıyla güncellendi.")

    def on_delete(self):
        row = self.table.currentRow()
        if row < 0:
            return
        current = self._filtered[row]
        reply = QMessageBox.question(self, "Onay", f"{current['AdSoyad']} müşterisini silmek istediğinizden emin misiniz?")
        if reply == QMessageBox.StandardButton.Yes:
            kod = self.table.item(row,0).text()
            self._all_rows = [r for r in self._all_rows if r["Kod"] != kod]
            self.apply_filters()
            QMessageBox.information(self, "Başarılı", "Müşteri başarıyla silindi.")

    # Exportlar
    def export_excel(self):
        try:
            from openpyxl import Workbook
            os.makedirs("exports", exist_ok=True)
            wb = Workbook(); ws = wb.active; ws.title = "Cari"
            headers = ["Kod","Ad Soyad","Telefon","Bakiye","Son İşlem","Durum"]
            ws.append(headers)
            for r in self._filtered:
                ws.append([r[h] if h!="Bakiye" else r["Bakiye"] for h in headers])
            wb.save("exports/cari_listesi.xlsx")
            self.summary.setText(self.summary.text() + " • Excel: exports/cari_listesi.xlsx")
        except Exception as e:
            self.summary.setText("Excel aktarımında hata: " + str(e))

    def export_pdf(self):
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.units import mm
            os.makedirs("exports", exist_ok=True)
            c = canvas.Canvas("exports/cari_listesi.pdf", pagesize=A4)
            w, h = A4
            y = h - 20*mm
            c.setFont("Helvetica-Bold", 12)
            c.drawString(20*mm, y, "Cari Listesi"); y -= 10*mm
            c.setFont("Helvetica", 9)
            for r in self._filtered:
                line = f"{r['Kod']:6}  {r['AdSoyad']:<22}  {r['Telefon']:>14}  {r['Bakiye']:>10.2f}  {r['Son İşlem']:>10}  {r['Durum']}"
                c.drawString(15*mm, y, line)
                y -= 6*mm
                if y < 20*mm:
                    c.showPage(); y = h - 20*mm; c.setFont("Helvetica", 9)
            c.save()
            self.summary.setText(self.summary.text() + " • PDF: exports/cari_listesi.pdf")
        except Exception as e:
            self.summary.setText("PDF aktarımında hata: " + str(e))
