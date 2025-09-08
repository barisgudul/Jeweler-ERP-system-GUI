# app/pages/dashboard.py
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QFrame, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, QLocale, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter, QLinearGradient, QColor
from random import uniform, randint
from theme import elevate  # gölge için

TR = QLocale(QLocale.Language.Turkish, QLocale.Country.Turkey)

def fmt_currency(value: float) -> str:
    # Yerel biçimlendirme + ₺, ince boşluklar
    return TR.toCurrencyString(value, "₺")

def kpi_card(title: str, value: str, subtitle: str = "") -> QFrame:
    card = QFrame()
    card.setObjectName("Glass")  # Cam efektli kart
    v = QVBoxLayout(card)
    v.setContentsMargins(20, 20, 20, 20)
    v.setSpacing(12)

    t = QLabel(title)
    t.setProperty("variant", "title")
    v.addWidget(t)

    val = QLabel(value)
    f = QFont("Segoe UI", 26)
    f.setWeight(QFont.Weight.ExtraBold)
    val.setFont(f)
    v.addWidget(val)

    if subtitle:
        sub = QLabel(subtitle)
        sub.setProperty("variant", "muted")
        v.addWidget(sub)

    v.addStretch(1)
    elevate(card,scheme="dim", blur=32, y=10)  # Daha güçlü gölge
    return card

