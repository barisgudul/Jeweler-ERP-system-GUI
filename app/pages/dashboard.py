# app/pages/dashboard.py
from PyQt6.QtWidgets import (QWidget, QGridLayout, QLabel, QFrame, QVBoxLayout,
                           QHBoxLayout, QPushButton, QLayout)
from PyQt6.QtCore import Qt, QLocale, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter, QLinearGradient, QColor
import random
from random import uniform, randint
from theme import elevate

TR = QLocale(QLocale.Language.Turkish, QLocale.Country.Turkey)

def fmt_currency(value: float) -> str:
    return TR.toCurrencyString(value, "₺")

def tl(v: float) -> str:
    try:
        return TR.toCurrencyString(float(v), "₺")
    except:
        return f"{float(v):,.2f} ₺"

def kpi_card(title: str, value: str, subtitle: str = "") -> QFrame:
    card = QFrame()
    card.setObjectName("Glass")
    v = QVBoxLayout(card)
    v.setContentsMargins(16, 16, 16, 16)
    v.setSpacing(8)

    title_label = QLabel(title)
    title_label.setProperty("variant", "title")
    v.addWidget(title_label)

    value_label = QLabel(value)
    value_label.setProperty("variant", "heading")
    v.addWidget(value_label)

    if subtitle:
        sub_label = QLabel(subtitle)
        sub_label.setProperty("variant", "muted")
        v.addWidget(sub_label)

    v.addStretch(1)
    elevate(card, scheme="dim", blur=32, y=10)
    return card

