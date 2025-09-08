### app/pages/sales.py ###

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QDateEdit,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem, QAbstractItemView,
    QHeaderView, QSplitter, QSpinBox, QDoubleSpinBox, QMessageBox, QGroupBox,
    QFormLayout
)
from PyQt6.QtCore import Qt, QDate, QLocale, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter, QLinearGradient, QColor, QPalette
from random import randint, choice
from dialogs import NewSaleItemDialog
from theme import elevate

TR = QLocale(QLocale.Language.Turkish, QLocale.Country.Turkey)

# — Mock veriler (prod-ready)
CUSTOMERS = [
    "Ahmet Yılmaz — 0555 123 4567",
    "Mehmet Demir — 0555 234 5678",
    "Zeynep Arslan — 0555 345 6789",
    "Ayşe Kaya — 0555 456 7890",
    "Ali Çelik — 0555 567 8901",
    "Emre Korkmaz — 0555 678 9012",
    "Gizem Yıldız — 0555 789 0123",
    "Caner Özkan — 0555 890 1234",
    "İrem Şahin — 0555 901 2345",
    "Burak Aydın — 0555 012 3456"
]

SUPPLIERS = [
    "ABC Kuyumculuk — 0555 111 2222",
    "XYZ Altın — 0555 333 4444",
    "GoldCenter — 0555 555 6666",
    "AltınMarkt — 0555 777 8888",
    "KülçeSarraf — 0555 999 0000"
]

PRODUCTS = [
    # Altın Takılar
    {"Kod":"STK0001","Ad":"Bilezik 22 Ayar","Kategori":"Altın Takı","Gram":7.90,"Fiyat":25300.00,"Stok":15},
    {"Kod":"STK0002","Ad":"Bilezik 18 Ayar","Kategori":"Altın Takı","Gram":8.20,"Fiyat":19800.00,"Stok":8},
    {"Kod":"STK0003","Ad":"Yüzük 22 Ayar","Kategori":"Altın Takı","Gram":4.50,"Fiyat":14500.00,"Stok":22},
    {"Kod":"STK0004","Ad":"Yüzük 18 Ayar","Kategori":"Altın Takı","Gram":3.80,"Fiyat":9200.00,"Stok":12},
    {"Kod":"STK0005","Ad":"Kolye 22 Ayar","Kategori":"Altın Takı","Gram":12.30,"Fiyat":39700.00,"Stok":6},
    {"Kod":"STK0006","Ad":"Kolye 18 Ayar","Kategori":"Altın Takı","Gram":10.80,"Fiyat":26100.00,"Stok":9},
    {"Kod":"STK0007","Ad":"Küpe 22 Ayar","Kategori":"Altın Takı","Gram":6.20,"Fiyat":20000.00,"Stok":18},
    {"Kod":"STK0008","Ad":"Küpe 18 Ayar","Kategori":"Altın Takı","Gram":5.50,"Fiyat":13300.00,"Stok":14},
    {"Kod":"STK0009","Ad":"Set 22 Ayar","Kategori":"Altın Takı","Gram":18.70,"Fiyat":60500.00,"Stok":4},
    {"Kod":"STK0010","Ad":"Set 18 Ayar","Kategori":"Altın Takı","Gram":16.40,"Fiyat":39700.00,"Stok":7},

    # Gümüş Takılar
    {"Kod":"STK0011","Ad":"Gümüş Bilezik","Kategori":"Gümüş Takı","Gram":25.0,"Fiyat":850.00,"Stok":35},
    {"Kod":"STK0012","Ad":"Gümüş Yüzük","Kategori":"Gümüş Takı","Gram":8.5,"Fiyat":290.00,"Stok":45},
    {"Kod":"STK0013","Ad":"Gümüş Kolye","Kategori":"Gümüş Takı","Gram":22.0,"Fiyat":750.00,"Stok":28},
    {"Kod":"STK0014","Ad":"Gümüş Küpe","Kategori":"Gümüş Takı","Gram":6.0,"Fiyat":205.00,"Stok":52},

    # Külçe ve Çubuk
    {"Kod":"STK0015","Ad":"Külçe 1gr","Kategori":"Külçe","Gram":1.0,"Fiyat":2800.00,"Stok":100},
    {"Kod":"STK0016","Ad":"Külçe 2.5gr","Kategori":"Külçe","Gram":2.5,"Fiyat":7000.00,"Stok":80},
    {"Kod":"STK0017","Ad":"Külçe 5gr","Kategori":"Külçe","Gram":5.0,"Fiyat":14000.00,"Stok":60},
    {"Kod":"STK0018","Ad":"Külçe 10gr","Kategori":"Külçe","Gram":10.0,"Fiyat":28000.00,"Stok":40},
    {"Kod":"STK0019","Ad":"Külçe 25gr","Kategori":"Külçe","Gram":25.0,"Fiyat":70000.00,"Stok":25},
    {"Kod":"STK0020","Ad":"Külçe 50gr","Kategori":"Külçe","Gram":50.0,"Fiyat":140000.00,"Stok":15},

    # Gram Altın
    {"Kod":"STK0021","Ad":"Gram Altın 22 Ayar","Kategori":"Gram Altın","Gram":1.0,"Fiyat":2735.50,"Stok":200},
    {"Kod":"STK0022","Ad":"Gram Altın 18 Ayar","Kategori":"Gram Altın","Gram":1.0,"Fiyat":2090.00,"Stok":150},

    # Ziynet
    {"Kod":"STK0023","Ad":"Ziynet Bilezik","Kategori":"Ziynet","Gram":15.0,"Fiyat":12000.00,"Stok":12},
    {"Kod":"STK0024","Ad":"Ziynet Yüzük","Kategori":"Ziynet","Gram":8.0,"Fiyat":6400.00,"Stok":20},
    {"Kod":"STK0025","Ad":"Ziynet Kolye","Kategori":"Ziynet","Gram":20.0,"Fiyat":16000.00,"Stok":8},
]

