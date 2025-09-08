### app/theme.py ###
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import (
    QApplication, QGraphicsDropShadowEffect,
    QWidget, QVBoxLayout, QLabel, QProgressBar
)
from PyQt6.QtCore import Qt

SCHEMES = {
    "dark": {
        "PRIMARY": "#5B8CFF",
        "BG":      "#0C1016",
        "SURFACE": "rgba(22,28,38,0.92)",
        "TEXT":    "#E9EDF2",
        "MUTED":   "#9CA6B4",
        "BORDER":  "rgba(255,255,255,0.06)",
        "FOCUS":   "#8FB3FF",
        "SHADOW":  QColor(0, 0, 0, 180),
    },
    "dim": {
        "PRIMARY": "#4C7DFF",
        "BG":      "#171C23",
        "SURFACE": "rgba(28,34,44,0.96)",
        "TEXT":    "#F1F4F8",
        "MUTED":   "#B7C0CC",
        "BORDER":  "rgba(255,255,255,0.10)",
        "FOCUS":   "#97B7FF",
        "SHADOW":  QColor(0, 0, 0, 140),
    },
    "light": {
        "PRIMARY": "#3C6DFF",
        "BG":      "#F5F7FA",
        "SURFACE": "#FFFFFF",
        "TEXT":    "#1B2430",
        "MUTED":   "#6B7785",
        "BORDER":  "rgba(0,0,0,0.10)",
        "FOCUS":   "#3C6DFF",
        "SHADOW":  QColor(0, 0, 0, 45),
    },
}

