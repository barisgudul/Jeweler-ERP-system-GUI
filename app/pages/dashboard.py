# app/pages/dashboard.py
from PyQt6.QtWidgets import QWidget, QGridLayout, QLabel, QFrame, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, QLocale
from PyQt6.QtGui import QFont
from random import uniform
from theme import elevate  # gölge için

TR = QLocale(QLocale.Language.Turkish, QLocale.Country.Turkey)

def fmt_currency(value: float) -> str:
    # Yerel biçimlendirme + ₺, ince boşluklar
    return TR.toCurrencyString(value, "₺")

def kpi_card(title: str, value: str, subtitle: str = "") -> QFrame:
    card = QFrame()
    card.setObjectName("Card")
    v = QVBoxLayout(card)
    v.setContentsMargins(18, 18, 18, 18)
    v.setSpacing(10)

    t = QLabel(title)
    t.setProperty("variant", "title")
    v.addWidget(t)

    val = QLabel(value)
    f = QFont("Segoe UI", 24)
    f.setWeight(QFont.Weight.ExtraBold)
    val.setFont(f)
    v.addWidget(val)

    if subtitle:
        sub = QLabel(subtitle)
        sub.setProperty("variant", "muted")
        v.addWidget(sub)

    v.addStretch(1)
    elevate(card,scheme="dim", blur=28, y=8)  # ipek gölge
    return card

class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(16)

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

        # — KPI grid
        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)

        # Sahte (mock) değerler
        gram  = round(uniform(2500, 2700), 2)
        satis = round(uniform(150000, 350000), 2)
        stok  = round(uniform(2000000, 3500000), 2)

        grid.addWidget(kpi_card("Gram Altın",        fmt_currency(gram),  "Anlık gram fiyatı"), 0, 0)
        grid.addWidget(kpi_card("Günlük Satış",      fmt_currency(satis), "Bugünün toplam işlemleri"), 0, 1)
        grid.addWidget(kpi_card("Toplam Stok Değeri",fmt_currency(stok),  "Stoktaki varlıkların tahmini değeri"), 0, 2)

        # Sütunlar eşit genişlikte
        for c in range(3):
            grid.setColumnStretch(c, 1)

        root.addLayout(grid)
        root.addStretch(1)