class DashboardPage(QWidget):
    quick_action_triggered = pyqtSignal(dict)

    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.data = data
        self._recent_max = 7

        # === KOZMİK ARKA PLAN ===
        self._sky = QLabel(self)
        self._sky.lower()  # en arkada dursun
        self._sky.setScaledContents(True)
        self._sky.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Ana layout
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)

        # Başlık
        header = QHBoxLayout()
        title = QLabel("Dashboard")
        tf = QFont("Segoe UI", 18, QFont.Weight.Bold)
        title.setFont(tf)
        header.addWidget(title, 0, Qt.AlignmentFlag.AlignLeft)

        hint = QLabel("Güncel göstergeler • canlı mock veri")
        hint.setProperty("variant", "muted")
        header.addWidget(hint, 0, Qt.AlignmentFlag.AlignRight)
        root.addLayout(header)

        # Ana layout - iki sütun
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)

        # Sol sütun: KPI'lar
        left_column = QVBoxLayout()
        left_column.setSpacing(16)

        # KPI grid
        kpi_grid = QGridLayout()
        kpi_grid.setHorizontalSpacing(12)
        kpi_grid.setVerticalSpacing(12)

        # Mock değerler
        self.gram = round(uniform(2500, 2700), 2)
        self.satis = round(uniform(150000, 350000), 2)
        self.stok = round(uniform(2000000, 3500000), 2)
        self.aylik_ciro = round(uniform(2000000, 4000000), 2)
        self.bekleyen_odeme = round(uniform(50000, 150000), 2)
        self.kritik_stok = randint(3, 8)

        # Gram altın kartı
        gold_card = QFrame()
        gold_card.setObjectName("Glass")
        gv = QVBoxLayout(gold_card)
        gv.setContentsMargins(20, 20, 20, 20)
        gv.setSpacing(12)

        g_title = QLabel("Gram Altın")
        g_title.setProperty("variant", "title")
        gv.addWidget(g_title)

        self._gram_val_label = QLabel(fmt_currency(self.gram))
        gf = QFont("Segoe UI", 26)
        gf.setWeight(QFont.Weight.ExtraBold)
        self._gram_val_label.setFont(gf)
        gv.addWidget(self._gram_val_label)

        sub = QLabel("Anlık gram fiyatı")
        sub.setProperty("variant", "muted")
        gv.addWidget(sub)

        gv.addStretch(1)
        elevate(gold_card, scheme="dim", blur=32, y=10)
        kpi_grid.addWidget(gold_card, 0, 0)

        # Diğer KPI kartları
        kpi_grid.addWidget(kpi_card("Günlük Satış", fmt_currency(self.satis), "Bugünün toplam işlemleri"), 0, 1)
        kpi_grid.addWidget(kpi_card("Toplam Stok Değeri", fmt_currency(self.stok), "Stoktaki varlıkların değeri"), 0, 2)
        kpi_grid.addWidget(kpi_card("Aylık Ciro", fmt_currency(self.aylik_ciro), "Bu ay toplam satış"), 1, 0)
        kpi_grid.addWidget(kpi_card("Bekleyen Ödeme", fmt_currency(self.bekleyen_odeme), "Tedarikçi borçları"), 1, 1)
        kpi_grid.addWidget(kpi_card("Kritik Stok", f"{self.kritik_stok} ürün", "Düşük stok seviyesi"), 1, 2)

        for c in range(3):
            kpi_grid.setColumnStretch(c, 1)

        left_column.addLayout(kpi_grid)

        # Kritik stok listesi
        critical_stock_card = QFrame()
        critical_stock_card.setObjectName("Glass")
        critical_stock_card.setMinimumHeight(200)
        elevate(critical_stock_card, "dim", blur=24, y=6)
        critical_layout = QVBoxLayout(critical_stock_card)
        critical_layout.setContentsMargins(16, 16, 16, 16)

        critical_title = QLabel("Kritik Stok Seviyesi")
        critical_title.setProperty("variant", "title")
        critical_layout.addWidget(critical_title)

        critical_items = [
            ("Bilezik 22A", "2 adet"),
            ("Kolye 18A", "1 adet"),
            ("Yüzük 22A", "3 adet"),
            ("Külçe 5gr", "2 adet")
        ]

        for item_name, stock in critical_items:
            item_label = QLabel(f"• {item_name}: {stock}")
            item_label.setProperty("variant", "danger")
            item_label.setStyleSheet("font-size: 12px; margin: 2px 0px; font-weight: 600;")
            critical_layout.addWidget(item_label)

        critical_layout.addStretch(1)
        left_column.addWidget(critical_stock_card)

        left_column.addStretch(1)
        main_layout.addLayout(left_column, 2)

        # Sağ sütun: Hızlı erişim ve son işlemler
        right_column = QVBoxLayout()
        right_column.setSpacing(16)

        # Hızlı erişim kartı
        quick_access_card = QFrame()
        quick_access_card.setObjectName("Glass")
        quick_access_card.setMinimumHeight(200)
        elevate(quick_access_card, "dim", blur=24, y=6)
        quick_layout = QVBoxLayout(quick_access_card)
        quick_layout.setContentsMargins(16, 16, 16, 16)

        quick_title = QLabel("Hızlı Erişim")
        quick_title.setProperty("variant", "title")
        quick_layout.addWidget(quick_title)

        # Hızlı erişim butonları - 2x2 grid düzen
        quick_grid = QGridLayout()
        quick_grid.setHorizontalSpacing(12)
        quick_grid.setVerticalSpacing(12)

        btn_new_sale = QPushButton("Yeni Satış İşlemi")
        btn_new_customer = QPushButton("Yeni Müşteri Ekle")
        btn_new_stock = QPushButton("Yeni Stok Girişi")
        btn_reports = QPushButton("Raporlar")

        # Buton bağlantıları
        btn_new_sale.clicked.connect(lambda: self.quick_action_triggered.emit({'route': 'sales', 'action': 'new'}))
        btn_new_customer.clicked.connect(lambda: self.quick_action_triggered.emit({'route': 'customers', 'action': 'new'}))
        btn_new_stock.clicked.connect(lambda: self.quick_action_triggered.emit({'route': 'stock', 'action': 'new'}))
        btn_reports.clicked.connect(lambda: self.quick_action_triggered.emit({'route': 'reports', 'action': 'view'}))

        # Butonları 2x2 grid'e yerleştir
        quick_grid.addWidget(btn_new_sale, 0, 0)      # Sol üst
        quick_grid.addWidget(btn_new_customer, 0, 1)   # Sağ üst
        quick_grid.addWidget(btn_new_stock, 1, 0)      # Sol alt
        quick_grid.addWidget(btn_reports, 1, 1)        # Sağ alt

        # Buton stilleri ve minimum yükseklik
        for btn in [btn_new_sale, btn_new_customer, btn_new_stock, btn_reports]:
            btn.setMinimumHeight(45)
            btn.setMinimumWidth(140)  # Minimum genişlik ekle

        # Grid'i ana layout'a ekle
        quick_layout.addLayout(quick_grid)

        right_column.addWidget(quick_access_card)

        # Son işlemler kartı
        recent_transactions_card = QFrame()
        recent_transactions_card.setObjectName("Glass")
        recent_transactions_card.setMinimumHeight(250)
        elevate(recent_transactions_card, "dim", blur=24, y=6)
        self.recent_layout = QVBoxLayout(recent_transactions_card)
        self.recent_layout.setContentsMargins(16, 16, 16, 16)

        recent_title = QLabel("Son İşlemler")
        recent_title.setProperty("variant", "title")
        self.recent_layout.addWidget(recent_title)

        # Son işlemleri yükle
        self.reload_recent_from_db()
        right_column.addWidget(recent_transactions_card)

        main_layout.addLayout(right_column, 1)
        root.addLayout(main_layout)

        # Başlangıçta market fiyatlarını çek ve güncelle
        if self.data:
            # Market data güncellendiğinde otomatik güncelle
            self.data.marketDataUpdated.connect(self._update_market_kpis)
            self.data.fetch_market_prices()
            self._update_market_kpis()

        # Kozmik arka planı çiz
        self._paint_sky(self.width(), self.height())

    def _clear_recent_ui(self):
        while self.recent_layout.count() > 1:
            item = self.recent_layout.takeAt(1)
            w = item.widget()
            if w:
                w.deleteLater()

    def _add_recent_card(self, *, kind: str, date: str, doc_no: str, who: str, total: float, pay_type: str, due: float):
        card = QFrame()
        card.setObjectName("Glass")

        h = QHBoxLayout(card)
        h.setContentsMargins(12, 8, 12, 8)
        h.setSpacing(12)

        left_v = QVBoxLayout()
        left_v.setSpacing(2)

        type_date = QLabel(f"{kind} • {date}")
        type_date.setProperty("variant", "title")
        left_v.addWidget(type_date)

        doc_label = QLabel(f"Belge: {doc_no}")
        doc_label.setProperty("variant", "muted")
        doc_label.setStyleSheet("font-size: 11px;")
        left_v.addWidget(doc_label)

        h.addLayout(left_v)

        center_v = QVBoxLayout()
        center_v.setSpacing(2)

        who_label = QLabel(who)
        who_label.setProperty("variant", "title")
        who_label.setStyleSheet("font-weight: 500;")
        center_v.addWidget(who_label)

        total_label = QLabel(tl(total))
        total_label.setProperty("variant", "success")
        total_label.setStyleSheet("font-size: 14px;")
        center_v.addWidget(total_label)

        h.addLayout(center_v)

        right_v = QVBoxLayout()
        right_v.setSpacing(2)

        pay_label = QLabel(pay_type)
        pay_label.setProperty("variant", "muted")
        pay_label.setStyleSheet("font-size: 11px;")
        right_v.addWidget(pay_label)

        if due > 0:
            due_label = QLabel(f"Bekleyen: {tl(due)}")
            due_label.setProperty("variant", "warning")
            due_label.setStyleSheet("font-size: 11px;")
            right_v.addWidget(due_label)

        h.addLayout(right_v)
        self.recent_layout.addWidget(card)

    def reload_recent_from_db(self):
        if not self.data:
            return

        self._clear_recent_ui()
        recent = self.data.get_recent_transactions(limit=self._recent_max)

        for tx in recent:
            self._add_recent_card(
                kind=tx['kind'],
                date=tx['date'],
                doc_no=tx['doc_no'],
                who=tx['who'],
                total=tx['total'],
                pay_type=tx['pay_type'],
                due=tx['due']
            )

    def on_sale_committed(self, payload: dict):
        self.reload_recent_from_db()
        if hasattr(self, '_update_market_kpis'):
            self._update_market_kpis()

    def _update_market_kpis(self):
        if not self.data or not hasattr(self.data, 'market_data'):
            return

        market = self.data.market_data
        # API'den gelen gram altın anahtarı HAS_ALTIN
        gram_keys = ['HAS_ALTIN', 'gram_altin', 'Gram Altın']

        for key in gram_keys:
                if key in market:
                    price = market[key].get('satis', 0)  # satış fiyatını kullan
                    if price > 0:
                        self._gram_val_label.setText(fmt_currency(price))
                        break

    # --- kozmik arka plan
    def _paint_sky(self, w: int, h: int):
        if w <= 0 or h <= 0: return
        pm = QPixmap(w, h)
        pm.fill(Qt.GlobalColor.black)
        p = QPainter(pm)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        grad = QLinearGradient(0, 0, w, h)
        grad.setColorAt(0.0, QColor(10, 16, 32))
        grad.setColorAt(0.5, QColor(20, 26, 48))
        grad.setColorAt(1.0, QColor(12, 18, 36))
        p.fillRect(0, 0, w, h, grad)
        p.setPen(Qt.PenStyle.NoPen)
        for _ in range(int((w * h) / 12000)):
            x, y = random.randint(0, w), random.randint(0, h)
            r = random.choice([1, 1, 2])
            p.setBrush(QColor(255, 255, 255, random.randint(70, 150)))
            p.drawEllipse(x, y, r, r)
        p.end()
        self._sky.setPixmap(pm)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, '_sky'):
            self._sky.resize(self.size())
            self._paint_sky(self.width(), self.height())