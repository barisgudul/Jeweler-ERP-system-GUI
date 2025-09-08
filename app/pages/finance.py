### app/pages/finance.py ###
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QSplitter,
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView,
    QLineEdit, QComboBox, QDateEdit, QTimeEdit, QPushButton, QGroupBox, QFormLayout,
    QDoubleSpinBox, QTextEdit, QMessageBox, QDialog, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, QTime, QLocale, QTimer, QSettings
from PyQt6.QtGui import QFont, QPixmap, QPainter, QLinearGradient, QColor, QPalette, QShortcut, QKeySequence
from random import randint, choice
from theme import elevate, apply_dialog_theme
from dialogs import ExpenseVoucherDialog

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
        self.f_date.dateChanged.connect(self._refresh_state)
        self.f_time.timeChanged.connect(self._refresh_state)
        self.f_acc.currentIndexChanged.connect(self._refresh_state)
        self.f_cat.currentIndexChanged.connect(self._refresh_state)
        self.f_desc.textChanged.connect(self._refresh_state)
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
            f"Tutar: <b>{tl(self.f_amt.value())}</b> • Tarih/Saat: {self.f_date.date().toString('dd.MM.yyyy')} {self.f_time.time().toString('HH:mm')} • "
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
def _kpi(title: str, value: str, sub: str = "") -> tuple[QFrame, QLabel]:
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

    return card, val