def _qss(p):
    return f"""
* {{
  color: {p['TEXT']};
  font-size: 13px;
}}
QMainWindow {{ background: {p['BG']}; }}
QWidget[role="container"] {{ background: transparent; margin: 0px; }}

QFrame#Card {{
  background: {p['SURFACE']};
  border: 1px solid {p['BORDER']};
  border-radius: 18px;
}}

QLabel[variant="title"] {{
  font-weight: 700;
  font-size: 16px;
}}
QLabel[variant="muted"] {{
  color: {p['MUTED']};
  font-size: 12px;
}}

QPushButton {{
  background: transparent;
  border: 1px solid {p['BORDER']};
  border-radius: 12px;
  padding: 8px 14px;
}}
QPushButton:hover {{ border-color: {p['FOCUS']}; }}
QPushButton:pressed {{ background: rgba(127,127,127,0.08); }}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
  background: rgba(255,255,255,0.04);
  border: 1px solid {p['BORDER']};
  border-radius: 10px;
  padding: 8px 10px;
  color: {p['TEXT']};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
  border-color: {p['FOCUS']};
  background: rgba(76,125,255,0.04);
}}

/* QComboBox açılır menü (popup) */
QComboBox QAbstractItemView {{
  background: rgba(28,34,44,0.98);
  color: {p['TEXT']};
  border: 1px solid {p['BORDER']};
  selection-background-color: {p['PRIMARY']};
  selection-color: white;
  outline: none;
}}
QComboBox QAbstractItemView::item {{
  padding: 6px 10px;
}}

QHeaderView::section {{
  background: {p['SURFACE']};
  border: none;
  padding: 8px 10px;
}}
QDialog {{
  background: transparent; 
}}

QTableView {{
  gridline-color: {p['BORDER']};
  selection-background-color: {p['PRIMARY']};
  selection-color: {"white" if p['TEXT'] != "#1B2430" else "#ffffff"};
  background: transparent;
  border: 1px solid {p['BORDER']};
  border-radius: 14px;
  alternate-background-color: rgba(255,255,255,0.04);
}}
QTableView::item {{ background: transparent; }}

QTableWidget {{
  gridline-color: {p['BORDER']};
  selection-background-color: {p['PRIMARY']};
  selection-color: {"white" if p['TEXT'] != "#1B2430" else "#ffffff"};
  background: transparent;
  border: 1px solid {p['BORDER']};
  border-radius: 14px;
  alternate-background-color: rgba(255,255,255,0.04);
}}
QTableWidget::item {{ background: transparent; }}
QTableWidget::item:selected {{ background-color: {p['PRIMARY']}; }}

/* Cam kart */
QFrame#Glass {{
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 16px;
}}

/* Kullanıcı kartları */
QToolButton[role="usercard"] {{
  color: {p['TEXT']};
  border: 1px solid {p['BORDER']};
  border-radius: 16px;
  padding: 8px 6px;
  background: rgba(255,255,255,0.04);
}}
QToolButton[role="usercard"]:hover {{
  border-color: {p['FOCUS']};
  background: rgba(76,125,255,0.08);
}}
QToolButton[role="usercard"]:checked {{
  border-color: {p['PRIMARY']};
  border-width: 2px;
  background: rgba(76,125,255,0.12);
}}

/* QDialog ve açılan pencereler için tema uyumluluğu */
QDialog {{
  /* Arka planı transparent yapmak yerine, cam efektinin temelini atalım */
  background: rgba(28, 34, 44, 0.85); /* Hafif şeffaf yüzey rengi */
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
}}

/* ComboBox açılır menüsü (daha detaylı) */
QComboBox QAbstractItemView {{
  background-color: {p['SURFACE']}; /* Yüzey rengi */
  color: {p['TEXT']};
  border: 1px solid {p['PRIMARY']}; /* Seçimi belli etmek için ana renkte kenarlık */
  selection-background-color: {p['PRIMARY']};
  selection-color: white;
  outline: 0px; /* Rahatsız edici çerçeveyi kaldır */
  padding: 4px; /* Kenarlardan boşluk */
}}
QComboBox QAbstractItemView::item {{
  padding: 8px 12px; /* Her bir elemanın iç boşluğu */
  border-radius: 6px;
}}
QComboBox QAbstractItemView::item:selected {{
  background-color: {p['PRIMARY']};
}}
QComboBox QAbstractItemView::item:hover {{
  background-color: rgba(255, 255, 255, 0.1);
}}

/* QSplitter tutamacı (handle) stilleri */
QSplitter::handle {{
    background-color: {p['BORDER']}; /* Kenarlık rengiyle aynı olsun */
    image: none; /* Varsayılan okları/noktaları kaldır */
}}
QSplitter::handle:horizontal {{
    width: 4px; /* Genişlik */
    margin: 2px 0;
}}
QSplitter::handle:vertical {{
    height: 4px; /* Yükseklik */
    margin: 0 2px;
}}
QSplitter::handle:hover {{
    background-color: {p['PRIMARY']}; /* Üzerine gelince ana renge dönsün */
}}
"""

def apply_theme(app: QApplication, scheme: str = "dim"):
    p = SCHEMES.get(scheme, SCHEMES["dim"])
    app.setStyleSheet(_qss(p))
    app.setFont(QFont("Segoe UI", 10))

