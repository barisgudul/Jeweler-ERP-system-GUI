### app/pages/finance.py ###
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QSplitter,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView,
    QLineEdit, QComboBox, QDateEdit, QTimeEdit, QPushButton, QGroupBox, QFormLayout,
    QDoubleSpinBox, QTextEdit, QMessageBox, QDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, QTime, QLocale, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter, QLinearGradient, QColor, QPalette, QShortcut, QKeySequence
from random import randint, choice
from theme import elevate, apply_dialog_theme

TR = QLocale(QLocale.Language.Turkish, QLocale.Country.Turkey)

# Mock cari hesap listesi
CUSTOMERS_FOR_FINANCE = [
    "Müşteri Seç",
    "Ahmet Yılmaz — Cari: CAR0001",
    "Mehmet Demir — Cari: CAR0002",
    "Zeynep Arslan — Cari: CAR0003",
    "Ayşe Kaya — Cari: CAR0004",
    "Ali Çelik — Cari: CAR0005",
    "Emre Korkmaz — Cari: CAR0006"
]

def tl(x: float) -> str:
    try:
        return TR.toCurrencyString(x, "₺")
    except Exception:
        return f"{x:,.2f} ₺"

# --- Yeni Finansal Kayıt Diyaloğu (zarif sürüm) ------------------------------------
class NewFinanceRecordDialog(QDialog):
    """Giriş/Çıkış için anlaşılır + zarif modal (canlı doğrulamalı)"""

    def __init__(self, parent=None, record_type="Giriş"):
        super().__init__(parent)
        self.record_type = record_type  # "Giriş" | "Çıkış"

        # Pencere
        self.setModal(True)
        self.setMinimumWidth(520)
        self.setWindowFlag(Qt.WindowType.MSWindowsFixedSizeDialogHint)
        self.setWindowTitle(f"{record_type} Kaydı Ekle - Finansal İşlem")
        self.setObjectName("FinanceDialog")
        apply_dialog_theme(self, "dim")

        # Kısayollar
        QShortcut(QKeySequence("Esc"), self, activated=self.reject)
        QShortcut(QKeySequence("Return"), self, activated=lambda: self.try_accept(force=True))

        # Ana iskelet
        root = QVBoxLayout(self); root.setContentsMargins(24,24,24,24); root.setSpacing(18)

        # Başlık + rozet
        header = QHBoxLayout()
        h_title = QLabel(f"{record_type} İşlemi Kaydet")
        h_title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        h_title.setProperty("variant", "title")  # Tema fonksiyonu bunu tanıyacak
        h_sub = QLabel("Zorunlu alanlar * ile işaretlidir")
        h_sub.setProperty("variant", "muted")  # Tema fonksiyonu bunu tanıyacak
        h_sub.setStyleSheet("margin-left:8px;")
        header.addWidget(h_title); header.addStretch(1); header.addWidget(h_sub)
        root.addLayout(header)

        # Kart - tema ile uyumlu
        card = QFrame(objectName="DialogCard")
        elevate(card, "dim", blur=24, y=6)
        body = QVBoxLayout(card); body.setContentsMargins(18,18,18,18); body.setSpacing(14)

        # --- ZAMAN ---
        g_time = QGroupBox("İşlem Zamanı")
        time_grid = QGridLayout(g_time); time_grid.setHorizontalSpacing(12); time_grid.setVerticalSpacing(8)
        time_grid.addWidget(self._lbl("Tarih *"), 0, 0)
        self.f_date = QDateEdit(QDate.currentDate()); self.f_date.setCalendarPopup(True)
        time_grid.addWidget(self.f_date, 1, 0)
        time_grid.addWidget(self._lbl("Saat *"), 0, 1)
        self.f_time = QTimeEdit(QTime.currentTime()); self.f_time.setDisplayFormat("HH:mm")
        time_grid.addWidget(self.f_time, 1, 1)
        body.addWidget(g_time)

        # --- İŞLEM DETAYLARI ---
        g_tx = QGroupBox("İşlem Detayları")
        tx_grid = QGridLayout(g_tx); tx_grid.setHorizontalSpacing(12); tx_grid.setVerticalSpacing(8)

        tx_grid.addWidget(self._lbl("Hesap *"), 0, 0)
        self.f_acc = QComboBox()
        self.f_acc.addItems(["Kasa","Banka — VakıfBank","Banka — Ziraat"])
        self.f_acc.setMaxVisibleItems(5)
        tx_grid.addWidget(self.f_acc, 1, 0)

        tx_grid.addWidget(self._lbl("Kategori *"), 0, 1)
        self.f_cat = QComboBox()
        if record_type == "Giriş":
            self.f_cat.addItems(["Satış Tahsilatı","Müşteri Ödemesi","Diğer Gelirler"])
        else:
            self.f_cat.addItems(["Masraf","Tedarikçi Ödemesi","Kira","Elektrik","Diğer Giderler"])
        self.f_cat.setMaxVisibleItems(5)
        tx_grid.addWidget(self.f_cat, 1, 1)

        tx_grid.addWidget(self._lbl("İlişkili Cari (opsiyonel)"), 2, 0, 1, 2)
        self.f_customer = QComboBox()
        self.f_customer.addItems(CUSTOMERS_FOR_FINANCE)
        self.f_customer.setMaxVisibleItems(10)  # Maksimum 10 öğe görünsün, fazlası kaydırılır
        tx_grid.addWidget(self.f_customer, 3, 0, 1, 2)
        body.addWidget(g_tx)

        # --- TUTAR & AÇIKLAMA ---
        g_amt = QGroupBox("Tutar ve Açıklama")
        amt_grid = QGridLayout(g_amt); amt_grid.setHorizontalSpacing(12); amt_grid.setVerticalSpacing(8)

        amt_grid.addWidget(self._lbl("Tutar (₺) *"), 0, 0)
        self.f_amt = QDoubleSpinBox()
        self.f_amt.setRange(0.00, 1_000_000.00)
        self.f_amt.setDecimals(2)
        self.f_amt.setSingleStep(10.00)
        self.f_amt.setPrefix("₺ ")
        self.f_amt.setLocale(TR)   # Türkçe biçim
        self.f_amt.setButtonSymbols(self.f_amt.ButtonSymbols.NoButtons)
        self.f_amt.setAlignment(Qt.AlignmentFlag.AlignRight)
        amt_grid.addWidget(self.f_amt, 1, 0)

        amt_grid.addWidget(self._lbl("Açıklama *"), 2, 0)
        self.f_desc = QTextEdit(); self.f_desc.setPlaceholderText("Kısa ama anlamlı bir açıklama yazın…")
        self.f_desc.setMaximumHeight(90)
        amt_grid.addWidget(self.f_desc, 3, 0, 1, 2)
        body.addWidget(g_amt)

        # --- ÖZET ŞERİDİ ---
        self.summary = QLabel("")
        self.summary.setProperty("variant", "muted")  # Tema fonksiyonu bunu tanıyacak
        self.summary.setStyleSheet("padding:6px 8px; border:1px solid rgba(255,255,255,0.08);"
                                   "border-radius:8px; background:rgba(255,255,255,0.04);")
        body.addWidget(self.summary)

        root.addWidget(card)

        # Alt butonlar
        actions = QHBoxLayout(); actions.addStretch(1)
        self.btn_cancel = QPushButton("İptal"); self.btn_cancel.clicked.connect(self.reject)
        self.btn_save = QPushButton("Kaydet"); self.btn_save.setProperty("variant","primary")
        self.btn_save.clicked.connect(lambda: self.try_accept(force=False))
        actions.addWidget(self.btn_cancel); actions.addWidget(self.btn_save)
        root.addLayout(actions)

        # Vurgu rengi (Giriş/Çıkış) - tema fonksiyonuna ek olarak
        accent = QColor(76,175,80) if record_type == "Giriş" else QColor(244,67,54)
        # apply_dialog_theme fonksiyonu zaten temel stilleri uyguluyor
        # Sadece GroupBox vurgu rengini ek olarak ayarla
        current_style = self.styleSheet()
        self.setStyleSheet(current_style + f"""
            QGroupBox {{
                border: 2px solid rgba({accent.red()},{accent.green()},{accent.blue()},0.3);
            }}
        """)

        # Bağlantılar (canlı doğrulama + özet)
        for w in (self.f_date, self.f_time, self.f_acc, self.f_cat, self.f_amt, self.f_desc):
            if hasattr(w, "textChanged"): w.textChanged.connect(self._refresh_state)
        self.f_amt.valueChanged.connect(self._refresh_state)
        self._refresh_state()

    # ---------- yardımcılar ----------
    def _lbl(self, txt):
        lbl = QLabel(txt)
        lbl.setStyleSheet("font-weight:600;")  # Renk tema fonksiyonundan gelecek
        return lbl

    def _refresh_state(self):
        # Özet
        short_desc = self.f_desc.toPlainText().strip().splitlines()[0] if self.f_desc.toPlainText().strip() else "—"
        self.summary.setText(
            f"Hesap: <b>{self.f_acc.currentText()}</b> • Kategori: <b>{self.f_cat.currentText()}</b> • "
            f"Tutar: <b>₺ {self.f_amt.value():,.2f}</b> • Tarih/Saat: {self.f_date.date().toString('dd.MM.yyyy')} {self.f_time.time().toString('HH:mm')} • "
            f"Açıklama: {short_desc}"
        )

        # Doğrulama
        valid = True
        valid &= self.f_amt.value() > 0
        valid &= len(self.f_desc.toPlainText().strip()) > 0
        self.btn_save.setEnabled(valid)

        # Alan kenarlıkları (hata vurgusu) - uygulama temasıyla uyumlu
        # QDoubleSpinBox için placeholder yerine tooltip kullan
        if self.f_amt.value() <= 0:
            self.f_amt.setToolTip("⚠️ Tutar 0'dan büyük olmalıdır")
            self.f_amt.setStyleSheet("QDoubleSpinBox { border: 2px solid rgba(244,67,54,0.5); }")
        else:
            self.f_amt.setToolTip("")
            self.f_amt.setStyleSheet("")

        if len(self.f_desc.toPlainText().strip()) == 0:
            self.f_desc.setPlaceholderText("⚠️ Açıklama zorunludur")
        else:
            self.f_desc.setPlaceholderText("Kısa ama anlamlı bir açıklama yazın…")

    def try_accept(self, force=False):
        # Enter ile geldiğinde, geçerli değilse kaydetme
        if not force and not self.btn_save.isEnabled():
            return
        if self.btn_save.isEnabled():
            self.accept()

    def data(self):
        import random
        doc_no = f"FIN{random.randint(1000, 9999):04d}"
        return {
            "tarih": self.f_date.date().toString("dd.MM.yyyy"),
            "saat":  self.f_time.time().toString("HH:mm"),
            "hesap": self.f_acc.currentText(),
            "tur":   self.record_type,
            "kategori": self.f_cat.currentText(),
            "cari":  self.f_customer.currentText(),
            "belge_no": doc_no,
            "aciklama": self.f_desc.toPlainText().strip(),
            "tutar": self.f_amt.value()
        }

