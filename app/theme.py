### app/theme.py ###
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtWidgets import QApplication, QGraphicsDropShadowEffect

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

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
  background: rgba(255,255,255,0.04);
  border: 1px solid {p['BORDER']};
  border-radius: 10px;
  padding: 8px 10px;
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
  border-color: {p['FOCUS']};
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
"""

def apply_theme(app: QApplication, scheme: str = "dim"):
    p = SCHEMES.get(scheme, SCHEMES["dim"])
    app.setStyleSheet(_qss(p))
    app.setFont(QFont("Segoe UI", 10))

def elevate(widget, scheme: str = "dim", blur=36, y=10):
    p = SCHEMES.get(scheme, SCHEMES["dim"])
    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(blur)
    effect.setXOffset(0)
    effect.setYOffset(y)
    effect.setColor(p["SHADOW"])
    widget.setGraphicsEffect(effect)
    return widget