class DashboardPage(QWidget):
    quick_action_triggered = pyqtSignal(dict)  # Sayfa değiştirme sinyali

    def __init__(self, parent=None):
        super().__init__(parent)

        # === KOZMİK ARKA PLAN ===
        self._sky = QLabel(self)
        self._sky.lower()  # en arkada dursun
        self._sky.setScaledContents(True)
        self._sky.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        # — Üst başlık
        header = QHBoxLayout()
        title = QLabel("Dashboard")
        tf = QFont("Segoe UI", 18, QFont.Weight.Bold)
        title.setFont(tf)
        header.addWidget(title, 0, Qt.AlignmentFlag.AlignLeft)

        hint = QLabel("Güncel göstergeler • canlı mock veri")
        hint.setProperty("variant", "muted")
        header.addWidget(hint, 0, Qt.AlignmentFlag.AlignRight)
        root.addLayout(header)

        # Ana layout'u iki sütunlu yapalım
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)

        # === Sol Sütun: KPI'lar ve Mini Listeler ===
        left_column = QVBoxLayout()
        left_column.setSpacing(16)

        # Üst KPI'lar - 2x3 grid
        kpi_grid = QGridLayout()
        kpi_grid.setHorizontalSpacing(12)
        kpi_grid.setVerticalSpacing(12)

        # Mock değerler
        gram = round(uniform(2500, 2700), 2)
        satis = round(uniform(150000, 350000), 2)
        stok = round(uniform(2000000, 3500000), 2)
        aylik_ciro = round(uniform(2000000, 4000000), 2)
        bekleyen_odeme = round(uniform(50000, 150000), 2)
        kritik_stok = randint(3, 8)

        kpi_grid.addWidget(kpi_card("Gram Altın", fmt_currency(gram), "Anlık gram fiyatı"), 0, 0)
        kpi_grid.addWidget(kpi_card("Günlük Satış", fmt_currency(satis), "Bugünün toplam işlemleri"), 0, 1)
        kpi_grid.addWidget(kpi_card("Toplam Stok Değeri", fmt_currency(stok), "Stoktaki varlıkların değeri"), 0, 2)
        kpi_grid.addWidget(kpi_card("Aylık Ciro", fmt_currency(aylik_ciro), "Bu ay toplam satış"), 1, 0)
        kpi_grid.addWidget(kpi_card("Bekleyen Ödeme", fmt_currency(bekleyen_odeme), "Tedarikçi borçları"), 1, 1)
        kpi_grid.addWidget(kpi_card("Kritik Stok", f"{kritik_stok} ürün", "Düşük stok seviyesi"), 1, 2)

        for c in range(3):
            kpi_grid.setColumnStretch(c, 1)

        left_column.addLayout(kpi_grid)

        # Kritik Stok Listesi
        critical_stock_card = QFrame(objectName="Glass")
        critical_stock_card.setMinimumHeight(200)
        elevate(critical_stock_card, "dim", blur=24, y=6)
        critical_layout = QVBoxLayout(critical_stock_card)
        critical_layout.setContentsMargins(16, 16, 16, 16)

        critical_title = QLabel("Kritik Stok Seviyesi")
        critical_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        critical_title.setStyleSheet("color: #E9EDF2; margin-bottom: 8px;")
        critical_layout.addWidget(critical_title)

        # Mock kritik ürünler
        critical_items = [
            ("Bilezik 22A", "2 adet"),
            ("Kolye 18A", "1 adet"),
            ("Yüzük 22A", "3 adet"),
            ("Külçe 5gr", "2 adet")
        ]

        for item_name, stock in critical_items:
            item_label = QLabel(f"• {item_name}: {stock}")
            item_label.setStyleSheet("color: #F44336; font-size: 12px; margin: 2px 0px;")
            critical_layout.addWidget(item_label)

        critical_layout.addStretch(1)
        left_column.addWidget(critical_stock_card)

        left_column.addStretch(1)
        main_layout.addLayout(left_column, 2)  # Sol sütun daha geniş

        # === Sağ Sütun: Hızlı Erişim ve Son İşlemler ===
        right_column = QVBoxLayout()
        right_column.setSpacing(16)

        # Hızlı Erişim Kartı
        quick_access_card = QFrame(objectName="Glass")
        quick_access_card.setMinimumHeight(200)
        elevate(quick_access_card, "dim", blur=24, y=6)
        quick_layout = QVBoxLayout(quick_access_card)
        quick_layout.setContentsMargins(16, 16, 16, 16)

        quick_title = QLabel("Hızlı Erişim")
        quick_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        quick_title.setStyleSheet("color: #E9EDF2; margin-bottom: 12px;")
        quick_layout.addWidget(quick_title)

        # Hızlı erişim butonları
        btn_new_sale = QPushButton("Yeni Satış İşlemi")
        btn_new_customer = QPushButton("Yeni Müşteri Ekle")
        btn_new_stock = QPushButton("Yeni Stok Girişi")
        btn_reports = QPushButton("Raporlar")

        # Butonları sinyale bağla
        btn_new_sale.clicked.connect(lambda: self.quick_action_triggered.emit({'route': 'sales', 'action': 'new'}))
        btn_new_customer.clicked.connect(lambda: self.quick_action_triggered.emit({'route': 'customers', 'action': 'new'}))
        btn_new_stock.clicked.connect(lambda: self.quick_action_triggered.emit({'route': 'stock', 'action': 'new'}))
        btn_reports.clicked.connect(lambda: self.quick_action_triggered.emit({'route': 'reports', 'action': 'view'}))

        # Buton stilleri
        button_style = """
            QPushButton {
                padding: 12px 16px;
                border-radius: 10px;
                background: rgba(76,125,255,0.1);
                border: 2px solid rgba(76,125,255,0.3);
                color: #E9EDF2;
                font-size: 13px;
                font-weight: 600;
                margin: 4px 0px;
                text-align: left;
            }
            QPushButton:hover {
                border-color: #97B7FF;
                background: rgba(76,125,255,0.2);
                color: #F1F4F8;
            }
            QPushButton:pressed {
                background: rgba(76,125,255,0.3);
            }
        """

        for btn in [btn_new_sale, btn_new_customer, btn_new_stock, btn_reports]:
            btn.setStyleSheet(button_style)
            btn.setMinimumHeight(45)
            quick_layout.addWidget(btn)

        right_column.addWidget(quick_access_card)

        # Son İşlemler Listesi
        recent_transactions_card = QFrame(objectName="Glass")
        recent_transactions_card.setMinimumHeight(250)
        elevate(recent_transactions_card, "dim", blur=24, y=6)
        recent_layout = QVBoxLayout(recent_transactions_card)
        recent_layout.setContentsMargins(16, 16, 16, 16)

        recent_title = QLabel("Son İşlemler")
        recent_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        recent_title.setStyleSheet("color: #E9EDF2; margin-bottom: 8px;")
        recent_layout.addWidget(recent_title)

        # Mock son işlemler
        recent_items = [
            ("14:30 - Ahmet Yılmaz", "22A Bilezik Satışı", fmt_currency(25600)),
            ("13:45 - Mehmet Demir", "18A Kolye Satışı", fmt_currency(18900)),
            ("12:15 - Zeynep Arslan", "Gram Altın Alışı", fmt_currency(5200)),
            ("11:20 - Ali Çelik", "5gr Külçe Satışı", fmt_currency(13500)),
            ("10:30 - Emre Korkmaz", "22A Yüzük Satışı", fmt_currency(32100))
        ]

        for time_customer, description, amount in recent_items:
            transaction_layout = QHBoxLayout()

            left_part = QVBoxLayout()
            time_label = QLabel(time_customer)
            time_label.setStyleSheet("color: #B7C0CC; font-size: 11px; font-weight: 600;")
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #E9EDF2; font-size: 12px;")
            left_part.addWidget(time_label)
            left_part.addWidget(desc_label)

            amount_label = QLabel(amount)
            amount_label.setStyleSheet("color: #4CAF50; font-size: 13px; font-weight: 600;")
            amount_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            transaction_layout.addLayout(left_part)
            transaction_layout.addWidget(amount_label)
            recent_layout.addLayout(transaction_layout)

        recent_layout.addStretch(1)
        right_column.addWidget(recent_transactions_card)

        main_layout.addLayout(right_column, 1)  # Sağ sütun daha dar

        root.addLayout(main_layout)

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