def apply_dialog_theme(dialog, scheme: str = "dim"):
    """Dialog'lara özel tema uygular"""
    p = SCHEMES.get(scheme, SCHEMES["dim"])

    dialog.setStyleSheet(f"""
        /* Dialog ana kapsayıcı */
        QDialog {{
            background: {p['BG']};
            color: {p['TEXT']};
            border: 1px solid {p['BORDER']};
            border-radius: 16px;
        }}

        /* Tüm genel etiketler */
        QLabel {{
            color: {p['TEXT']};
            font-size: 13px;
        }}

        /* Özel variant'lı etiketler */
        QLabel[variant="muted"] {{
            color: {p['MUTED']};
            font-size: 12px;
        }}

        QLabel[variant="title"] {{
            color: {p['TEXT']};
            font-weight: 700;
            font-size: 16px;
        }}

        /* GroupBox'lar */
        QGroupBox {{
            font-weight: 600;
            color: {p['TEXT']};
            border: 1px solid {p['BORDER']};
            border-radius: 10px;
            margin-top: 6px;
            padding: 10px;
            background: transparent;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px;
            color: {p['TEXT']};
            font-weight: 600;
        }}

        /* Form elemanları */
        QLineEdit, QDateEdit, QTimeEdit, QComboBox, QDoubleSpinBox, QTextEdit {{
            background: rgba(255,255,255,0.04);
            border: 1px solid {p['BORDER']};
            border-radius: 8px;
            padding: 8px 10px;
            color: {p['TEXT']};
            font-size: 13px;
            selection-background-color: {p['PRIMARY']};
        }}

        QLineEdit:focus, QDateEdit:focus, QTimeEdit:focus, QComboBox:focus,
        QDoubleSpinBox:focus, QTextEdit:focus {{
            border-color: {p['FOCUS']};
            background: rgba(76,125,255,0.04);
        }}

        /* QDoubleSpinBox özel */
        QDoubleSpinBox {{
            padding-right: 20px; /* Oklar için yer bırak */
        }}

        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
            background: transparent;
            border: none;
            width: 16px;
            height: 12px;
        }}

        QDoubleSpinBox::up-arrow {{
            image: url(up_arrow.png); /* Varsayılan okları kullan */
            width: 8px;
            height: 8px;
        }}

        QDoubleSpinBox::down-arrow {{
            image: url(down_arrow.png);
            width: 8px;
            height: 8px;
        }}

        /* QDateEdit/QTimeEdit takvim/saat açılır butonları */
        QDateEdit::drop-down, QTimeEdit::drop-down {{
            background: transparent;
            border: none;
            width: 20px;
        }}

        /* QDateEdit takvim popup'u */
        QCalendarWidget {{
            background: {p['SURFACE']};
            color: {p['TEXT']};
            border: 1px solid {p['BORDER']};
            border-radius: 8px;
        }}

        QCalendarWidget QToolButton {{
            color: {p['TEXT']};
            background: transparent;
            border: none;
            border-radius: 4px;
            padding: 4px;
        }}

        QCalendarWidget QToolButton:hover {{
            background: rgba(76,125,255,0.1);
        }}

        /* QComboBox açılır menüsü */
        QComboBox::drop-down {{
            background: transparent;
            border: none;
            width: 20px;
        }}

        QComboBox QAbstractItemView {{
            background: {p['SURFACE']};
            color: {p['TEXT']};
            border: 1px solid {p['BORDER']};
            border-radius: 6px;
            selection-background-color: {p['PRIMARY']};
            selection-color: white;
            outline: none;
            padding: 4px;
        }}

        QComboBox QAbstractItemView::item {{
            padding: 8px 12px;
            border-radius: 4px;
            color: {p['TEXT']};
        }}

        QComboBox QAbstractItemView::item:selected {{
            background-color: {p['PRIMARY']};
            color: white;
        }}

        QComboBox QAbstractItemView::item:hover {{
            background-color: rgba(76,125,255,0.1);
        }}

        /* Butonlar */
        QPushButton {{
            background: rgba(255,255,255,0.04);
            border: 1px solid {p['BORDER']};
            border-radius: 8px;
            padding: 10px 16px;
            color: {p['TEXT']};
            font-weight: 500;
            font-size: 13px;
            min-width: 80px;
        }}

        QPushButton:hover {{
            border-color: {p['FOCUS']};
            background: rgba(76,125,255,0.06);
            color: {p['TEXT']};
        }}

        QPushButton:pressed {{
            background: rgba(76,125,255,0.12);
        }}

        QPushButton:disabled {{
            color: {p['MUTED']};
            border-color: rgba(255,255,255,0.06);
            background: rgba(255,255,255,0.02);
            opacity: 0.6;
        }}

        /* Primary variant butonlar */
        QPushButton[variant="primary"] {{
            background: rgba(76,125,255,0.15);
            border: 1px solid {p['PRIMARY']};
            color: {p['TEXT']};
            font-weight: 600;
        }}

        QPushButton[variant="primary"]:hover {{
            background: rgba(76,125,255,0.25);
            border-color: {p['FOCUS']};
        }}

        QPushButton[variant="primary"]:pressed {{
            background: rgba(76,125,255,0.35);
        }}

        QPushButton[variant="primary"]:disabled {{
            opacity: 0.6;
            border-color: rgba(255,255,255,0.04);
            background: rgba(255,255,255,0.02);
        }}

        /* Özel çerçeveler */
        QFrame#DialogCard {{
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 16px;
        }}

        QFrame#Glass {{
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 16px;
        }}

        /* Takvim popup'u için */
        QCalendarWidget {{
            background: {p['SURFACE']};
            color: {p['TEXT']};
            border: 1px solid {p['BORDER']};
            border-radius: 8px;
        }}

        QCalendarWidget QToolButton {{
            color: {p['TEXT']};
            background: transparent;
            border: none;
            border-radius: 4px;
            padding: 4px;
        }}

        QCalendarWidget QToolButton:hover {{
            background: rgba(76,125,255,0.1);
        }}

        QCalendarWidget QMenu {{
            background: {p['SURFACE']};
            color: {p['TEXT']};
            border: 1px solid {p['BORDER']};
        }}

        QCalendarWidget QSpinBox {{
            background: rgba(255,255,255,0.04);
            border: 1px solid {p['BORDER']};
            border-radius: 4px;
            color: {p['TEXT']};
        }}
    """)