# --- ana sayfa ----------------------------------------------------------------
class FinancePage(QWidget):
    """Kasa & Finans (frontend/mock) — kozmik tema, orantılı yerleşim"""
    def __init__(self, parent=None):
        super().__init__(parent)

        # Prefs durum bayrakları
        self._loading_prefs = False
        self._range_mode = "quick"   # "quick" | "manual"

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
        k0, _ = _kpi("Kasa Bakiyesi", tl(215_450.00), "Güncel nakit")
        k1, _ = _kpi("Banka Toplam", tl(1_485_200.00), "3 hesap aktif")
        kpi_grid.addWidget(k0, 0, 0)
        kpi_grid.addWidget(k1, 0, 1)
        k1, self.kpi_sel_in  = _kpi("Seçili Aralık Giriş", tl(0), "Tahsilat")
        k2, self.kpi_sel_out = _kpi("Seçili Aralık Çıkış", tl(0), "Ödeme & Masraf")
        k3, self.kpi_sel_net = _kpi("Net", tl(0), "Pozitif")
        kpi_grid.addWidget(k1, 0, 2)
        kpi_grid.addWidget(k2, 0, 3)
        kpi_grid.addWidget(k3, 0, 4)
        k4, _ = _kpi("Aylık Ciro", tl(2_450_000.00), "Bu ay toplam")
        k5, _ = _kpi("Bekleyen Ödeme", tl(145_800.00), "Tedarikçi borç")
        k6, _ = _kpi("Müşteri Borç", tl(89_200.00), "Aktif alacak")
        k7, _ = _kpi("Kar Marjı", "%24.8", "Brüt kar")
        k8, _ = _kpi("Günlük Hedef", tl(100_000.00), "Hedefe ulaştı")
        kpi_grid.addWidget(k4, 1, 0)
        kpi_grid.addWidget(k5, 1, 1)
        kpi_grid.addWidget(k6, 1, 2)
        kpi_grid.addWidget(k7, 1, 3)
        kpi_grid.addWidget(k8, 1, 4)
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

        self.dt_from = QDateEdit(QDate(2025, 1, 1))  # 2025 başı
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

        self.dt_to = QDateEdit(QDate(2025, 12, 31))  # 2025 sonu
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
        self.cmb_quick.addItems(["Son 7 gün", "Eylül 2025", "Ağustos 2025", "2025 Yılı"])
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

        # Filtre sinyalleri - canlı güncelleme
        self.e_search.textChanged.connect(self._refresh_table)
        self.cmb_account.currentIndexChanged.connect(self._refresh_table)
        self.cmb_type.currentIndexChanged.connect(self._refresh_table)
        self.dt_from.dateChanged.connect(self._refresh_table)
        self.dt_to.dateChanged.connect(self._refresh_table)

        # Kaydetme bağlantıları
        self.e_search.textChanged.connect(self._save_prefs)
        self.cmb_account.currentIndexChanged.connect(self._save_prefs)
        self.cmb_type.currentIndexChanged.connect(self._save_prefs)

        # Tarihler—manuel moda geçsin
        self.dt_from.dateChanged.connect(lambda *_: self._mark_manual_and_save())
        self.dt_to.dateChanged.connect(lambda *_: self._mark_manual_and_save())

        # Hızlı aralık seçilince quick moda geçsin
        self.cmb_quick.currentIndexChanged.connect(lambda *_: self._mark_quick_and_save())

        # Splitter ve sıralama değişimleri - splitter oluşturulduktan sonra bağlanacak

        # İkinci satır: Export butonları
        bottom_filter_row = QHBoxLayout()
        bottom_filter_row.setSpacing(8)

        self.btn_export_xls = QPushButton("Excel'e Aktar")
        self.btn_export_xls.setEnabled(True)
        self.btn_export_xls.setToolTip("Filtrelenmiş kayıtları Excel olarak aktar")
        self.btn_export_pdf = QPushButton("PDF'e Aktar")
        self.btn_export_pdf.setEnabled(True)
        self.btn_export_pdf.setToolTip("Filtrelenmiş kayıtları PDF olarak aktar")

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
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setHandleWidth(8)

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
        self.table.setSortingEnabled(True)
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

        # --- dahili defter veri modeli
        self._rows: list[dict] = []    # {id,tarih,saat,hesap,tur,kategori,aciklama,tutar}
        self._seq = 1  # benzersiz id sayacı

        self.splitter.addWidget(left)
        self.splitter.setStretchFactor(0, 1)

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

        # mock satırlar - etiketlerden sonra yükle
        self._load_mock_rows()

        # --- 2. İşlemler Grubu (GRID DÜZENİ) ---
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

        actions_grid = QGridLayout(actions_group)
        actions_grid.setContentsMargins(8, 8, 8, 8)
        actions_grid.setHorizontalSpacing(8)
        actions_grid.setVerticalSpacing(8)

        # 1. satır: Yeni Gelir | Yeni Gider
        self.btn_new_income  = self._action_btn("Yeni Gelir",  "success")
        self.btn_new_income.setToolTip("Yeni gelir kaydı oluştur")
        self.btn_new_expense = self._action_btn("Yeni Gider",  "danger")
        self.btn_new_expense.setToolTip("Yeni gider kaydı oluştur")

        # 2. satır: tam genişlik Gider Pusulası
        self.btn_expense_voucher = self._action_btn("Gider Pusulası", "warning")
        self.btn_expense_voucher.setToolTip("Yeni gider pusulası oluştur")
        self.btn_expense_voucher.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # 3. satır: Düzenle | Sil
        self.btn_edit = self._action_btn("Düzenle", "neutral"); self.btn_edit.setEnabled(False)
        self.btn_edit.setToolTip("Seçili kaydı düzenle")
        self.btn_del  = self._action_btn("Sil",     "neutral"); self.btn_del.setEnabled(False)
        self.btn_del.setToolTip("Seçili kaydı sil")

        # yerleşim
        actions_grid.addWidget(self.btn_new_income,      0, 0)
        actions_grid.addWidget(self.btn_new_expense,     0, 1)
        actions_grid.addWidget(self.btn_expense_voucher, 1, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        actions_grid.addWidget(self.btn_edit,            2, 0)
        actions_grid.addWidget(self.btn_del,             2, 1)

        # sütunlar eşit genişlikte yayılsın
        actions_grid.setColumnStretch(0, 1)
        actions_grid.setColumnStretch(1, 1)

        actions_group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        # --- SAĞ PANEL YERLEŞİMİ ---
        rv.addWidget(box_sum)
        rv.addWidget(actions_group)
        rv.addStretch(1) # Boşluğu en alta it

        # Buton bağlantıları
        self.btn_new_income.clicked.connect(lambda: self.open_new_record_dialog("Giriş"))
        self.btn_new_expense.clicked.connect(lambda: self.open_new_record_dialog("Çıkış"))
        self.btn_expense_voucher.clicked.connect(self.open_expense_voucher)

        self.btn_edit.clicked.connect(self._edit_selected)
        self.btn_del.clicked.connect(self._delete_selected)
        self.table.itemDoubleClicked.connect(lambda _: self._edit_selected())
        QShortcut(QKeySequence.StandardKey.Delete, self, activated=self._delete_selected)  # Delete tuşu ile sil

        self.btn_export_xls.clicked.connect(self._export_excel)
        self.btn_export_pdf.clicked.connect(self._export_pdf)

        # not - Not kutusu
        note = QTextEdit(readOnly=True)
        note.setPlainText(
            "Not: Kasa Defteri tam işlevsel!\n"
            "• Satır seç + Düzenle/Sil butonları\n"
            "• Çift tıklama veya Delete tuşu ile hızlı işlemler\n"
            "• Tablo sıralaması aktif\n"
            "• Filtreler + Dışa Aktar özellikleri çalışıyor"
        )
        note.setStyleSheet("""
            QTextEdit {
                background: rgba(20,26,48,0.6); border: 1px solid rgba(255,255,255,0.08);
                border-radius: 8px; color: #B7C0CC; font-size: 11px; padding: 8px;
            }
        """)
        note.setMaximumHeight(80)
        rv.addWidget(note)

        right.setMinimumWidth(360)
        right.setMaximumWidth(420)
        self.splitter.addWidget(right)

        root.addWidget(self.splitter, 1)

        # Splitter ve sıralama bağlantıları - artık güvenli
        self.splitter.splitterMoved.connect(lambda *_: self._save_prefs())
        self.table.horizontalHeader().sortIndicatorChanged.connect(lambda *_: self._save_prefs())

        # ilk oran
        QTimer.singleShot(0, lambda: self.splitter.setSizes([self.width()-360, 360]))
        QTimer.singleShot(0, lambda: self._paint_sky(self.width(), self.height()))
        QTimer.singleShot(0, self._load_prefs)

    # FinancePage içinde
    def _action_btn(self, text: str, variant: str = "neutral") -> QPushButton:
        """
        Yüksek kontrastlı, tema-uyumlu işlem butonu üretir.
        variant: success | danger | warning | neutral
        """
        btn = QPushButton(text)
        btn.setMinimumHeight(44)
        btn.setMinimumWidth(130)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Eğer theme.py bir stil fonksiyonu sağlıyorsa onu kullan
        try:
            from theme import style_button  # opsiyonel
            style_button(btn, variant)
            return btn
        except Exception:
            pass

        # Fallback: yüksek kontrast QSS
        if variant == "success":
            qss = """
            QPushButton {
                padding: 10px; border-radius: 10px;
                background: #2e7d32; color: #FFFFFF;
                border: 1px solid #43a047; font-weight: 600;
            }
            QPushButton:hover { background: #388e3c; }
            QPushButton:pressed { background: #1b5e20; }
            """
        elif variant == "danger":
            qss = """
            QPushButton {
                padding: 10px; border-radius: 10px;
                background: #c62828; color: #FFFFFF;
                border: 1px solid #ef5350; font-weight: 600;
            }
            QPushButton:hover { background: #d32f2f; }
            QPushButton:pressed { background: #8e0000; }
            """
        elif variant == "warning":
            qss = """
            QPushButton {
                padding: 10px; border-radius: 10px;
                background: #ffb300; color: #0b0f16;  /* sarıda koyu metin */
                border: 1px solid #ffa000; font-weight: 700;
            }
            QPushButton:hover { background: #ffca28; }
            QPushButton:pressed { background: #ff8f00; color: #0b0f16; }
            """
        else:  # neutral
            qss = """
            QPushButton {
                padding: 10px; border-radius: 10px;
                background: rgba(255,255,255,0.06); color: #E9EDF2;
                border: 1px solid rgba(255,255,255,0.12); font-weight: 600;
            }
            QPushButton:hover { background: rgba(255,255,255,0.10); }
            QPushButton:pressed { background: rgba(255,255,255,0.16); }
            """
        btn.setStyleSheet(qss)
        return btn

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
        if txt == "Son 7 gün":
            # Örnek verilerin tarihi: 09.09.2025
            base_date = QDate(2025, 9, 9)
            self.dt_to.setDate(base_date)
            self.dt_from.setDate(base_date.addDays(-7))
        elif txt == "Eylül 2025":
            # Eylül 2025
            self.dt_from.setDate(QDate(2025, 9, 1))
            self.dt_to.setDate(QDate(2025, 9, 30))
        elif txt == "Ağustos 2025":
            # Ağustos 2025
            self.dt_from.setDate(QDate(2025, 8, 1))
            self.dt_to.setDate(QDate(2025, 8, 31))
        elif txt == "2025 Yılı":
            # 2025 başından Eylül sonuna
            self.dt_from.setDate(QDate(2025, 1, 1))
            self.dt_to.setDate(QDate(2025, 9, 30))

    def _update_kpis(self):
        rows = getattr(self, "_visible_cache", [])
        total_in  = sum(r["tutar"] for r in rows if r["tutar"] > 0)
        total_out = -sum(r["tutar"] for r in rows if r["tutar"] < 0)
        net = total_in - total_out
        self.lbl_sum_in.setText(tl(total_in))
        self.lbl_sum_out.setText(tl(total_out))
        self.lbl_sum_net.setText(tl(net))

    def _toggle_right_actions(self):
        sm = self.table.selectionModel()
        has = bool(sm and sm.selectedRows())
        self.btn_edit.setEnabled(has)
        self.btn_del.setEnabled(has)

    def _load_mock_rows(self):
        samples = [
            ("09.09.2025","09:15","Kasa","Giriş","Satış Tahsilatı","A. Yılmaz'a 22A bilezik satışı - nakit", 25400.00),
            ("09.09.2025","09:45","Banka — VakıfBank","Giriş","Müşteri Ödemesi","M. Demir'den havale - borç kapat", 18750.00),
            ("09.09.2025","10:30","Kasa","Giriş","Satış Tahsilatı","Z. Arslan'a küpe seti - kart", 45900.00),
            ("09.09.2025","11:20","Banka — Ziraat","Giriş","Müşteri Ödemesi","E. Korkmaz'dan EFT - altın borç", 32500.00),
            ("09.09.2025","12:10","Kasa","Çıkış","Masraf","Kırtasiye malzemeleri", -850.00),
            ("09.09.2025","13:45","Banka — VakıfBank","Çıkış","Tedarikçi Ödemesi","Altın tedarikçisi faturası", -67300.00),
            ("09.09.2025","14:20","Kasa","Giriş","Satış Tahsilatı","İ. Şahin'e kolye - nakit", 28600.00),
            ("09.09.2025","15:05","Banka — Ziraat","Çıkış","Masraf","Mağaza kirası ödemesi", -15500.00),
            ("09.09.2025","15:40","Kasa","Giriş","Satış Tahsilatı","B. Aydın'a gram altın - kart", 12300.00),
            ("09.09.2025","16:15","Kasa","Çıkış","Masraf","Çay/kahve ikramı", -120.00),
            ("09.09.2025","16:45","Banka — VakıfBank","Giriş","Müşteri Ödemesi","C. Özkan'dan havale - borç kapat", 9200.00),
            ("09.09.2025","17:20","Kasa","Çıkış","Tedarikçi Ödemesi","Gümüş tedarikçisi ödemesi", -8900.00),
            ("08.09.2025","16:30","Banka — Ziraat","Giriş","Satış Tahsilatı","Dünkü satışlardan havale", 55200.00),
            ("08.09.2025","14:15","Kasa","Çıkış","Masraf","Elektrik faturası", -2450.00),
            ("08.09.2025","11:50","Banka — VakıfBank","Çıkış","Tedarikçi Ödemesi","Altın külçe tedarikçisi", -89400.00),
        ]
        self._rows = []
        for (t,s,h,tur,k,a,v) in samples:
            self._rows.append({
                "id": self._seq, "tarih": t, "saat": s,
                "hesap": h, "tur": tur, "kategori": k,
                "aciklama": a, "tutar": v
            })
            self._seq += 1
        self._refresh_table()   # tabloyu ve özeti ilk kez çiz

    def _pass_filters(self, r: dict) -> bool:
        # tarih
        d = QDate.fromString(r["tarih"], "dd.MM.yyyy")
        if d.isValid():
            if d < self.dt_from.date() or d > self.dt_to.date():
                return False
        # tür
        t = self.cmb_type.currentText()
        if t != "Tümü" and r["tur"] != t:
            return False
        # hesap
        h = self.cmb_account.currentText()
        if h != "Tüm Hesaplar" and r["hesap"] != h:
            return False
        # arama
        q = self.e_search.text().strip().lower()
        if q:
            hay = (r["aciklama"] + " " + r["kategori"] + " " + r["hesap"]).lower()
            if q not in hay:
                return False
        return True

    def _refresh_table(self):
        # Tablo sıralamasını geçici olarak kapat (veri yükleme sırasında)
        sorting_enabled = self.table.isSortingEnabled()
        if sorting_enabled:
            self.table.setSortingEnabled(False)

        # filtrelerden geçen kayıtları topla
        vis = [r for r in self._rows if self._pass_filters(r)]
        self.table.setRowCount(len(vis))

        for i, r in enumerate(vis):
            it_date = QTableWidgetItem(r["tarih"])
            it_date.setData(Qt.ItemDataRole.UserRole, r["id"])
            self.table.setItem(i, 0, it_date)
            self.table.setItem(i, 1, QTableWidgetItem(r["saat"]))
            self.table.setItem(i, 2, QTableWidgetItem(r["hesap"]))
            self.table.setItem(i, 3, QTableWidgetItem(r["tur"]))
            self.table.setItem(i, 4, QTableWidgetItem(r["kategori"]))
            self.table.setItem(i, 5, QTableWidgetItem(r["aciklama"]))
            it = QTableWidgetItem(tl(abs(r["tutar"])))
            it.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            it.setForeground(QColor(120,200,140) if r["tutar"] >= 0 else QColor(220,120,120))
            self.table.setItem(i, 6, it)

        self._visible_cache = vis
        self._recalc_summary(vis)

        # Sıralamayı geri aç
        if sorting_enabled:
            self.table.setSortingEnabled(True)

    def _recalc_summary(self, rows: list[dict]):
        total_in  = sum(r["tutar"] for r in rows if r["tutar"] > 0)
        total_out = -sum(r["tutar"] for r in rows if r["tutar"] < 0)
        net = total_in - total_out
        self.lbl_sum_in.setText(tl(total_in))
        self.lbl_sum_out.setText(tl(total_out))
        self.lbl_sum_net.setText(tl(net))

        # Üst KPI'ları da güncelle
        if hasattr(self, "kpi_sel_in"):
            self.kpi_sel_in.setText(tl(total_in))
        if hasattr(self, "kpi_sel_out"):
            self.kpi_sel_out.setText(tl(total_out))
        if hasattr(self, "kpi_sel_net"):
            self.kpi_sel_net.setText(tl(net))


    def _selected_row_id(self):
        sel = self.table.selectionModel().selectedRows()
        if not sel: return None
        row = sel[0].row()
        it = self.table.item(row, 0)
        return it.data(Qt.ItemDataRole.UserRole) if it else None

    def _find_row_index_by_id(self, rid: int) -> int:
        for i, r in enumerate(self._rows):
            if r.get("id") == rid:
                return i
        return -1

    def _select_id_in_table(self, rid: int):
        # Önce tabloyu sıralamasız moda al (sıralama bozulmasın)
        sorting_enabled = self.table.isSortingEnabled()
        if sorting_enabled:
            self.table.setSortingEnabled(False)

        # Görünür satırlarda ara
        if hasattr(self, "_visible_cache"):
            for idx, rec in enumerate(self._visible_cache):
                if rec.get("id") == rid:
                    self.table.setCurrentCell(idx, 0)
                    break

        # Sıralamayı geri aç
        if sorting_enabled:
            self.table.setSortingEnabled(True)

    def _edit_selected(self):
        rid = self._selected_row_id()
        if rid is None: return
        i = self._find_row_index_by_id(rid)
        if i < 0: return

        rec = self._rows[i]
        dlg = NewFinanceRecordDialog(self, rec["tur"])

        # mevcut verilerle doldur
        dlg.f_date.setDate(QDate.fromString(rec["tarih"], "dd.MM.yyyy"))
        dlg.f_time.setTime(QTime.fromString(rec["saat"], "HH:mm"))
        dlg.f_acc.setCurrentText(rec["hesap"])
        if dlg.f_cat.findText(rec["kategori"]) == -1:
            dlg.f_cat.addItem(rec["kategori"])
        dlg.f_cat.setCurrentText(rec["kategori"])
        dlg.f_desc.setPlainText(rec["aciklama"])
        dlg.f_amt.setValue(abs(float(rec["tutar"])))
        dlg._refresh_state()

        if dlg.exec():
            data = dlg.data()
            if not data["aciklama"].strip() or data["tutar"] <= 0:
                QMessageBox.warning(self, "Uyarı", "Tutar > 0 ve açıklama zorunlu.")
                return

            rec.update({
                "tarih": data["tarih"],
                "saat":  data["saat"],
                "hesap": data["hesap"],
                "tur":   data["tur"],
                "kategori": data["kategori"],
                "aciklama": data["aciklama"],
                "tutar":  data["tutar"] if data["tur"] == "Giriş" else -data["tutar"],
            })
            self._refresh_table()
            # Kısa bekletme ile tablonun güncellenmesini bekle
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(50, lambda: self._select_id_in_table(rid))
            QMessageBox.information(self, "Güncellendi", "Kayıt başarıyla güncellendi.")

    def _delete_selected(self):
        rid = self._selected_row_id()
        if rid is None: return

        # Hedef satırın görünür listedeki indeksini bul
        next_index = 0
        if hasattr(self, "_visible_cache"):
            for i, rec in enumerate(self._visible_cache):
                if rec["id"] == rid:
                    next_index = min(i, len(self._visible_cache)-2)  # bir sonrasına hizala
                    break

        btn = QMessageBox.question(
            self, "Sil", "Seçili kaydı silmek istiyor musun?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if btn != QMessageBox.StandardButton.Yes:
            return

        self._rows = [r for r in self._rows if r.get("id") != rid]
        self._refresh_table()

        # Sonraki satırı seç
        if self._visible_cache:
            self._select_id_in_table(self._visible_cache[max(next_index,0)]["id"])

        QMessageBox.information(self, "Silindi", "Kayıt başarıyla silindi.")

    def open_new_record_dialog(self, record_type):
        dlg = NewFinanceRecordDialog(self, record_type)
        if dlg.exec():
            data = dlg.data()
            if not data["aciklama"].strip() or data["tutar"] <= 0:
                QMessageBox.warning(self, "Uyarı", "Tutar > 0 ve açıklama zorunlu.")
                return

            # modele ekle
            self._rows.append({
                "id": self._seq,
                "tarih": data["tarih"],
                "saat":  data["saat"],
                "hesap": data["hesap"],
                "tur":   data["tur"],
                "kategori": data["kategori"],
                "aciklama": data["aciklama"],
                "tutar":  data["tutar"] if record_type=="Giriş" else -data["tutar"],
            })
            self._seq += 1
            self._refresh_table()

            QMessageBox.information(self, "Kaydedildi",
                f"{record_type} kaydı eklendi.\nTutar: {tl(data['tutar'])} • Belge No: {data['belge_no']}")

    def open_expense_voucher(self):
        dlg = ExpenseVoucherDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.data()
            self._rows.append({
                "id": self._seq, "tarih": d["date"],
                "saat": QTime.currentTime().toString("HH:mm"),
                "hesap": "Kasa", "tur": "Çıkış", "kategori": "Masraf",
                "aciklama": f"Gider Pusulası — {d['mahi']} ({d['cins']})",
                "tutar": -float(d["tutar"]),
            })
            self._seq += 1
            self._refresh_table()
            QMessageBox.information(self, "Gider Pusulası", f"Kayıt eklendi. Tutar: {tl(d['tutar'])}")

    def _export_excel(self):
        rows = getattr(self, "_visible_cache", [])
        if not rows:
            QMessageBox.information(self, "Dışa Aktar", "Aktarılacak kayıt yok.")
            return

        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, "Excel olarak kaydet", self._last_path("exportExcel", "finans_kasa.xlsx"),
            "Excel (*.xlsx);;CSV (*.csv)"
        )
        if not path:
            return

        try:
            # .xlsx tercih; kütüphane yoksa .csv'ye düş
            if path.lower().endswith(".csv"):
                raise ImportError("csv requested")  # doğrudan csv yaz
            import xlsxwriter  # type: ignore

            wb   = xlsxwriter.Workbook(path)
            ws   = wb.add_worksheet("KasaDefteri")
            fmt_h = wb.add_format({"bold": True, "bg_color": "#E8EEF9", "border": 1})
            fmt_tl_pos = wb.add_format({"num_format": u'[$-tr-TR]₺ #,##0.00;[Red]-[$-tr-TR]₺ #,##0.00', "border": 1})
            fmt_txt = wb.add_format({"border": 1})

            headers = ["Tarih","Saat","Hesap","Tür","Kategori","Açıklama","Tutar"]
            for c, h in enumerate(headers): ws.write(0, c, h, fmt_h)

            for r, rec in enumerate(rows, start=1):
                ws.write(r, 0, rec["tarih"], fmt_txt)
                ws.write(r, 1, rec["saat"],  fmt_txt)
                ws.write(r, 2, rec["hesap"], fmt_txt)
                ws.write(r, 3, rec["tur"],   fmt_txt)
                ws.write(r, 4, rec["kategori"], fmt_txt)
                ws.write(r, 5, rec["aciklama"], fmt_txt)
                ws.write_number(r, 6, float(rec["tutar"]), fmt_tl_pos)

            ws.autofilter(0, 0, len(rows), len(headers)-1)
            ws.freeze_panes(1, 0)
            ws.set_column(0, 0, 12)  # Tarih
            ws.set_column(1, 1, 8)   # Saat
            ws.set_column(2, 2, 20)  # Hesap
            ws.set_column(3, 4, 14)  # Tür/Kategori
            ws.set_column(5, 5, 36)  # Açıklama
            ws.set_column(6, 6, 14)  # Tutar
            wb.close()

        except Exception as e:
            try:
                # Basit CSV fallback
                import csv
                if not path.lower().endswith(".csv"):
                    path += ".csv"
                headers = ["Tarih","Saat","Hesap","Tür","Kategori","Açıklama","Tutar"]
                with open(path, "w", newline="", encoding="utf-8-sig") as f:
                    w = csv.writer(f, delimiter=";")
                    w.writerow(headers)
                    for rec in rows:
                        tutar = f"{rec['tutar']:.2f}".replace(".", ",")  # TR uyumlu
                        w.writerow([rec["tarih"], rec["saat"], rec["hesap"], rec["tur"],
                                    rec["kategori"], rec["aciklama"], tutar])
            except Exception as e2:
                QMessageBox.critical(self, "Dışa Aktar", f"Kaydetme başarısız:\n{e2}")
                return

        self._store_path("exportExcel", path)
        QMessageBox.information(self, "Dışa Aktar", "Dosya kaydedildi.")

    def _export_pdf(self):
        rows = getattr(self, "_visible_cache", [])
        if not rows:
            QMessageBox.information(self, "Dışa Aktar", "Aktarılacak kayıt yok.")
            return

        from PyQt6.QtWidgets import QFileDialog
        from PyQt6.QtGui import QTextDocument
        from PyQt6.QtPrintSupport import QPrinter

        path, _ = QFileDialog.getSaveFileName(
            self, "PDF olarak kaydet", self._last_path("exportPdf", "finans_kasa.pdf"), "PDF (*.pdf)"
        )
        if not path:
            return

        try:
            # Para biçimi yardımcıları
            def tl_abs(v: float) -> str:
                return TR.toCurrencyString(abs(v), "₺").replace("\u00a0"," ")

            def tl_signed(v: float) -> str:
                return TR.toCurrencyString(v, "₺").replace("\u00a0"," ")

            rows_html = "\n".join([
                f"<tr>"
                f"<td>{r['tarih']}</td><td>{r['saat']}</td><td>{r['hesap']}</td>"
                f"<td>{r['tur']}</td><td>{r['kategori']}</td><td>{r['aciklama']}</td>"
                f"<td class='r' style='color:{'#4CAF50' if r['tutar']>=0 else '#E53935'};'>{tl_abs(r['tutar'])}</td>"
                f"</tr>"
                for r in rows
            ])

            html = f"""
            <style>
              body {{ font-family: -apple-system, Segoe UI, Roboto, Arial; font-size: 11pt; }}
              table {{ border-collapse: collapse; width: 100%; }}
              th, td {{ border: 1px solid #999; padding: 6px; vertical-align: top; }}
              thead th {{ background: #e8eef9; }}
              .r {{ text-align: right; }}
              h2 {{ margin: 0 0 8px 0; }}
              .meta {{ color:#555; margin-bottom: 10px; }}
            </style>
            <h2>Kasa Defteri</h2>
            <div class="meta">Tarih Aralığı: {self.dt_from.date().toString('dd.MM.yyyy')} – {self.dt_to.date().toString('dd.MM.yyyy')}</div>
            <table>
              <thead>
                <tr>
                  <th>Tarih</th><th>Saat</th><th>Hesap</th><th>Tür</th><th>Kategori</th><th>Açıklama</th><th class='r'>Tutar</th>
                </tr>
              </thead>
              <tbody>
                {rows_html}
              </tbody>
            </table>
            <br/>
            # Toplam hesaplamaları
            total_in  = sum(r['tutar'] for r in rows if r['tutar'] > 0)
            total_out = -sum(r['tutar'] for r in rows if r['tutar'] < 0)
            net       = sum(r['tutar'] for r in rows)

            <table>
              <tr><td><b>Toplam Giriş</b></td><td class='r'>{tl_abs(total_in)}</td></tr>
              <tr><td><b>Toplam Çıkış</b></td><td class='r'>{tl_abs(total_out)}</td></tr>
              <tr><td><b>Net</b></td><td class='r'>{tl_signed(net)}</td></tr>
            </table>
            """

            doc = QTextDocument(); doc.setHtml(html)
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(path)
            doc.print(printer)

            self._store_path("exportPdf", path)
            QMessageBox.information(self, "Dışa Aktar", "PDF kaydedildi.")

        except Exception as e:
            QMessageBox.critical(self, "Dışa Aktar", f"PDF oluşturma başarısız:\n{e}")

    def add_financial_record(self):
        """Eski metod - artık kullanılmıyor, diyalog ile değiştirildi"""
        pass

    def _clear_financial_form(self):
        """Eski metod - artık kullanılmıyor"""
        pass

    def _prefs(self) -> QSettings:
        return QSettings("OrbitX", "KuyumcuERP")

    def _last_path(self, key, default_name):
        s = self._prefs(); s.beginGroup("paths")
        p = s.value(key, default_name); s.endGroup(); return p

    def _store_path(self, key, path):
        s = self._prefs(); s.beginGroup("paths")
        s.setValue(key, path); s.endGroup()

    def _mark_manual_and_save(self):
        if self._loading_prefs: return
        self._range_mode = "manual"
        self._save_prefs()

    def _mark_quick_and_save(self):
        if self._loading_prefs: return
        self._range_mode = "quick"
        self._save_prefs()

    def _save_prefs(self):
        if self._loading_prefs: return
        s = self._prefs()
        s.beginGroup("finance")
        s.setValue("search", self.e_search.text())
        s.setValue("account", self.cmb_account.currentText())
        s.setValue("type", self.cmb_type.currentText())
        s.setValue("from", self.dt_from.date().toString(Qt.DateFormat.ISODate))
        s.setValue("to", self.dt_to.date().toString(Qt.DateFormat.ISODate))
        s.setValue("rangeMode", self._range_mode)                  # "quick" | "manual"
        s.setValue("quickIndex", self.cmb_quick.currentIndex())
        s.setValue("splitter", self.splitter.sizes())
        hdr = self.table.horizontalHeader()
        s.setValue("sortCol", hdr.sortIndicatorSection())
        s.setValue("sortOrder", hdr.sortIndicatorOrder().value)
        s.endGroup()

    def _load_prefs(self):
        self._loading_prefs = True
        s = self._prefs()
        s.beginGroup("finance")

        # Text & combolar
        self.e_search.setText(s.value("search", ""))
        self.cmb_account.setCurrentText(s.value("account", "Tüm Hesaplar"))
        self.cmb_type.setCurrentText(s.value("type", "Tümü"))

        # Tarihler
        from_str = s.value("from", "")
        to_str   = s.value("to", "")
        if from_str:
            self.dt_from.setDate(QDate.fromString(from_str, Qt.DateFormat.ISODate))
        if to_str:
            self.dt_to.setDate(QDate.fromString(to_str, Qt.DateFormat.ISODate))

        # Aralık modu & hızlı aralık
        self._range_mode = s.value("rangeMode", "quick")
        qi = int(s.value("quickIndex", 0))
        if self._range_mode == "quick":
            self.cmb_quick.setCurrentIndex(qi)   # _apply_quick_range tetiklenir

        # Splitter oranları
        sizes = s.value("splitter", None)
        if sizes:
            try:
                self.splitter.setSizes([int(x) for x in list(sizes)])
            except Exception:
                pass

        # Sıralama
        sortCol   = int(s.value("sortCol", 0))
        sortOrder = int(s.value("sortOrder", 0))  # 0 = AscendingOrder, 1 = DescendingOrder
        self.table.horizontalHeader().setSortIndicator(sortCol, Qt.SortOrder(sortOrder))

        s.endGroup()
        self._loading_prefs = False

        # Görünümü güncelle
        self._refresh_table()