# --- cam KPI kartı - GÜNCELLENDİ (DAHA KOMPAKT) ---
def _kpi(title: str, value: str, sub: str = "") -> QFrame:
    card = QFrame()
    card.setObjectName("Glass")
    elevate(card, "dim", blur=28, y=8)
    v = QVBoxLayout(card)
    v.setContentsMargins(16, 10, 16, 10) # Dikey boşluk azaltıldı
    v.setSpacing(4) # Spacing azaltıldı

    t = QLabel(title)
    t.setProperty("variant", "muted")
    t.setStyleSheet("color: #B7C0CC; font-size: 11px; font-weight: 500;")
    v.addWidget(t)

    val = QLabel(value)
    f = QFont("Segoe UI", 20, QFont.Weight.Bold) # Font boyutu küçültüldü
    val.setFont(f)
    val.setStyleSheet("color: #E9EDF2; font-weight: 700;")
    v.addWidget(val)

    if sub:
        s = QLabel(sub)
        s.setProperty("variant","muted")
        s.setStyleSheet("color: #B7C0CC; font-size: 10px;")
        v.addWidget(s)

    return card

# --- ana sayfa ----------------------------------------------------------------
class FinancePage(QWidget):
    """Kasa & Finans (frontend/mock) — kozmik tema, orantılı yerleşim"""
    def __init__(self, parent=None):
        super().__init__(parent)

        # kozmik arka plan
        self._sky = QLabel(self)
        self._sky.lower()
        self._sky.setScaledContents(True)
        self._sky.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        # başlık
        header = QHBoxLayout()
        title = QLabel("Kasa & Finans")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setStyleSheet("color: #E9EDF2; font-weight: 700;")
        header.addWidget(title, 0, Qt.AlignmentFlag.AlignLeft)

        hint = QLabel("Günlük kasa, banka ve hareketler • mock arayüz")
        hint.setProperty("variant", "muted")
        hint.setStyleSheet("font-size: 12px;")
        header.addWidget(hint, 0, Qt.AlignmentFlag.AlignRight)
        root.addLayout(header)

        # --- üst KPI şeridi - GÜNCELLENDİ (DAHA KOMPAKT) ---
        kpi_grid = QGridLayout()
        kpi_grid.setHorizontalSpacing(16)
        kpi_grid.setVerticalSpacing(10) # Dikey boşluk azaltıldı
        kpi_grid.addWidget(_kpi("Kasa Bakiyesi", tl(215_450.00), "Güncel nakit"), 0, 0)
        kpi_grid.addWidget(_kpi("Banka Toplam", tl(1_485_200.00), "3 hesap aktif"), 0, 1)
        kpi_grid.addWidget(_kpi("Bugün Giriş", tl(86_500.00), "Tahsilat"), 0, 2)
        kpi_grid.addWidget(_kpi("Bugün Çıkış", tl(23_900.00), "Ödeme & Masraf"), 0, 3)
        kpi_grid.addWidget(_kpi("Net Günlük", tl(62_600.00), "Pozitif"), 0, 4)
        kpi_grid.addWidget(_kpi("Aylık Ciro", tl(2_450_000.00), "Bu ay toplam"), 1, 0)
        kpi_grid.addWidget(_kpi("Bekleyen Ödeme", tl(145_800.00), "Tedarikçi borç"), 1, 1)
        kpi_grid.addWidget(_kpi("Müşteri Borç", tl(89_200.00), "Aktif alacak"), 1, 2)
        kpi_grid.addWidget(_kpi("Kar Marjı", "%24.8", "Brüt kar"), 1, 3)
        kpi_grid.addWidget(_kpi("Günlük Hedef", tl(100_000.00), "Hedefe ulaştı"), 1, 4)
        for c in range(5): kpi_grid.setColumnStretch(c, 1)
        root.addLayout(kpi_grid)

        # --- filtre barı - Responsive
        filter_card = QFrame(objectName="Glass")
        elevate(filter_card, "dim", blur=24, y=6)
        fb = QVBoxLayout(filter_card)
        fb.setContentsMargins(16, 12, 16, 12)
        fb.setSpacing(8)

        # Üst satır: Arama ve temel filtreler
        top_filter_row = QHBoxLayout()
        top_filter_row.setSpacing(8)

        self.e_search = QLineEdit(placeholderText="Ara: açıklama, kategori, hesap…")
        self.e_search.setMinimumWidth(200)
        self.e_search.setMaximumWidth(300)
        self.e_search.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
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

        self.cmb_account = QComboBox()
        self.cmb_account.addItems(["Tüm Hesaplar", "Kasa", "Banka — VakıfBank", "Banka — Ziraat"])
        self.cmb_account.setMinimumWidth(120)
        self.cmb_account.setMaximumWidth(160)
        self.cmb_account.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
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

        self.cmb_type = QComboBox()
        self.cmb_type.addItems(["Tümü", "Giriş", "Çıkış"])
        self.cmb_type.setMinimumWidth(100)
        self.cmb_type.setMaximumWidth(120)
        self.cmb_type.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
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

        self.dt_from = QDateEdit(QDate.currentDate().addDays(-7))
        self.dt_from.setCalendarPopup(True)
        self.dt_from.setMinimumWidth(100)
        self.dt_from.setMaximumWidth(120)
        self.dt_from.setStyleSheet("""
            QDateEdit {
                padding: 8px 12px;
                border-radius: 8px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                color: #E9EDF2;
                font-size: 14px;
            }
            QDateEdit::drop-down {
                border: none;
            }
            QDateEdit:focus {
                border-color: #4C7DFF;
                background: rgba(76,125,255,0.06);
            }
        """)

        self.dt_to = QDateEdit(QDate.currentDate())
        self.dt_to.setCalendarPopup(True)
        self.dt_to.setMinimumWidth(100)
        self.dt_to.setMaximumWidth(120)
        self.dt_to.setStyleSheet("""
            QDateEdit {
                padding: 8px 12px;
                border-radius: 8px;
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.08);
                color: #E9EDF2;
                font-size: 14px;
            }
            QDateEdit::drop-down {
                border: none;
            }
            QDateEdit:focus {
                border-color: #4C7DFF;
                background: rgba(76,125,255,0.06);
            }
        """)

        self.cmb_quick = QComboBox()
        self.cmb_quick.addItems(["Son 7 gün", "Bu Ay", "Geçen Ay", "Yıl Başından Bugüne"])
        self.cmb_quick.setMinimumWidth(120)
        self.cmb_quick.setMaximumWidth(160)
        self.cmb_quick.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
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
        self.cmb_quick.currentIndexChanged.connect(self._apply_quick_range)
        self.cmb_quick.currentIndexChanged.connect(self._update_kpis)

        # İkinci satır: Export butonları
        bottom_filter_row = QHBoxLayout()
        bottom_filter_row.setSpacing(8)

        self.btn_export_xls = QPushButton("Excel'e Aktar")
        self.btn_export_xls.setEnabled(False)
        self.btn_export_xls.setToolTip("Devre dışı — backend/raporlama eklenecek")
        self.btn_export_pdf = QPushButton("PDF'e Aktar")
        self.btn_export_pdf.setEnabled(False)
        self.btn_export_pdf.setToolTip("Devre dışı — backend/raporlama eklenecek")

        # Buton stilleri
        for btn in [self.btn_export_xls, self.btn_export_pdf]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 8px 16px;
                    border-radius: 8px;
                    background: rgba(255,255,255,0.04);
                    border: 1px solid rgba(255,255,255,0.08);
                    color: #E9EDF2;
                    font-size: 14px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    border-color: #97B7FF;
                    background: rgba(76,125,255,0.06);
                    color: #F1F4F8;
                }
                QPushButton:pressed {
                    background: rgba(76,125,255,0.12);
                }
                QPushButton:disabled {
                    color: #6B7785;
                    border-color: rgba(255,255,255,0.04);
                    background: rgba(255,255,255,0.02);
                }
            """)

        # Top row'a widget'ları ekle
        top_filter_row.addWidget(self.e_search, 2)
        top_filter_row.addWidget(self.cmb_account, 1)
        top_filter_row.addWidget(self.cmb_type, 1)
        top_filter_row.addWidget(self.dt_from)
        top_filter_row.addWidget(QLabel("→"))
        top_filter_row.addWidget(self.dt_to)
        top_filter_row.addWidget(self.cmb_quick, 1)
        top_filter_row.addStretch(1)

        # Bottom row'a export butonlarını ekle
        bottom_filter_row.addStretch(1)
        bottom_filter_row.addWidget(self.btn_export_xls)
        bottom_filter_row.addWidget(self.btn_export_pdf)

        # Ana filter layout'una row'ları ekle
        fb.addLayout(top_filter_row)
        fb.addLayout(bottom_filter_row)
        root.addWidget(filter_card)

        # --- ana içerik: sol defter / sağ özet & form
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(8)

        # SOL — Kasa Defteri
        left = QFrame(objectName="Glass")
        elevate(left, "dim", blur=28, y=8)
        lv = QVBoxLayout(left)
        lv.setContentsMargins(16, 16, 16, 16)
        lv.setSpacing(8)

        lbl_left = QLabel("Kasa Defteri")
        lbl_left.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_left.setStyleSheet("color: #E9EDF2; margin-bottom: 4px;")
        lv.addWidget(lbl_left)

        self.table = QTableWidget(0, 7, self)
        self.table.setHorizontalHeaderLabels(["Tarih","Saat","Hesap","Tür","Kategori","Açıklama","Tutar"])
        self.table.verticalHeader().setVisible(False)
        self.table.setCornerButtonEnabled(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._toggle_right_actions)

        # Tablo stilleri
        self.table.setStyleSheet("""
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

        pal = self.table.palette()
        pal.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0, 0))
        pal.setColor(QPalette.ColorRole.AlternateBase, QColor(255, 255, 255, 6))
        pal.setColor(QPalette.ColorRole.Text, QColor(241, 244, 248))
        pal.setColor(QPalette.ColorRole.Highlight, QColor(76, 125, 255, 120))
        pal.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.table.setPalette(pal)

        # Header stilleri
        hdr = self.table.horizontalHeader()
        hdr.setDefaultAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        hdr.setStretchLastSection(False)
        hdr.setMinimumSectionSize(60)
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

        # Kolon oranları
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 96)   # tarih
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 70)   # saat
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(2, 160)  # hesap
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(3, 80)   # tür
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(4, 160)  # kategori
        hdr.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch) # açıklama
        hdr.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(6, 120)  # tutar

        lv.addWidget(self.table)

        # mock satırlar
        self._load_mock_rows()

        splitter.addWidget(left)
        splitter.setStretchFactor(0, 1)

        # SAĞ — Özet & Form (sabit genişlik) - GÜNCELLENDİ (YENİDEN DÜZENLENDİ)
        right = QFrame(objectName="Glass")
        elevate(right, "dim", blur=28, y=8)
        rv = QVBoxLayout(right)
        rv.setContentsMargins(16, 16, 16, 16)
        rv.setSpacing(12)

        # --- 1. Özet Grubu ---
        box_sum = QGroupBox("Özet")
        box_sum.setStyleSheet("""
            QGroupBox {
                font-weight: 600; color: #E9EDF2; border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px; margin-top: 8px; padding: 12px 8px 8px 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 8px; padding: 0 4px 0 4px;
                color: #E9EDF2; font-size: 13px;
            }
        """)
        sv = QVBoxLayout(box_sum)
        sv.setSpacing(8)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Toplam Giriş:"))
        row1.addStretch(1)
        self.lbl_sum_in = QLabel(tl(86_500.00))
        self.lbl_sum_in.setStyleSheet("color: #4CAF50; font-weight: bold;")
        row1.addWidget(self.lbl_sum_in)
        sv.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Toplam Çıkış:"))
        row2.addStretch(1)
        self.lbl_sum_out = QLabel(tl(23_900.00))
        self.lbl_sum_out.setStyleSheet("color: #F44336; font-weight: bold;")
        row2.addWidget(self.lbl_sum_out)
        sv.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Net Bakiye:"))
        row3.addStretch(1)
        self.lbl_sum_net = QLabel(tl(62_600.00))
        self.lbl_sum_net.setStyleSheet("color: #E9EDF2; font-weight: bold;")
        row3.addWidget(self.lbl_sum_net)
        sv.addLayout(row3)
        box_sum.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        # --- 2. İşlemler Grubu (YENİ, BİRLEŞTİRİLMİŞ) ---
        actions_group = QGroupBox("İşlemler")
        actions_group.setStyleSheet("""
            QGroupBox {
                font-weight: 600; color: #E9EDF2; border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px; margin-top: 8px; padding: 12px 8px 8px 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin; left: 8px; padding: 0 4px 0 4px;
                color: #E9EDF2; font-size: 13px;
            }
        """)
        actions_layout = QVBoxLayout(actions_group)
        actions_layout.setSpacing(8)

        # Yeni kayıt butonları
        new_record_layout = QHBoxLayout()
        new_record_layout.setSpacing(8)
        self.btn_new_income = QPushButton("➕ Yeni Gelir")
        self.btn_new_income.setToolTip("Yeni gelir kaydı oluştur")
        self.btn_new_expense = QPushButton("➖ Yeni Gider")
        self.btn_new_expense.setToolTip("Yeni gider kaydı oluştur")
        new_record_layout.addWidget(self.btn_new_income)
        new_record_layout.addWidget(self.btn_new_expense)

        self.btn_new_income.setStyleSheet("""
            QPushButton {
                padding: 10px; border-radius: 8px; background: rgba(76, 175, 80, 0.2);
                border: 1px solid rgba(76, 175, 80, 0.5); color: #E9EDF2;
                font-size: 13px; font-weight: 600; min-height: 38px;
            }
            QPushButton:hover { background: rgba(76, 175, 80, 0.3); border-color: rgba(129, 199, 132, 0.8); }
            QPushButton:pressed { background: rgba(76, 175, 80, 0.4); }
        """)
        self.btn_new_expense.setStyleSheet("""
            QPushButton {
                padding: 10px; border-radius: 8px; background: rgba(244, 67, 54, 0.2);
                border: 1px solid rgba(244, 67, 54, 0.5); color: #E9EDF2;
                font-size: 13px; font-weight: 600; min-height: 38px;
            }
            QPushButton:hover { background: rgba(244, 67, 54, 0.3); border-color: rgba(239, 83, 80, 0.8); }
            QPushButton:pressed { background: rgba(244, 67, 54, 0.4); }
        """)

        # Seçili işlem butonları
        edit_record_layout = QHBoxLayout()
        edit_record_layout.setSpacing(8)
        self.btn_edit = QPushButton("Düzenle")
        self.btn_edit.setEnabled(False)
        self.btn_edit.setToolTip("Seçili kaydı düzenle")
        self.btn_del = QPushButton("Sil")
        self.btn_del.setEnabled(False)
        self.btn_del.setToolTip("Seçili kaydı sil")
        edit_record_layout.addWidget(self.btn_edit)
        edit_record_layout.addWidget(self.btn_del)
        
        for btn in [self.btn_edit, self.btn_del]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 10px; border-radius: 8px; background: rgba(255,255,255,0.04);
                    border: 1px solid rgba(255,255,255,0.08); color: #E9EDF2;
                    font-size: 13px; font-weight: 500; min-height: 38px;
                }
                QPushButton:hover { border-color: #97B7FF; background: rgba(76,125,255,0.06); }
                QPushButton:pressed { background: rgba(76,125,255,0.12); }
                QPushButton:disabled {
                    color: #6B7785; border-color: rgba(255,255,255,0.04);
                    background: rgba(255,255,255,0.02);
                }
            """)

        actions_layout.addLayout(new_record_layout)
        actions_layout.addLayout(edit_record_layout)
        actions_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        # --- SAĞ PANEL YERLEŞİMİ ---
        rv.addWidget(box_sum)
        rv.addWidget(actions_group)
        rv.addStretch(1) # Boşluğu en alta it

        # Buton bağlantıları
        self.btn_new_income.clicked.connect(lambda: self.open_new_record_dialog("Giriş"))
        self.btn_new_expense.clicked.connect(lambda: self.open_new_record_dialog("Çıkış"))

        # not - Not kutusu
        note = QTextEdit(readOnly=True)
        note.setPlainText(
            "Not: Bu sayfa tasarım önizlemesidir.\n"
            "Kaydet/Düzenle/Sil ve dışa aktarma butonları şu an devre dışıdır.\n"
            "Veritabanına geçildiğinde tüm işlevler aktif hale getirilecektir."
        )
        note.setStyleSheet("""
            QTextEdit {
                background: rgba(20,26,48,0.6); border: 1px solid rgba(255,255,255,0.08);
                border-radius: 8px; color: #B7C0CC; font-size: 11px; padding: 8px;
            }
        """)
        note.setMaximumHeight(80)
        rv.addWidget(note)

        right.setMinimumWidth(340)
        right.setMaximumWidth(380)
        splitter.addWidget(right)

        root.addWidget(splitter, 1)

        # ilk oran
        QTimer.singleShot(0, lambda: splitter.setSizes([self.width()-360, 360]))
        QTimer.singleShot(0, lambda: self._paint_sky(self.width(), self.height()))

    # --- kozmik arka plan
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
        for _ in range(int((w*h)/20000)):
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

    # --- yardımcılar
    def _apply_quick_range(self):
        txt = self.cmb_quick.currentText()
        today = QDate.currentDate()
        if txt == "Son 7 gün":
            self.dt_to.setDate(today)
            self.dt_from.setDate(today.addDays(-7))
        elif txt == "Bu Ay":
            self.dt_from.setDate(QDate(today.year(), today.month(), 1))
            self.dt_to.setDate(today)
        elif txt == "Geçen Ay":
            m = today.addMonths(-1)
            self.dt_from.setDate(QDate(m.year(), m.month(), 1))
            self.dt_to.setDate(QDate(m.year(), m.month(), QDate(m.year(), m.month(), 1).daysInMonth()))
        elif txt == "Yıl Başından Bugüne":
            self.dt_from.setDate(QDate(today.year(), 1, 1))
            self.dt_to.setDate(today)

    def _update_kpis(self):
        """Tarih filtresine göre KPI'ları dinamik olarak güncelle"""
        selected_range = self.cmb_quick.currentText()

        # Mock güncel değerler - gerçek uygulamada veritabanından çekilecek
        if selected_range == "Son 7 gün":
            today_income = 86500.00
            today_outcome = 23900.00
        elif selected_range == "Bu Ay":
            today_income = 124500.00
            today_outcome = 45200.00
        elif selected_range == "Geçen Ay":
            today_income = 98700.00
            today_outcome = 32100.00
        else:  # Yıl başından bugüne
            today_income = 1543200.00
            today_outcome = 876500.00

        net_today = today_income - today_outcome

        # KPI kartlarını güncelle - dinamik etiketler için
        # Not: Gerçek uygulamada bu kartların text'lerini güncellemek için
        # kartları bir listede tutmak daha iyi olur

        # Özet alanlarını da güncelle
        self.lbl_sum_in.setText(tl(today_income))
        self.lbl_sum_out.setText(tl(today_outcome))
        self.lbl_sum_net.setText(tl(net_today))

    def _toggle_right_actions(self):
        has = len(self.table.selectedItems()) > 0
        self.btn_edit.setEnabled(False if not has else False)  # taslakta devre dışı
        self.btn_del.setEnabled(False if not has else False)

    def _load_mock_rows(self):
        # zengin örnek hareketler - prod-ready
        samples = [
            ("09.09.2025","09:15","Kasa","Giriş","Satış Tahsilatı","A. Yılmaz'a 22A bilezik satışı - nakit", 25_400.00),
            ("09.09.2025","09:45","Banka — VakıfBank","Giriş","Müşteri Ödemesi","M. Demir'den havale - borç kapat", 18_750.00),
            ("09.09.2025","10:30","Kasa","Giriş","Satış Tahsilatı","Z. Arslan'a küpe seti - kart", 45_900.00),
            ("09.09.2025","11:20","Banka — Ziraat","Giriş","Müşteri Ödemesi","E. Korkmaz'dan EFT - altın borç", 32_500.00),
            ("09.09.2025","12:10","Kasa","Çıkış","Masraf","Kırtasiye malzemeleri", -850.00),
            ("09.09.2025","13:45","Banka — VakıfBank","Çıkış","Tedarikçi Ödemesi","Altın tedarikçisi faturası", -67_300.00),
            ("09.09.2025","14:20","Kasa","Giriş","Satış Tahsilatı","İ. Şahin'e kolye - nakit", 28_600.00),
            ("09.09.2025","15:05","Banka — Ziraat","Çıkış","Masraf","Mağaza kirası ödemesi", -15_500.00),
            ("09.09.2025","15:40","Kasa","Giriş","Satış Tahsilatı","B. Aydın'a gram altın - kart", 12_300.00),
            ("09.09.2025","16:15","Kasa","Çıkış","Masraf","Çay/kahve ikramı", -120.00),
            ("09.09.2025","16:45","Banka — VakıfBank","Giriş","Müşteri Ödemesi","C. Özkan'dan havale - borç kapat", 9_200.00),
            ("09.09.2025","17:20","Kasa","Çıkış","Tedarikçi Ödemesi","Gümüş tedarikçisi ödemesi", -8_900.00),
            ("08.09.2025","16:30","Banka — Ziraat","Giriş","Satış Tahsilatı","Dünkü satışlardan havale", 55_200.00),
            ("08.09.2025","14:15","Kasa","Çıkış","Masraf","Elektrik faturası", -2_450.00),
            ("08.09.2025","11:50","Banka — VakıfBank","Çıkış","Tedarikçi Ödemesi","Altın külçe tedarikçisi", -89_400.00),
        ]
        self.table.setRowCount(len(samples))
        for i, (tarih, saat, hesap, tur, kat, ack, tut) in enumerate(samples):
            self.table.setItem(i,0, QTableWidgetItem(tarih))
            self.table.setItem(i,1, QTableWidgetItem(saat))
            self.table.setItem(i,2, QTableWidgetItem(hesap))
            self.table.setItem(i,3, QTableWidgetItem(tur))
            self.table.setItem(i,4, QTableWidgetItem(kat))
            self.table.setItem(i,5, QTableWidgetItem(ack))
            it = QTableWidgetItem(tl(abs(tut)))
            it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            # renk farkı (giriş/çıkış)
            color = QColor(120, 200, 140) if tut >= 0 else QColor(220, 120, 120)
            it.setForeground(color)
            self.table.setItem(i,6, it)

    def open_new_record_dialog(self, record_type):
        """Yeni gelir/gider kaydı için diyalog aç"""
        dialog = NewFinanceRecordDialog(self, record_type)
        if dialog.exec():
            data = dialog.data()

            # Form validasyonu
            if not data["aciklama"].strip():
                QMessageBox.warning(self, "Uyarı", "Açıklama alanı zorunludur!")
                return

            if data["tutar"] <= 0:
                QMessageBox.warning(self, "Uyarı", "Tutar 0'dan büyük olmalıdır!")
                return

            # Başarı mesajı
            QMessageBox.information(self, "Başarılı",
                                   f"{record_type} kaydı başarıyla eklendi!\n\n"
                                   f"Hesap: {data['hesap']}\n"
                                   f"Kategori: {data['kategori']}\n"
                                   f"Tutar: {tl(data['tutar'])}\n"
                                   f"Belge No: {data['belge_no']}")

            # KPI'ları güncelle
            self._update_kpis()

    def add_financial_record(self):
        """Eski metod - artık kullanılmıyor, diyalog ile değiştirildi"""
        pass

    def _clear_financial_form(self):
        """Eski metod - artık kullanılmıyor"""
        pass