def elevate(widget, scheme: str = "dim", blur=36, y=10):
    p = SCHEMES.get(scheme, SCHEMES["dim"])
    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(blur)
    effect.setXOffset(0)
    effect.setYOffset(y)
    effect.setColor(p["SHADOW"])
    widget.setGraphicsEffect(effect)
    return widget

# Loading durumu için widget
class LoadingWidget(QWidget):
    def __init__(self, message="Veriler yükleniyor...", parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel(message)
        self.label.setProperty("variant", "title")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Belirsiz progress
        self.progress.setFixedWidth(200)

        layout.addStretch()
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        layout.addStretch()

# Empty state için widget
class EmptyStateWidget(QWidget):
    def __init__(self, message="Gösterilecek kayıt bulunamadı.", icon="📄", parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_label = QLabel(icon)
        self.icon_label.setStyleSheet("font-size: 48px; color: #6B7785;")
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.message_label = QLabel(message)
        self.message_label.setProperty("variant", "muted")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setStyleSheet("font-size: 14px; color: #6B7785;")

        layout.addStretch()
        layout.addWidget(self.icon_label)
        layout.addWidget(self.message_label)
        layout.addStretch()

# theme.py
from PyQt6.QtWidgets import QPushButton

def style_button(btn: QPushButton, variant: str = "neutral"):
    palette = {
        "success": ("#2e7d32", "#43a047", "#FFFFFF"),
        "danger":  ("#c62828", "#ef5350", "#FFFFFF"),
        "warning": ("#ffb300", "#ffa000", "#0b0f16"),
        "neutral": ("rgba(255,255,255,0.06)", "rgba(255,255,255,0.12)", "#E9EDF2"),
    }
    bg, border, fg = palette.get(variant, palette["neutral"])
    # Hover renklerini hesapla (basit tonlama)
    hover_bg = bg
    if variant == "success":
        hover_bg = "#388e3c"  # daha koyu yeşil
    elif variant == "danger":
        hover_bg = "#d32f2f"  # daha koyu kırmızı
    elif variant == "warning":
        hover_bg = "#ffca28"  # daha açık sarı

    btn.setStyleSheet(f"""
        QPushButton {{
            padding: 10px; border-radius: 10px;
            background: {bg}; color: {fg};
            border: 1px solid {border}; font-weight: 600;
        }}
        QPushButton:hover {{
            background: {hover_bg};
        }}
    """)