def tl(v: float) -> str:  # ₺ formatı
    try: return TR.toCurrencyString(v, "₺")
    except: return f"{v:,.2f} ₺"

class SalesPage(QWidget):
    """Alış–Satış işlemleri (frontend/mock)"""
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
        title = QLabel("Alış–Satış İşlemleri")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #E9EDF2; font-weight: 700;")
        header.addWidget(title, 0, Qt.AlignmentFlag.AlignLeft)

        hint = QLabel("Müşteri seçimi, satır ekleme ve işlem özeti • mock")
        hint.setProperty("variant", "muted")
        hint.setStyleSheet("font-size: 12px;")
        header.addWidget(hint, 0, Qt.AlignmentFlag.AlignRight)
        root.addLayout(header)

        # — üst form (müşteri, belge no, tarih, işlem türü) - Kompakt Tasarım
        form_card = QFrame(objectName="Glass")
        elevate(form_card, "dim", blur=20, y=6)
        form = QVBoxLayout(form_card)
        form.setContentsMargins(16, 12, 16, 12)   # ↓
        form.setSpacing(8)                        # ↓

        form_title = QLabel("İşlem Bilgileri")
        form_title.setFont(QFont("Segoe UI", 12, QFont.Weight.DemiBold))  # ↓ boyut
        form_title.setStyleSheet("color: #E9EDF2; margin-bottom: 2px;")
        form.addWidget(form_title)

        # ortak küçük input stili (padding ve min-width'ler küçüldü)
        small_input_css = """
            padding: 8px 10px;
            border-radius: 8px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.12);
            color: #E9EDF2;
            font-size: 12px;
        """

        # İlk satır: Ana bilgiler (İşlem türü, Müşteri, Belge No, Tarih)
        first_row = QHBoxLayout()
        first_row.setSpacing(12)

        # İşlem türü
        type_layout = QVBoxLayout()
        type_label = QLabel("İşlem Türü")
        type_label.setStyleSheet("color: #B7C0CC; font-size: 11px; font-weight: 500;")
        self.cmb_type = QComboBox()
        self.cmb_type.addItems(["Satış", "Alış"])
        self.cmb_type.setCurrentIndex(0)
        self.cmb_type.currentTextChanged.connect(self._on_transaction_type_changed)
        self.cmb_type.setStyleSheet(f"QComboBox{{{small_input_css} min-width: 96px;}}"
                                    "QComboBox::drop-down{border:none;width:16px;}"
                                    "QComboBox QAbstractItemView{background:rgba(28,34,44,0.98);color:#E9EDF2;border:1px solid rgba(255,255,255,0.08);selection-background-color:#4C7DFF;padding:4px;}")
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.cmb_type)
        first_row.addLayout(type_layout)

        # Müşteri/Tedarikçi
        customer_layout = QVBoxLayout()
        self.lbl_customer = QLabel("Müşteri")
        self.lbl_customer.setStyleSheet("color: #B7C0CC; font-size: 11px; font-weight: 500;")
        self.cmb_customer = QComboBox()
        self.cmb_customer.addItems(CUSTOMERS)
        self.cmb_customer.setCurrentIndex(0)
        self.cmb_customer.setStyleSheet(f"QComboBox{{{small_input_css} min-width: 200px;}}"
                                        "QComboBox::drop-down{border:none;width:16px;}"
                                        "QComboBox QAbstractItemView{background:rgba(28,34,44,0.98);color:#E9EDF2;border:1px solid rgba(255,255,255,0.08);selection-background-color:#4C7DFF;padding:4px;}")
        customer_layout.addWidget(self.lbl_customer)
        customer_layout.addWidget(self.cmb_customer)
        first_row.addLayout(customer_layout, 1)  # Esnek genişlik

        # Belge numarası
        doc_layout = QVBoxLayout()
        doc_label = QLabel("Belge No")
        doc_label.setStyleSheet("color: #B7C0CC; font-size: 11px; font-weight: 500;")
        import random
        doc_no = f"SL{f'{random.randint(1, 9999):04d}'}"
        self.in_docno = QLineEdit(doc_no)
        self.in_docno.setStyleSheet(f"QLineEdit{{{small_input_css} min-width: 110px;}} QLineEdit:focus{{border-color:#4C7DFF;background:rgba(76,125,255,0.08);}}")
        doc_layout.addWidget(doc_label)
        doc_layout.addWidget(self.in_docno)
        first_row.addLayout(doc_layout)

        # Tarih
        date_layout = QVBoxLayout()
        date_label = QLabel("Tarih")
        date_label.setStyleSheet("color: #B7C0CC; font-size: 11px; font-weight: 500;")
        self.in_date = QDateEdit(QDate.currentDate())
        self.in_date.setCalendarPopup(True)
        self.in_date.setStyleSheet(f"QDateEdit{{{small_input_css} min-width: 110px;}} QDateEdit::drop-down{{border:none;width:16px;}} QDateEdit:focus{{border-color:#4C7DFF;background:rgba(76,125,255,0.08);}}")
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.in_date)
        first_row.addLayout(date_layout)

        form.addLayout(first_row)

        # İkinci satır: Açıklama ve aksiyon butonları
        second_row = QHBoxLayout()
        second_row.setSpacing(12)

        # Açıklama
        notes_layout = QVBoxLayout()
        notes_label = QLabel("Açıklama (Opsiyonel)")
        notes_label.setStyleSheet("color: #B7C0CC; font-size: 11px; font-weight: 500;")
        self.in_notes = QLineEdit()
        self.in_notes.setPlaceholderText("Genel açıklama...")
        self.in_notes.setStyleSheet(f"QLineEdit{{{small_input_css}}} QLineEdit:focus{{border-color:#4C7DFF;background:rgba(76,125,255,0.08);}}")
        notes_layout.addWidget(notes_label)
        notes_layout.addWidget(self.in_notes)
        second_row.addLayout(notes_layout, 1)  # Esnek genişlik

        # Aksiyon butonları
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        self.btn_add = QPushButton("Ürün Ekle")
        self.btn_edit = QPushButton("Düzenle")
        self.btn_del = QPushButton("Sil")
        self.btn_edit.setEnabled(False)
        self.btn_del.setEnabled(False)

        # Daha kompakt buton stilleri
        for btn in [self.btn_add, self.btn_edit, self.btn_del]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 12px;
                    border-radius: 10px;
                    background: rgba(76,125,255,0.1);
                    border: 2px solid rgba(76,125,255,0.3);
                    color: #E9EDF2;
                    font-size: 12px;
                    font-weight: 600;
                    min-width: 90px;
                }
                QPushButton:hover {
                    border-color: #97B7FF;
                    background: rgba(76,125,255,0.2);
                    color: #F1F4F8;
                }
                QPushButton:pressed {
                    background: rgba(76,125,255,0.3);
                }
                QPushButton:disabled {
                    color: #6B7785;
                    border-color: rgba(255,255,255,0.08);
                    background: rgba(255,255,255,0.02);
                }
            """)

        buttons_layout.addWidget(self.btn_add)
        buttons_layout.addWidget(self.btn_edit)
        buttons_layout.addWidget(self.btn_del)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)  # Butonları alta hizala

        second_row.addLayout(buttons_layout)
        form.addLayout(second_row)

        root.addWidget(form_card, 0)  # Form daha az yer kaplasın

        # — içerik: sol satırlar / sağ özet
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(8)

        # Sol: tablo kartı
        table_card = QFrame(objectName="Glass")
        elevate(table_card, "dim", blur=28, y=8)
        tlayout = QVBoxLayout(table_card)
        tlayout.setContentsMargins(16, 16, 16, 16)
        tlayout.setSpacing(8)

        lbl_items = QLabel("İşlem Satırları")
        lbl_items.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_items.setStyleSheet("color: #E9EDF2; margin-bottom: 4px;")
        tlayout.addWidget(lbl_items)

        self.table = QTableWidget(0, 7, self)
        self.table.setHorizontalHeaderLabels(["Kod","Ürün","Gram","Adet","Birim Fiyat","Tutar","Not"])
        self.table.verticalHeader().setVisible(False)
        self.table.setCornerButtonEnabled(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._toggle_actions)

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

        # Header stilleri - Stok yönetimindeki gibi güzel
        hdr = self.table.horizontalHeader()
        hdr.setDefaultAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        hdr.setStretchLastSection(False)
        hdr.setMinimumSectionSize(60)
        hdr.setDefaultSectionSize(120)
        hdr.setStyleSheet("""
            QHeaderView::section {
                background: rgba(20,26,48,0.95);
                border: 1px solid rgba(255,255,255,0.15);
                border-bottom: 3px solid rgba(76,125,255,0.5);
                border-right: 1px solid rgba(255,255,255,0.08);
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
                border-left: 1px solid rgba(255,255,255,0.15);
                border-top-left-radius: 10px;
            }
            QHeaderView::section:last {
                border-right: 1px solid rgba(255,255,255,0.15);
                border-top-right-radius: 10px;
            }
        """)

        # Kolon oranları
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 90)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # ürün adı
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 80)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 70)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 110)
        hdr.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(5, 110)
        hdr.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(6, 120)

        tlayout.addWidget(self.table)

        splitter.addWidget(table_card)
        splitter.setStretchFactor(0, 2)  # Sol panel (index 0) 2 birim büyüme

        # Sağ: özet panel - YENİDEN TASARLANDI
        right = QFrame(objectName="Glass")
        elevate(right, "dim", blur=28, y=8)
        r_layout = QVBoxLayout(right)
        r_layout.setContentsMargins(16, 16, 16, 16)
        r_layout.setSpacing(16)

        # --- 1. İşlem Özeti Grubu ---
        summary_group = QGroupBox("İşlem Özeti")
        summary_form = QFormLayout(summary_group)
        summary_form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        summary_form.setFormAlignment(Qt.AlignmentFlag.AlignRight)
        summary_form.setHorizontalSpacing(10)

        self.lbl_sum_count = QLabel("0")
        self.lbl_sum_sub   = QLabel(tl(0))
        self.lbl_sum_disc  = QLabel(tl(0))
        self.lbl_sum_total = QLabel(tl(0))
        self.lbl_sum_total.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.lbl_sum_total.setStyleSheet("color: #4C7DFF;")

        summary_form.addRow("Ürün Sayısı:", self.lbl_sum_count)
        summary_form.addRow("Ara Toplam:", self.lbl_sum_sub)
        summary_form.addRow("İndirim:", self.lbl_sum_disc)
        summary_form.addRow("Genel Toplam:", self.lbl_sum_total)

        r_layout.addWidget(summary_group)

        # --- 2. Ödeme Bilgileri Grubu — 2x2 net grid ---
        payment_group = QGroupBox("Ödeme Bilgileri")
        payment_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px; font-weight: 600; color: #E9EDF2;
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 12px;
                padding: 10px 12px 12px 12px;
                margin-top: 8px;
                background: rgba(255,255,255,0.03);
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 12px; padding: 2px 6px;
            }
        """)

        CTRL_H = 40  # tüm input/pill yükseklik standardı

        from PyQt6.QtWidgets import QGridLayout, QSizePolicy
        grid = QGridLayout(payment_group)
        grid.setContentsMargins(6, 6, 6, 6)
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(14)

        # — SOL ÜST: Ödeme Türü
        self.cmb_pay = QComboBox()
        self.cmb_pay.addItems(["Nakit", "Kart", "Havale", "Veresiye"])
        self.cmb_pay.setCurrentIndex(0)
        self.cmb_pay.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.cmb_pay.setFixedHeight(CTRL_H)
        self.cmb_pay.setStyleSheet("""
            QComboBox {
                padding: 8px 10px; border-radius: 10px;
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.12);
                color: #E9EDF2; font-size: 13px;
            }
            QComboBox::drop-down { border: none; width: 16px; }
            QComboBox QAbstractItemView {
                background: rgba(28,34,44,0.98); color: #E9EDF2;
                border: 1px solid rgba(255,255,255,0.08);
                selection-background-color: #4C7DFF; padding: 4px;
            }
        """)

        # — SAĞ ÜST: Büyük Toplam "pill"
        self._total_big = QLabel("Genel Toplam: 0 ₺")
        self._total_big.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._total_big.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._total_big.setFixedHeight(CTRL_H)
        self._total_big.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self._total_big.setStyleSheet("""
            QLabel {
                color: #E9EDF2; padding: 8px 10px; border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.10);
                background: rgba(255,255,255,0.04);
                font-weight: 700;
            }
        """)

        # — SOL ALT: Alınan Tutar
        self.in_paid = QDoubleSpinBox()
        self.in_paid.setRange(0, 1_000_000)
        self.in_paid.setDecimals(2)
        self.in_paid.setPrefix("₺ ")
        self.in_paid.setGroupSeparatorShown(True)
        self.in_paid.setLocale(TR)
        self.in_paid.setButtonSymbols(self.in_paid.ButtonSymbols.NoButtons)
        self.in_paid.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.in_paid.setFixedHeight(CTRL_H)
        self.in_paid.setStyleSheet("""
            QDoubleSpinBox {
                padding: 8px 10px; border-radius: 10px;
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.12);
                color: #E9EDF2; font-size: 13px;
            }
            QDoubleSpinBox:focus {
                border-color: #4C7DFF; background: rgba(76,125,255,0.08);
            }
        """)

        # — SAĞ ALT: Para Üstü / Kalan "pill"
        self.lbl_change = QLabel("Para Üstü: 0 ₺")
        self.lbl_change.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_change.setFixedHeight(CTRL_H)
        self.lbl_change.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.lbl_change.setStyleSheet("""
            QLabel {
                color: #2ECC71; font-weight: 600; padding: 8px 10px;
                border-radius: 10px; background: rgba(46,204,113,0.10);
                border: 1px solid rgba(46,204,113,0.25);
            }
        """)

        self.lbl_remaining = QLabel("Kalan (Veresiye): 0 ₺")
        self.lbl_remaining.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_remaining.setFixedHeight(CTRL_H)
        self.lbl_remaining.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.lbl_remaining.setStyleSheet("""
            QLabel {
                color: #FF6B6B; font-weight: 600; padding: 8px 10px;
                border-radius: 10px; background: rgba(255,107,107,0.10);
                border: 1px solid rgba(255,107,107,0.25);
            }
        """)
        self.lbl_remaining.setVisible(False)

        # 2x2 yerleşim — artık hiçbir şey "üst üste" değil
        grid.addWidget(self.cmb_pay,      0, 0)
        grid.addWidget(self._total_big,   0, 1)
        grid.addWidget(self.in_paid,      1, 0)
        grid.addWidget(self.lbl_change,   1, 1)

        # satırlar arasında ince ayırıcı istersen:
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: rgba(255,255,255,0.08);")
        # grid.addWidget(line, 2, 0, 1, 2)   # istersen aç
        r_layout.addWidget(payment_group)

        r_layout.addStretch(1)  # <<< EN ÖNEMLİ KISIM: Butonları en alta iter

        # Ana aksiyon butonları - Daha büyük ve belirgin
        self.btn_save  = QPushButton("İşlemi Kaydet")
        self.btn_print = QPushButton("Makbuz Yazdır")

        # Büyük aksiyon butonları
        for btn in [self.btn_save, self.btn_print]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 12px 18px;
                    border-radius: 12px;
                    background: rgba(76,125,255,0.15);
                    border: 2px solid rgba(76,125,255,0.4);
                    color: #E9EDF2;
                    font-size: 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    border-color: #97B7FF;
                    background: rgba(76,125,255,0.25);
                    color: #F1F4F8;
                }
                QPushButton:pressed {
                    background: rgba(76,125,255,0.35);
                }
            """)

        r_layout.addWidget(self.btn_save)
        r_layout.addWidget(self.btn_print)

        right.setMinimumWidth(360)
        right.setMaximumWidth(380)
        splitter.addWidget(right)
        splitter.setStretchFactor(1, 1)  # Sağ panel (index 1) 1 birim büyüme

        root.addWidget(splitter, 1)

        # olaylar
        self.btn_add.clicked.connect(self.add_item)
        self.btn_edit.clicked.connect(self.edit_item)
        self.btn_del.clicked.connect(self.remove_item)
        self.btn_save.clicked.connect(self.save_transaction)
        self.in_paid.valueChanged.connect(self._recalc_change)
        self.cmb_pay.currentTextChanged.connect(self._on_payment_type_changed)

        # Başlangıç durumu için ödeme türü olayını tetikle
        self._on_payment_type_changed(self.cmb_pay.currentText())

        # ilk oran
        QTimer.singleShot(0, lambda: splitter.setSizes([self.width()-380, 340]))  # biraz daha dar üstten, sağ panel sabit
        QTimer.singleShot(0, lambda: self._paint_sky(self.width(), self.height()))

    # — kozmik arka plan
    def _paint_sky(self, w: int, h: int):
        if w <= 0 or h <= 0: return
        pm = QPixmap(w, h)
        pm.fill(Qt.GlobalColor.black)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        g = QLinearGradient(0,0,w,h)
        g.setColorAt(0.0, QColor(10,16,32))
        g.setColorAt(0.5, QColor(20,26,48))
        g.setColorAt(1.0, QColor(12,18,36))
        p.fillRect(0,0,w,h,g)
        p.setPen(Qt.PenStyle.NoPen)
        for _ in range(int((w*h)/18000)):
            x, y = randint(0,w), randint(0,h)
            r = choice([1,1,2])
            p.setBrush(QColor(255,255,255, randint(70,150)))
            p.drawEllipse(x,y,r,r)
        p.end()
        self._sky.setPixmap(pm)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, '_sky'):
            self._sky.resize(self.size())
            self._paint_sky(self.width(), self.height())

    # — yardımcılar
    def _toggle_actions(self):
        has = len(self.table.selectedItems()) > 0
        self.btn_edit.setEnabled(has)
        self.btn_del.setEnabled(has)

    def _selected_row(self):
        idxs = self.table.selectionModel().selectedRows()
        return idxs[0].row() if idxs else None

    def _calc_total(self) -> float:
        total = 0.0
        for i in range(self.table.rowCount()):
            total += float(self.table.item(i, 5).data(Qt.ItemDataRole.UserRole) or 0.0)
        return total

    def _recalc(self):
        rows = self.table.rowCount()
        total = self._calc_total()
        self.lbl_sum_count.setText(f"Satır: {rows}")
        self.lbl_sum_sub.setText(f"Ara Toplam: {tl(total)}")        # istersen gerçek ara toplamı ayır
        self.lbl_sum_disc.setText(f"İndirim: {tl(0.0)}")
        self.lbl_sum_total.setText(f"Genel Toplam: {tl(total)}")
        self._total_big.setText(f"Genel Toplam: {tl(total)}")        # yeni büyük başlık
        self._recalc_change()

    def _on_transaction_type_changed(self, transaction_type):
        """İşlem türü değiştiğinde müşteri/tedarikçi seçimini güncelle"""
        if transaction_type == "Alış":
            self.lbl_customer.setText("Tedarikçi")
            self.cmb_customer.clear()
            self.cmb_customer.addItems(SUPPLIERS)
        else:  # Satış
            self.lbl_customer.setText("Müşteri")
            self.cmb_customer.clear()
            self.cmb_customer.addItems(CUSTOMERS)

    def _on_payment_type_changed(self, payment_type):
        if payment_type == "Veresiye":
            self.in_paid.setEnabled(False)
            self.in_paid.setValue(0)
        else:
            self.in_paid.setEnabled(True)
        self._recalc_change()

    def _recalc_change(self):
        total = self._calc_total()
        if self.cmb_pay.currentText() == "Veresiye":
            self.lbl_change.setVisible(False)
            self.lbl_remaining.setVisible(True)
            self.lbl_remaining.setText(f"Kalan (Veresiye): {tl(total)}")
            # grid sağ altına remaining'i koy (change yerine)
            if self.lbl_change.parentWidget() is not None:
                parent = self.lbl_change.parentWidget().layout()
                if parent is not None:
                    parent.replaceWidget(self.lbl_change, self.lbl_remaining)
        else:
            self.lbl_remaining.setVisible(False)
            self.lbl_change.setVisible(True)
            paid = float(self.in_paid.value())
            change = max(0.0, paid - total)
            self.lbl_change.setText(f"Para Üstü: {tl(change)}")
            if self.lbl_remaining.parentWidget() is not None:
                parent = self.lbl_remaining.parentWidget().layout()
                if parent is not None:
                    parent.replaceWidget(self.lbl_remaining, self.lbl_change)

    # — satır işlemleri (mock)
    def add_item(self):
        dlg = NewSaleItemDialog(self, PRODUCTS)
        if dlg.exec():
            data = dlg.data()

            # Stok kontrolü
            product = None
            for p in PRODUCTS:
                if p["Kod"] == data["Kod"]:
                    product = p
                    break

            if product:
                if self.cmb_type.currentText() == "Satış" and data["Adet"] > product["Stok"]:
                    QMessageBox.warning(self, "Stok Uyarısı",
                                      f"{product['Ad']} için yeterli stok yok!\n"
                                      f"Mevcut stok: {product['Stok']} adet\n"
                                      f"İstenen: {data['Adet']} adet")
                    return
                elif self.cmb_type.currentText() == "Alış":
                    # Alış işleminde stok artacak, kontrol etmeye gerek yok
                    pass

                # Stok bilgisini göster
                QMessageBox.information(self, "Stok Bilgisi",
                                      f"{product['Ad']}\n"
                                      f"Mevcut Stok: {product['Stok']} adet\n"
                                      f"İşlem: {self.cmb_type.currentText()}")

            self._append_row(data)
            self._recalc()

    def edit_item(self):
        row = self._selected_row()
        if row is None: return
        current = {
            "Kod": self.table.item(row,0).text(),
            "Ad":  self.table.item(row,1).text(),
            "Gram": float(self.table.item(row,2).text().replace(",", ".")),
            "Adet": int(self.table.item(row,3).text()),
            "BirimFiyat": float(self.table.item(row,4).data(Qt.ItemDataRole.UserRole) or 0.0),
            "Not": self.table.item(row,6).text(),
        }
        dlg = NewSaleItemDialog(self, PRODUCTS, current)
        if dlg.exec():
            self._set_row(row, dlg.data())
            self._recalc()

    def remove_item(self):
        row = self._selected_row()
        if row is None: return
        self.table.removeRow(row)
        self._recalc()
        self._toggle_actions()

    # — tablo yazma
    def _append_row(self, d):
        r = self.table.rowCount()
        self.table.insertRow(r)
        self._set_row(r, d)

    def _set_row(self, r, d):
        self.table.setItem(r,0, QTableWidgetItem(d["Kod"]))
        self.table.setItem(r,1, QTableWidgetItem(d["Ad"]))
        it_gram = QTableWidgetItem(f"{d['Gram']:.2f}")
        it_gram.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(r,2, it_gram)
        it_adet = QTableWidgetItem(str(d["Adet"]))
        it_adet.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(r,3, it_adet)
        it_price = QTableWidgetItem(tl(d["BirimFiyat"]))
        it_price.setData(Qt.ItemDataRole.UserRole, float(d["BirimFiyat"]))
        it_price.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(r,4, it_price)
        tutar = d["Adet"] * d["BirimFiyat"]
        it_total = QTableWidgetItem(tl(tutar))
        it_total.setData(Qt.ItemDataRole.UserRole, float(tutar))
        it_total.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(r,5, it_total)
        self.table.setItem(r,6, QTableWidgetItem(d.get("Not","")))

    def save_transaction(self):
        """İşlemi kaydet ve formu temizle"""
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek satır bulunamadı!")
            return

        # İşlem özeti
        transaction_type = self.cmb_type.currentText()
        customer = self.cmb_customer.currentText()
        total = self.lbl_sum_total.text().split(":")[1].strip()

        # Veresiye kontrolü
        if self.cmb_pay.currentText() == "Veresiye":
            remaining = self.lbl_remaining.text().split(":")[1].strip()
            QMessageBox.information(self, "Veresiye İşlemi",
                                  f"{transaction_type} işlemi kaydedildi.\n"
                                  f"Cari: {customer}\n"
                                  f"Toplam Tutar: {total}\n"
                                  f"Kalan Tutar: {remaining}\n\n"
                                  f"Bu tutar ilgili cari hesaba borç olarak işlenecektir.")
        else:
            QMessageBox.information(self, "İşlem Başarılı",
                                  f"{transaction_type} işlemi başarıyla kaydedildi!\n"
                                  f"Cari: {customer}\n"
                                  f"Toplam Tutar: {total}")

        # Formu temizle - yeni işlem için hazırla
        self._clear_form()

    def _clear_form(self):
        """Formu temizle"""
        self.table.setRowCount(0)
        self.in_notes.clear()
        self.in_paid.setValue(0)
        self.lbl_sum_count.setText("Satır: 0")
        self.lbl_sum_sub.setText("Ara Toplam: 0 ₺")
        self.lbl_sum_disc.setText("İndirim: 0 ₺")
        self.lbl_sum_total.setText("Genel Toplam: 0 ₺")
        self.lbl_change.setText("Para Üstü: 0 ₺")
        self.lbl_remaining.setText("Kalan Tutar: 0 ₺")

        # Yeni belge numarası oluştur
        import random
        doc_no = f"SL{f'{random.randint(1, 9999):04d}'}"
        self.in_docno.setText(doc_no)
