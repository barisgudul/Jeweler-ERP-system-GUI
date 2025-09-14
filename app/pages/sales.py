### app/pages/sales.py ###

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QDateEdit,
    QPushButton, QFrame, QTableWidget, QTableWidgetItem, QAbstractItemView,
    QHeaderView, QSplitter, QSpinBox, QDoubleSpinBox, QMessageBox, QGroupBox,
    QFormLayout, QStyledItemDelegate, QStyleOptionViewItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, QLocale, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter, QLinearGradient, QColor, QPalette
import os
from .parameters import parse_money, fmt_money, TR

# PDF oluşturma için gerekli import'lar
try:
    from reportlab.lib.pagesizes import A5
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
    from reportlab.lib import colors
    from reportlab.lib.units import cm, mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.fonts import addMapping
    import os

    # Unicode fontları kaydet (Türkçe karakterler için)
    FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts")

    # Font dosyaları var mı kontrol et (birden fazla seçenek)
    FONTS_AVAILABLE = False

    # 1. Önce DejaVu fontlarını dene
    dejavu_font = os.path.join(FONT_DIR, "DejaVuSans.ttf")
    dejavu_bold_font = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

    if os.path.exists(dejavu_font) and os.path.exists(dejavu_bold_font):
        try:
            pdfmetrics.registerFont(TTFont("DejaVu", dejavu_font))
            pdfmetrics.registerFont(TTFont("DejaVu-Bold", dejavu_bold_font))
            addMapping("DejaVu", 0, 0, "DejaVu")
            addMapping("DejaVu", 0, 1, "DejaVu")
            addMapping("DejaVu", 1, 0, "DejaVu-Bold")
            addMapping("DejaVu", 1, 1, "DejaVu-Bold")
            FONTS_AVAILABLE = True
            print("✓ DejaVu fontları yüklendi")
        except Exception as e:
            print(f"✗ DejaVu font yükleme hatası: {e}")

    # 2. Alternatif: Sistem fontlarını dene (Windows için)
    if not FONTS_AVAILABLE:
        system_fonts = [
            (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
            (r"C:\Windows\Fonts\calibri.ttf", r"C:\Windows\Fonts\calibrib.ttf"),
            (r"C:\Windows\Fonts\tahoma.ttf", r"C:\Windows\Fonts\tahomabd.ttf")
        ]

        for normal_path, bold_path in system_fonts:
            if os.path.exists(normal_path):
                try:
                    pdfmetrics.registerFont(TTFont("SystemFont", normal_path))
                    if os.path.exists(bold_path):
                        pdfmetrics.registerFont(TTFont("SystemFont-Bold", bold_path))
                    else:
                        # Bold yoksa normal'i bold olarak kullan
                        pdfmetrics.registerFont(TTFont("SystemFont-Bold", normal_path))

                    addMapping("SystemFont", 0, 0, "SystemFont")
                    addMapping("SystemFont", 0, 1, "SystemFont")
                    addMapping("SystemFont", 1, 0, "SystemFont-Bold")
                    addMapping("SystemFont", 1, 1, "SystemFont-Bold")
                    FONTS_AVAILABLE = True
                    print("✓ Sistem fontu yüklendi")
                    break
                except Exception as e:
                    print(f"✗ Sistem font yükleme hatası: {e}")
                    continue

    # 3. Son çare: Unicode destekli basit font oluştur
    if not FONTS_AVAILABLE:
        print("⚠️ Özel font bulunamadı, varsayılan kullanılacak")

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    FONTS_AVAILABLE = False
from random import randint, choice
from dialogs import NewSaleItemDialog, NewCustomerDialog
from theme import elevate

TR = QLocale(QLocale.Language.Turkish, QLocale.Country.Turkey)

class QtyDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        sb = QSpinBox(parent)
        sb.setRange(1, 9999)
        sb.setAccelerated(True)
        sb.setButtonSymbols(QSpinBox.ButtonSymbols.PlusMinus)  # +/−
        sb.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sb.setMinimumHeight(28)
        sb.setStyleSheet("""
            QSpinBox {
                padding: 2px 6px; border-radius: 6px;
                background: rgba(76,125,255,0.12);
                border: 1px solid rgba(76,125,255,0.45);
                color: #E9EDF2; font-weight: 600;
            }
            QSpinBox:focus { border-color:#8FB3FF; }
            /* butonlar sabit boy – değerde artış olsa da genişlik oynamaz */
            QSpinBox::up-button, QSpinBox::down-button {
                width: 18px; height: 16px; margin: 0px;
            }
        """)
        # spinbox değer değişince modeli hemen güncelle
        sb.valueChanged.connect(lambda _:
            self.commitData.emit(sb)
        )
        return sb

    def setEditorData(self, editor, index):
        # Öncelik: UserRole (saf sayı)
        val = index.model().data(index, Qt.ItemDataRole.UserRole)
        if val is None:
            # Geriye dönük uyum: DisplayRole'dan da deneriz
            try:
                val = int(index.model().data(index, Qt.ItemDataRole.DisplayRole) or 1)
            except:
                val = 1
        editor.blockSignals(True)
        editor.setValue(max(1, int(val)))
        editor.blockSignals(False)
        # Çift metni önlemek için:
        index.model().setData(index, "", Qt.ItemDataRole.DisplayRole)

    def setModelData(self, editor, model, index):
        v = int(editor.value())
        # Sadece gerçek sayıyı UserRole'da tut
        model.setData(index, v, Qt.ItemDataRole.UserRole)
        # Görünür metni boşalt → "çift çizim" biter
        model.setData(index, "", Qt.ItemDataRole.DisplayRole)

    def updateEditorGeometry(self, editor, option, index):
        # editör tam hücreyi kaplasın (hiç boşluk kalmasın)
        editor.setGeometry(option.rect)

    def paint(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        self.initStyleOption(opt, index)
        opt.text = ""  # metni çizme
        super().paint(painter, opt, index)

# === Toplu Ürün Seçim Diyaloğu ================================================
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QTableWidget,
    QTableWidgetItem, QPushButton, QFrame, QAbstractItemView, QHeaderView,
    QSpinBox, QDoubleSpinBox, QLabel
)
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QFont

class MultiProductPickerDialog(QDialog):
    """
    Bir seferde birden fazla ürünü seç; her satırda Adet/Gram/Birim Fiyat düzenlenebilir.
    Seçili satırların listesi data() ile döner.
    """
    def __init__(self, parent=None, products: list[dict] = None):
        super().__init__(parent)
        self.setWindowTitle("Ürün Seçimi")
        self.setModal(True)
        self.setMinimumWidth(1400)
        self.setMinimumHeight(700)

        v = QVBoxLayout(self); v.setContentsMargins(20,20,20,20); v.setSpacing(16)

        # Başlık - adet değiştirme ipucu ile
        title_label = QLabel("Ürün Seçimi\nAdet değiştirmek için adet sütununa tıklayın")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #E9EDF2;
                padding: 8px 0px;
                margin-bottom: 8px;
                letter-spacing: 0.5px;
                line-height: 1.4;
            }
        """)
        v.addWidget(title_label)

        # — Filtre satırı - çok belirgin
        top = QHBoxLayout(); top.setSpacing(12)

        # Arama etiketi
        search_label = QLabel("Ara:")
        search_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #E9EDF2; padding: 4px 8px 4px 0px;")
        self.ed_search = QLineEdit(placeholderText="Kod, ürün adı, kategori...")
        self.ed_search.setMinimumHeight(36)
        self.ed_search.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                font-weight: 600;
                padding: 8px 12px;
                border-radius: 8px;
                background: rgba(255,255,255,0.1);
                border: 2px solid rgba(76,125,255,0.4);
                color: #E9EDF2;
            }
            QLineEdit:focus {
                border-color: #4C7DFF;
                background: rgba(76,125,255,0.15);
            }
        """)

        # Kategori etiketi
        cat_label = QLabel("Kategori:")
        cat_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #E9EDF2; padding: 4px 8px 4px 0px;")
        self.cmb_cat = QComboBox()
        self.cmb_cat.setMinimumHeight(36)
        cats = ["Tümü"]
        if products:
            cats.extend(sorted({p["Kategori"] for p in products}))
        self.cmb_cat.addItems(cats)
        self.cmb_cat.setStyleSheet("""
            QComboBox {
                font-size: 14px;
                font-weight: 600;
                padding: 8px 12px;
                border-radius: 8px;
                background: rgba(255,255,255,0.1);
                border: 2px solid rgba(76,125,255,0.4);
                color: #E9EDF2;
                min-width: 140px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background: rgba(28,34,44,0.98);
                color: #E9EDF2;
                border: 2px solid rgba(76,125,255,0.4);
                selection-background-color: #4C7DFF;
                padding: 6px;
                font-size: 14px;
                font-weight: 500;
            }
        """)

        top.addWidget(search_label, 0)
        top.addWidget(self.ed_search, 2)
        top.addWidget(cat_label, 0)
        top.addWidget(self.cmb_cat, 1)
        v.addLayout(top)

        # — Tablo
        self.tbl = QTableWidget(0, 11, self)
        self.tbl.setHorizontalHeaderLabels([
            "Seç","Kod","Ürün","Kategori","Gram","Adet (tıkla)","Birim Fiyat","Stok",
            "Milyem","İşçilik","Detay"
        ])
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setCornerButtonEnabled(False)
        self.tbl.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        # Delegate'i adet sütununa bağla
        self.tbl.setItemDelegateForColumn(5, QtyDelegate(self.tbl))
        self.tbl.setEditTriggers(
            QAbstractItemView.EditTrigger.SelectedClicked |
            QAbstractItemView.EditTrigger.EditKeyPressed
        )  # tek tık + klavye
        self.tbl.setAlternatingRowColors(True)

        # Ana sales tablosu ile aynı stil + adet sütunu vurgusu
        self.tbl.setStyleSheet("""
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
            /* Seçilince çerçeve vurgusu */
            QTableWidget::item:selected:active {
                border: 2px solid rgba(143,179,255,0.9);
                background: rgba(76,125,255,0.25);
            }
        """)

        # Ana sales tablosu ile aynı palette ayarı
        pal = self.tbl.palette()
        pal.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0, 0))
        pal.setColor(QPalette.ColorRole.AlternateBase, QColor(255, 255, 255, 8))
        pal.setColor(QPalette.ColorRole.Text, QColor(241, 244, 248))
        pal.setColor(QPalette.ColorRole.Highlight, QColor(76, 125, 255, 150))
        pal.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        self.tbl.setPalette(pal)

        # Ana sales tablosu ile aynı header stili
        hdr = self.tbl.horizontalHeader()
        hdr.setDefaultAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)

        # ÖNEMLİ: son sütunu esnetme, ürün adını esnet
        hdr.setStretchLastSection(False)
        hdr.setMinimumSectionSize(90)
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

        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed);   self.tbl.setColumnWidth(0, 70)     # Seç
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed);   self.tbl.setColumnWidth(1, 110)    # Kod
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)                                      # Ürün (esner)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed);   self.tbl.setColumnWidth(3, 140)    # Kategori
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed);   self.tbl.setColumnWidth(4, 90)     # Gram
        hdr.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed);   self.tbl.setColumnWidth(5, 110)    # Adet
        hdr.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed);   self.tbl.setColumnWidth(6, 135)    # Birim
        hdr.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed);   self.tbl.setColumnWidth(7, 110)    # Stok
        hdr.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed);   self.tbl.setColumnWidth(8, 90)     # Milyem (bir tık artırdım)
        hdr.setSectionResizeMode(9, QHeaderView.ResizeMode.Fixed);   self.tbl.setColumnWidth(9, 120)    # İşçilik (bir tık artırdım)

        # Detay sütunu sabit genişlikte olsun
        hdr.setSectionResizeMode(10, QHeaderView.ResizeMode.Fixed)
        self.tbl.setColumnWidth(10, 120)

        # Sabit satır yüksekliği - adet artınca hücre "şişmesin"
        self.tbl.verticalHeader().setDefaultSectionSize(42)

        # Daha pürüzsüz yatay kaydırma için bonus
        self.tbl.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        # Küçük güvenlik payı - sağda 2px tampon
        self.tbl.setViewportMargins(0, 0, 2, 0)

        v.addWidget(self.tbl, 1)

        self._all_products = products[:] if products else []
        self._apply_filter()

        # — Alt butonlar - çok belirgin
        bottom = QHBoxLayout(); bottom.addStretch(1)
        self.btn_cancel = QPushButton("İptal")
        self.btn_ok = QPushButton("Ürünleri Ekle")

        for b in (self.btn_cancel, self.btn_ok):
            b.setMinimumWidth(160)
            b.setMinimumHeight(45)
            b.setStyleSheet("""
                QPushButton {
                    font-size: 15px;
                    font-weight: 700;
                    padding: 10px 18px;
                    border-radius: 8px;
                    background: rgba(255,255,255,0.1);
                    border: 2px solid rgba(76,125,255,0.4);
                    color: #E9EDF2;
                    letter-spacing: 0.5px;
                }
                QPushButton:hover {
                    border-color: #4C7DFF;
                    background: rgba(76,125,255,0.2);
                    color: #F1F4F8;
                }
                QPushButton:pressed {
                    background: rgba(76,125,255,0.3);
                }
            """)

        # OK butonunu daha belirgin yap
        self.btn_ok.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                font-weight: 700;
                padding: 10px 18px;
                border-radius: 8px;
                background: rgba(76,125,255,0.15);
                border: 2px solid rgba(76,125,255,0.6);
                color: #F1F4F8;
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                background: rgba(76,125,255,0.25);
                border-color: #4C7DFF;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background: rgba(76,125,255,0.35);
            }
        """)

        bottom.addWidget(self.btn_cancel)
        bottom.addWidget(self.btn_ok)
        v.addLayout(bottom)

        # signals
        self.ed_search.textChanged.connect(self._apply_filter)
        self.cmb_cat.currentTextChanged.connect(self._apply_filter)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_ok.clicked.connect(self.accept)

        # Satır tıklama ile checkbox toggle - KALDIRILDI (Qt.ItemIsUserCheckable zaten çalışıyor)
        # self.tbl.itemClicked.connect(self._on_item_clicked)
        # self.tbl.itemDoubleClicked.connect(self._on_item_double_clicked)

        # Hover'da imleç değişimi için event filter
        self.tbl.viewport().installEventFilter(self)

        self._extras_by_code: dict[str, dict] = {}  # { "STK0001": {"Milyem":"916","Iscilik":39.50,"Foto":"..."} }

        # Ana sales sayfası ile aynı tema
        try:
            from theme import apply_dialog_theme
            apply_dialog_theme(self, "dim")
        except Exception:
            pass

    def _on_item_clicked(self, item):
        """Artık kullanılmıyor - Qt.ItemIsUserCheckable çalışıyor"""
        return

    def _on_item_double_clicked(self, item):
        """Artık kullanılmıyor - Qt.ItemIsUserCheckable çalışıyor"""
        return

    def eventFilter(self, obj, event):
        if obj is self.tbl.viewport() and event.type() == QEvent.Type.MouseMove:
            idx = self.tbl.indexAt(event.position().toPoint())
            if idx.isValid() and idx.column() == 5:
                self.tbl.viewport().setCursor(Qt.CursorShape.PointingHandCursor)
            else:
                self.tbl.viewport().unsetCursor()
        return super().eventFilter(obj, event)

    def _toggle_row_check(self, r):
        """Satırın checkbox'ını toggle eder"""
        it = self.tbl.item(r, 0)
        if it:
            it.setCheckState(Qt.CheckState.Unchecked if it.checkState() == Qt.CheckState.Checked else Qt.CheckState.Checked)

    def _apply_filter(self):
        q = self.ed_search.text().strip().lower()
        cat = self.cmb_cat.currentText()
        self.tbl.setRowCount(0)

        for p in self._all_products:
            if cat != "Tümü" and p["Kategori"] != cat:
                continue
            hay = f'{p["Kod"]} {p["Ad"]} {p["Kategori"]}'.lower()
            if q and q not in hay:
                continue
            self._append_product_row(p)

    def _append_product_row(self, p):
        r = self.tbl.rowCount()
        self.tbl.insertRow(r)

        # --- Seç (checkable item, widget değil)
        it_sel = QTableWidgetItem("")
        it_sel.setFlags(it_sel.flags() | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        it_sel.setCheckState(Qt.CheckState.Unchecked)
        it_sel.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tbl.setItem(r, 0, it_sel)

        # --- Kod / Ürün / Kategori
        self.tbl.setItem(r, 1, QTableWidgetItem(p["Kod"]))
        self.tbl.setItem(r, 2, QTableWidgetItem(p["Ad"]))
        self.tbl.setItem(r, 3, QTableWidgetItem(p["Kategori"]))

        # --- Gram (metin, sağa hizalı)
        gram_val = float(p.get("Gram", 0.0))
        it_g = QTableWidgetItem(f"{gram_val:.2f}")
        it_g.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        it_g.setData(Qt.ItemDataRole.UserRole, gram_val)
        self.tbl.setItem(r, 4, it_g)

        # --- Adet (kalıcı spinbox)
        it_a = QTableWidgetItem("")  # metin yok
        it_a.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        it_a.setData(Qt.ItemDataRole.UserRole, 1)  # gerçek değer burada
        it_a.setData(Qt.ItemDataRole.DisplayRole, "")  # garantiye almak için
        # Kalıcı editör çalışsın diye editable bırakıyoruz
        it_a.setFlags(Qt.ItemFlag.ItemIsSelectable |
                      Qt.ItemFlag.ItemIsEnabled   |
                      Qt.ItemFlag.ItemIsEditable)
        it_a.setToolTip("Sayı tuşları, +/− ve ↑/↓ ile değiştirin")
        it_a.setBackground(QColor(76, 125, 255, 36))
        self.tbl.setItem(r, 5, it_a)

        # >>> en kritik satır: kalıcı editörü aç
        self.tbl.openPersistentEditor(it_a)

        # --- Birim Fiyat (₺ metin)
        price = float(p.get("Fiyat", 0.0))
        it_f = QTableWidgetItem(tl(price))
        it_f.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        it_f.setData(Qt.ItemDataRole.UserRole, price)
        self.tbl.setItem(r, 6, it_f)

        # --- Stok
        it_s = QTableWidgetItem(str(p.get("Stok","-")))
        it_s.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        if p.get("Stok", 0) <= 5:
            it_s.setBackground(QColor(244, 67, 54, 60))
            it_s.setForeground(QColor(255,255,255))
        self.tbl.setItem(r, 7, it_s)

        # --- Milyem (okunur) başlangıç boş
        it_m = QTableWidgetItem("")        # gösterim
        it_m.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tbl.setItem(r, 8, it_m)

        # --- İşçilik (₺, okunur)
        it_i = QTableWidgetItem("")        # gösterim
        it_i.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.tbl.setItem(r, 9, it_i)

        # --- Detay butonu (tüm hücreyi kaplar)
        cell = QWidget()
        lay = QHBoxLayout(cell)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        btn = QPushButton("Detay")
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        btn.setProperty("small", True)
        btn.setStyleSheet("""
            QPushButton {
                /* hücreyi tam kapla */
                margin: 0; padding: 0; border-radius: 0;
                background: rgba(76,125,255,0.15);
                border: 1px solid rgba(76,125,255,0.5);
                color: #E9EDF2; font-weight: 700;
            }
            QPushButton:hover {
                background: rgba(76,125,255,0.25);
            }
        """)

        btn.clicked.connect(self._on_detail_clicked)
        lay.addWidget(btn)
        self.tbl.setCellWidget(r, 10, cell)

    def _on_detail_clicked(self):
        btn = self.sender()
        if not btn:
            return
        # Buton, hücre içindeki QWidget'in (cell) içinde: parent() = cell
        cell_widget = btn.parent()
        idx = self.tbl.indexAt(cell_widget.pos())
        row = idx.row()
        if row < 0:
            return

        # Kodu tablodan al (tekil anahtar)
        kod = self.tbl.item(row, 1).text()

        initial = self._extras_by_code.get(kod, {})
        d = ItemDetailDialog(self, initial)
        if d.exec():
            data = d.data()
            self._extras_by_code[kod] = data
            # Hücreleri güncelle
            self.tbl.item(row, 8).setText(data.get("Milyem", ""))
            isc = float(data.get("Iscilik", 0.0))
            self.tbl.item(row, 9).setText(tl(isc))

    def data(self) -> list[dict]:
        """Seçili checkbox'lı satırları döndürür."""
        rows = []
        for r in range(self.tbl.rowCount()):
            it_sel = self.tbl.item(r, 0)
            if not it_sel or it_sel.checkState() != Qt.CheckState.Checked:
                continue

            # Adet değerini UserRole'dan al (spinbox doğrudan güncelliyor)
            adet = int(self.tbl.item(r, 5).data(Qt.ItemDataRole.UserRole) or 1)

            kod = self.tbl.item(r, 1).text()
            extra = self._extras_by_code.get(kod, {})
            rows.append({
                "Kod":        kod,
                "Ad":         self.tbl.item(r, 2).text(),
                "Gram":       float(self.tbl.item(r, 4).data(Qt.ItemDataRole.UserRole) or 0.0),
                "Adet":       adet,
                "BirimFiyat": float(self.tbl.item(r, 6).data(Qt.ItemDataRole.UserRole) or 0.0),
                "Milyem":     extra.get("Milyem",""),
                "Iscilik":    float(extra.get("Iscilik", 0.0)),
                "Foto":       extra.get("Foto",""),
            })
        return rows

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

# === Tek ürün detay diyaloğu (Milyem / İşçilik / Foto) =======================
from PyQt6.QtWidgets import QFileDialog, QTextEdit, QDialogButtonBox

class ItemDetailDialog(QDialog):
    def __init__(self, parent=None, initial: dict|None=None):
        super().__init__(parent)
        self.setWindowTitle("Ürün Detayı")
        self.setModal(True)
        self.setMinimumWidth(420)

        v = QVBoxLayout(self); v.setContentsMargins(16,16,16,16); v.setSpacing(12)
        card = QFrame(self); card.setObjectName("Glass")
        body = QVBoxLayout(card); body.setContentsMargins(16,16,16,16); body.setSpacing(12)
        v.addWidget(card)

        title = QLabel("Milyem • İşçilik • Fotoğraf")
        title.setProperty("variant","title")
        body.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setHorizontalSpacing(12); form.setVerticalSpacing(10)

        self.cmb_milyem = QComboBox()
        self.cmb_milyem.addItems(["916", "900", "875", "835", "750", "585", "375"])
        self.sp_iscilik = QDoubleSpinBox(); self.sp_iscilik.setRange(0,1_000_000); self.sp_iscilik.setDecimals(2)
        self.sp_iscilik.setSuffix(" ₺")

        self.ed_foto = QLineEdit(); self.ed_foto.setReadOnly(True)
        btn_foto = QPushButton("Seç…")
        def pick():
            p, _ = QFileDialog.getOpenFileName(self, "Ürün Fotoğrafı", "", "Görseller (*.png *.jpg *.jpeg *.webp)")
            if p:
                import os
                if os.path.exists(p):
                    self.ed_foto.setText(p)
                else:
                    QMessageBox.warning(self, "Dosya Bulunamadı",
                        f"Seçilen dosya bulunamıyor:\n{p}\n\n"
                        f"Lütfen geçerli bir dosya seçin.")
        btn_foto.clicked.connect(pick)

        row = QHBoxLayout(); row.addWidget(self.ed_foto,1); row.addWidget(btn_foto)

        form.addRow("Milyem", self.cmb_milyem)
        form.addRow("İşçilik", self.sp_iscilik)
        form.addRow("Fotoğraf", row)
        body.addLayout(form)

        # Düzenleme
        if initial:
            if initial.get("Milyem"): self.cmb_milyem.setCurrentText(str(initial["Milyem"]))
            try: self.sp_iscilik.setValue(float(initial.get("Iscilik",0.0)))
            except: pass
            self.ed_foto.setText(initial.get("Foto",""))

        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        body.addWidget(btns)

        # tema
        try:
            from theme import apply_dialog_theme
            apply_dialog_theme(self,"dim")
        except Exception:
            pass

    def data(self):
        return {
            "Milyem": self.cmb_milyem.currentText(),
            "Iscilik": float(self.sp_iscilik.value()),
            "Foto": self.ed_foto.text().strip(),
        }

class SalesPage(QWidget):
    """Alış–Satış işlemleri (DB entegrasyonu ile)"""

    # Finans sayfası dinleyebilsin diye sinyal
    transactionCommitted = pyqtSignal(dict)  # payload: finans kaydı

    def __init__(self, data=None, parent=None):
        super().__init__(parent)
        self.data = data

        # Seed (bir kere)
        try:
            from pages.sales import PRODUCTS, CUSTOMERS  # senin dosyadaki listeler
        except Exception:
            PRODUCTS, CUSTOMERS = [], []
        if self.data:
            self.data.seed_if_empty(CUSTOMERS, PRODUCTS)


        # — kozmik arka plan
        self._sky = QLabel(self)
        self._sky.lower()  # en arkada dursun
        self._sky.setScaledContents(True)
        self._sky.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Performance için debounce timer
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._on_resize_timeout)

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
        form.setContentsMargins(12, 8, 12, 8)
        form.setSpacing(6)

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
        row_customer = QHBoxLayout()
        self.lbl_customer = QLabel("Müşteri")
        self.lbl_customer.setStyleSheet("color: #B7C0CC; font-size: 11px; font-weight: 500;")
        self.cmb_customer = QComboBox()
        self.cmb_customer.addItems(CUSTOMERS)
        self.cmb_customer.setCurrentIndex(-1)  # boş başlasın
        self.cmb_customer.setStyleSheet(f"QComboBox{{{small_input_css} min-width: 200px;}}"
                                        "QComboBox::drop-down{border:none;width:16px;}"
                                        "QComboBox QAbstractItemView{background:rgba(28,34,44,0.98);color:#E9EDF2;border:1px solid rgba(255,255,255,0.08);selection-background-color:#4C7DFF;padding:4px;}")
        btn_new_cari = QPushButton("+ Yeni")
        btn_new_cari.setFixedWidth(64)
        btn_new_cari.setStyleSheet("""
            QPushButton { padding: 6px 10px; border-radius: 8px;
            background: rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.12); }
            QPushButton:hover { border-color:#97B7FF; background: rgba(76,125,255,0.10); }
        """)
        row_customer.addWidget(self.cmb_customer, 1)
        row_customer.addWidget(btn_new_cari, 0, Qt.AlignmentFlag.AlignBottom)
        customer_layout.addWidget(self.lbl_customer)
        customer_layout.addLayout(row_customer)
        first_row.addLayout(customer_layout, 1)

        # Buton davranışı + completer
        def _on_new_cari():
            # Müşteri kutusundaki mevcut yazıyı al ve dialog'a aktar
            current_text = self.cmb_customer.currentText().strip()

            # Eğer mevcut bir müşteri seçiliyse, onu kullan
            if current_text and " — " in current_text:
                ad_soyad, telefon = current_text.split(" — ", 1)
                initial_data = {"AdSoyad": ad_soyad.strip(), "Telefon": telefon.strip()}
            else:
                # Yazılan metni ad-soyad olarak kullan
                initial_data = {"AdSoyad": current_text, "Telefon": ""}

            dlg = NewCustomerDialog(self, initial_data)
            if dlg.exec():
                d = dlg.data()
                new_customer_text = f"{d['AdSoyad']} — {d['Telefon']}"
                self.cmb_customer.addItem(new_customer_text)
                self.cmb_customer.setCurrentIndex(self.cmb_customer.count()-1)
                self._apply_customer_completer()
        btn_new_cari.clicked.connect(_on_new_cari)
        self._apply_customer_completer()

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

        self.btn_add = QPushButton("Toplu Ürün Seç")
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
        splitter.setHandleWidth(5)

        # Sol: tablo kartı
        table_card = QFrame(objectName="Glass")
        elevate(table_card, "dim", blur=28, y=8)
        tlayout = QVBoxLayout(table_card)
        tlayout.setContentsMargins(10, 10, 10, 10)
        tlayout.setSpacing(6)

        lbl_items = QLabel("İşlem Satırları")
        lbl_items.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_items.setStyleSheet("color: #E9EDF2; margin-bottom: 4px;")
        tlayout.addWidget(lbl_items)

        self.table = QTableWidget(0, 8, self)
        self.table.setHorizontalHeaderLabels(["Kod","Ürün","Gram","Adet","Milyem","İşçilik (Toplam)","Birim Fiyat","Tutar"])
        self.table.verticalHeader().setVisible(False)
        self.table.setCornerButtonEnabled(False)

        # satır yüksekliğini biraz artır (okunurluk) ama alanı iyi kullan
        self.table.verticalHeader().setDefaultSectionSize(44)   # 42→44
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.itemSelectionChanged.connect(self._toggle_actions)
        # Tablo değişikliklerinde save button durumunu güncelle
        self.table.model().rowsInserted.connect(lambda: self._update_save_button_state())
        self.table.model().rowsRemoved.connect(lambda: self._update_save_button_state())

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
        hdr.setDefaultSectionSize(110)                           # 120→110
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
        hdr.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed); self.table.setColumnWidth(4, 70)   # Milyem
        hdr.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed); self.table.setColumnWidth(5, 110)  # İşçilik
        hdr.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(6, 110)
        hdr.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(7, 110)

        tlayout.addWidget(self.table)

        splitter.addWidget(table_card)
        splitter.setStretchFactor(0, 2)  # Sol panel (index 0) 2 birim büyüme

        # Sağ: özet panel - YENİDEN TASARLANDI
        right = QFrame(objectName="Glass")
        elevate(right, "dim", blur=28, y=8)

        # Eskisi: QVBoxLayout
        # r_layout = QVBoxLayout(right)
        # r_layout.setContentsMargins(16, 16, 16, 16)
        # r_layout.setSpacing(16)

        # YENİ: tek sütunlu grid
        from PyQt6.QtWidgets import QGridLayout
        r_grid = QGridLayout(right)
        r_grid.setContentsMargins(12, 12, 12, 12)
        r_grid.setHorizontalSpacing(12)
        r_grid.setVerticalSpacing(12)

        # Fiyatlandırma paneli yok: varsayılan parametreler
        self._base_price = 3500.0   # 24K baz
        self._markup     = 0.0      # %
        self._round_step = 10.0     # ₺

        # --- 1. İşlem Özeti (responsive grid, indirim yok) ---
        summary_group = QGroupBox("İşlem Özeti")
        summary_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px; font-weight: 600; color: #E9EDF2;
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 12px;
                padding: 8px 10px 10px 10px;
                margin-top: 0px;
                background: rgba(255,255,255,0.03);
            }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 2px 6px; }
            QLabel[data='label'] { color: #B7C0CC; font-weight: 600; font-size: 12px; }
            QLabel#pill {
                padding: 6px 10px; border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.10);
                background: rgba(255,255,255,0.05);
                color: #E9EDF2; font-weight: 700; min-height: 26px;
                qproperty-alignment: 'AlignCenter';
                font-size: 12px;
            }
            QLabel#total {
                padding: 8px 12px; border-radius: 12px;
                border: 1px solid rgba(76,125,255,0.35);
                background: rgba(76,125,255,0.12);
                color: #E9EDF2; font-weight: 800; min-height: 34px; font-size: 13px;
                qproperty-alignment: 'AlignCenter';
            }
        """)

        from PyQt6.QtWidgets import QGridLayout
        self._summary_grid = QGridLayout(summary_group)
        self._summary_grid.setContentsMargins(6, 6, 6, 6)
        self._summary_grid.setHorizontalSpacing(8)
        self._summary_grid.setVerticalSpacing(6)

        # Etiket + değer kutuları (İNDİRİM YOK)
        lbl_items   = QLabel("Ürün");         lbl_items.setProperty("data","label")
        lbl_sub     = QLabel("Ara Top.");     lbl_sub.setProperty("data","label")
        lbl_grand   = QLabel("Genel Toplam"); lbl_grand.setProperty("data","label")

        self.lbl_sum_count = QLabel("0");   self.lbl_sum_count.setObjectName("pill")
        self.lbl_sum_sub   = QLabel(tl(0)); self.lbl_sum_sub.setObjectName("pill")
        self.lbl_sum_total = QLabel(tl(0)); self.lbl_sum_total.setObjectName("total")

        # Responsive yerleşim için bir liste tutalım (etiket, değer) çiftleri
        self._summary_pairs = [
            (lbl_items, self.lbl_sum_count),
            (lbl_sub,   self.lbl_sum_sub),
            (lbl_grand, self.lbl_sum_total),
        ]

        # DİKEL 3 satır: her satır "etiket | değer"
        self._apply_summary_layout(self._summary_grid, max_cols=1)

        r_grid.addWidget(summary_group, 0, 0)

        # --- 2. Ödeme Bilgileri Grubu — net 2x2 grid
        payment_group = QGroupBox("Ödeme Bilgileri")
        payment_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px; font-weight: 600; color: #E9EDF2;
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 12px;
                padding: 8px 10px 10px 10px;   /* daha dar */
                margin-top: 8px;
                background: rgba(255,255,255,0.03);
            }
            QGroupBox::title { subcontrol-origin: margin; left: 12px; padding: 2px 6px; }
        """)

        # daha kısa kontrol yüksekliği
        CTRL_H = 40

        from PyQt6.QtWidgets import QSizePolicy
        payment_group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        payment_group.setMaximumHeight(170)   # 150–180 arası deneyebilirsin

        from PyQt6.QtWidgets import QGridLayout
        grid = QGridLayout(payment_group)
        grid.setContentsMargins(8, 8, 8, 8)
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)

        common_pay_css = """
            padding: 8px 10px; border-radius: 10px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.12);
            color: #E9EDF2; font-size: 13px;
        """

        # Sol-üst: Ödeme türü
        self.cmb_pay = QComboBox()
        self.cmb_pay.addItems(["Nakit","Kart","Havale","Veresiye"])
        self.cmb_pay.setCurrentIndex(0)
        self.cmb_pay.setFixedHeight(CTRL_H)
        self.cmb_pay.setStyleSheet(f"""
            QComboBox {{ {common_pay_css} }}
            QComboBox::drop-down {{ border:none; width:16px; }}
            QComboBox QAbstractItemView {{
                background: rgba(28,34,44,0.98); color:#E9EDF2;
                border: 1px solid rgba(255,255,255,0.08);
                selection-background-color:#4C7DFF; padding:6px; font-size:13px;
            }}
        """)

        # Sağ-üst: Alınan tutar
        self.in_paid = QDoubleSpinBox()
        self.in_paid.setRange(0, 1_000_000); self.in_paid.setDecimals(2)
        self.in_paid.setPrefix("₺ "); self.in_paid.setGroupSeparatorShown(True)
        self.in_paid.setLocale(TR); self.in_paid.setButtonSymbols(self.in_paid.ButtonSymbols.NoButtons)
        self.in_paid.setFixedHeight(CTRL_H)
        self.in_paid.setStyleSheet(f"QDoubleSpinBox {{ {common_pay_css} }} QDoubleSpinBox:focus {{ border-color:#4C7DFF; background: rgba(76,125,255,0.08); }}")

        # Sol-alt: Büyük toplam (küçük font, kompakt)
        self._total_big = QLabel("Genel Toplam: 0 ₺")
        self._total_big.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._total_big.setFixedHeight(CTRL_H)
        self._total_big.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))  # 15 → 14
        self._total_big.setStyleSheet("""
            QLabel {
                color:#E9EDF2; padding:8px 12px;
                border-radius:10px;
                border:1px solid rgba(255,255,255,0.12);
                background: rgba(255,255,255,0.06);
                font-weight:800;
            }
        """)

        # Sağ-alt: Para üstü / kalan
        self.lbl_change = QLabel("Para Üstü: 0 ₺")
        self.lbl_change.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_change.setFixedHeight(CTRL_H)
        self.lbl_change.setStyleSheet("""
            QLabel {
                color:#2ECC71; font-weight:700; font-size:13px;
                padding:8px 12px; border-radius:10px;
                background: rgba(46,204,113,0.12);
                border: 1px solid rgba(46,204,113,0.28);
            }
        """)
        self.lbl_remaining = QLabel("Kalan (Veresiye): 0 ₺")
        self.lbl_remaining.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_remaining.setFixedHeight(CTRL_H)
        self.lbl_remaining.setVisible(False)
        self.lbl_remaining.setStyleSheet("""
            QLabel {
                color:#FF6B6B; font-weight:700; font-size:13px;
                padding:8px 12px; border-radius:10px;
                background: rgba(255,107,107,0.12);
                border: 1px solid rgba(255,107,107,0.28);
            }
        """)

        # 2×2 yerleşim
        grid.addWidget(self.cmb_pay,    0, 0)
        grid.addWidget(self.in_paid,    0, 1)
        grid.addWidget(self._total_big, 1, 0)
        grid.addWidget(self.lbl_change, 1, 1)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        # satırlar arasında ince ayırıcı istersen:
        line = QFrame(); line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: rgba(255,255,255,0.08);")
        # grid.addWidget(line, 2, 0, 1, 2)   # istersen aç
        r_grid.addWidget(payment_group, 1, 0)

        # Ana aksiyon butonları – sadece kaydet (makbuz otomatik)
        self.btn_save  = QPushButton("İşlemi Kaydet")

        for btn in (self.btn_save,):
            btn.setMinimumHeight(44)   # 48 → 44
            btn.setMaximumHeight(44)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setStyleSheet("""
                QPushButton {
                    padding: 10px 16px;        /* ↑ */
                    border-radius: 12px;
                    background: rgba(76,125,255,0.14);
                    border: 1px solid rgba(76,125,255,0.38);
                    color: #E9EDF2;
                    font-size: 14px; font-weight: 700;            /* ↑ */
                }
                QPushButton:hover { border-color:#97B7FF; background: rgba(76,125,255,0.22); }
                QPushButton:pressed { background: rgba(76,125,255,0.30); }
            """)

        actions_row = QHBoxLayout()
        actions_row.setSpacing(10)
        actions_row.addWidget(self.btn_save)

        actions_bar = QWidget()
        actions_bar.setLayout(actions_row)
        r_grid.addWidget(actions_bar, 2, 0)  # en alt sıra

        # Gruplar dikeyde esnesin, buton sabit kalsın, boş satır olmasın
        r_grid.setColumnStretch(0, 1)
        r_grid.setRowStretch(0, 2)   # Özet daha çok yer kaplasın
        r_grid.setRowStretch(1, 0)   # Ödeme sabit/kısa
        r_grid.setRowStretch(2, 0)   # Buton sabit
        # r_grid.setRowStretch(3, 1)  # ← KALDIR (boş satır istemiyoruz)

        right.setMinimumWidth(360)
        right.setMaximumWidth(420)   # sağ panel sabit dar

        splitter.addWidget(right)
        splitter.setStretchFactor(0, 6)  # sol taraf ezici çoğunluk
        splitter.setStretchFactor(1, 1)

        root.addWidget(splitter, 1)

        # olaylar
        self.btn_add.clicked.connect(self.bulk_add_items)
        self.btn_edit.clicked.connect(self.edit_item)
        self.btn_del.clicked.connect(self.remove_item)
        self.btn_save.clicked.connect(self.save_transaction)
        self.in_paid.valueChanged.connect(self._recalc_change)
        self.cmb_pay.currentTextChanged.connect(self._on_payment_type_changed)
        self.cmb_customer.currentTextChanged.connect(self._update_save_button_state)

        # Başlangıç durumu için olayları tetikle
        self._on_payment_type_changed(self.cmb_pay.currentText())
        self._update_save_button_state()

        # ilk oran
        QTimer.singleShot(0, lambda: splitter.setSizes([self.width()-420, 420]))
        QTimer.singleShot(0, lambda: self._paint_sky(self.width(), self.height()))

    # — yardımcılar
    def _update_save_button_state(self):
        """Cari seçilmediğinde Kaydet butonunu disable et"""
        has_customer = bool(self.cmb_customer.currentText().strip())
        has_items = self.table.rowCount() > 0
        self.btn_save.setEnabled(has_customer and has_items)

    def _apply_customer_completer(self):
        from PyQt6.QtWidgets import QCompleter
        self.cmb_customer.setEditable(True)
        self.cmb_customer.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        comp = QCompleter([self.cmb_customer.itemText(i) for i in range(self.cmb_customer.count())], self.cmb_customer)
        comp.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        comp.setFilterMode(Qt.MatchFlag.MatchContains)  # ortadan da eşleşsin

        # Tema uyumlu popup stili
        comp.popup().setStyleSheet("""
            QAbstractItemView {
                background: rgba(28,34,44,0.98);
                color: #E9EDF2;
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 6px;
                selection-background-color: rgba(76,125,255,0.2);
                selection-color: #F1F4F8;
                padding: 4px;
                outline: none;
            }
            QAbstractItemView::item {
                padding: 8px 12px;
                border-radius: 4px;
                margin: 1px;
            }
            QAbstractItemView::item:hover {
                background: rgba(76,125,255,0.1);
                color: #F1F4F8;
            }
            QAbstractItemView::item:selected {
                background: rgba(76,125,255,0.3);
                color: #FFFFFF;
            }
        """)

        self.cmb_customer.setCompleter(comp)
        # Boş metinle başlat (kullanıcı yazsın)
        self.cmb_customer.setCurrentIndex(-1)
        self.cmb_customer.setEditText("")

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
            # Debounce ile paint çağrısı - çok sık resize'de performans sorunu önler
            self._resize_timer.start(100)  # 100ms debounce

        # Özet her zaman 1 kolon (3 satır) kalsın
        try:
            if hasattr(self, '_summary_grid'):
                self._apply_summary_layout(self._summary_grid, max_cols=1)
        except Exception:
            pass

    def _on_resize_timeout(self):
        """Resize tamamlandıktan sonra sky'i yeniden çiz"""
        if hasattr(self, '_sky'):
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
            total += float(self.table.item(i, 7).data(Qt.ItemDataRole.UserRole) or 0.0)
        return total

    def _guess_milyem(self, name: str, category: str = "") -> float:
        t = (name or "").lower()
        if "külçe" in t or "gram altın" in t or "24" in t:  # saf
            return 995
        if "22" in t: return 916
        if "18" in t: return 750
        if "14" in t: return 585
        return 916  # varsayılan

    def _round_to_step(self, v: float) -> float:
        # Panel yoksa _round_step kullan
        try:
            if hasattr(self, "cmb_round"):
                step = float(self.cmb_round.currentText())
            else:
                step = getattr(self, "_round_step", 10.0)
        except Exception:
            step = getattr(self, "_round_step", 10.0)
        if step <= 0:
            return v
        # .5 ve üstünü hep yukarı at (banker rounding sorununu çöz)
        import math
        return math.floor(v / step + 0.5) * step

    def _refresh_row_pricing(self, r: int):
        # temel alanlar
        gram = float(str(self.table.item(r, 2).text()).replace(",", ".") or 0.0)
        adet = int(self.table.item(r, 3).text() or "1")
        name = self.table.item(r, 1).text()

        # milyem (boşsa üründen tahmin et ve hücreye yaz)
        mil_txt = (self.table.item(r, 4).text() or "").strip()
        if mil_txt:
            try: mil = float(mil_txt.replace(",", "."))
            except: mil = self._guess_milyem(name)
        else:
            mil = self._guess_milyem(name)
            self.table.item(r, 4).setText(str(int(mil)))

        base   = float(self.sp_base_price.value()) if hasattr(self, "sp_base_price") else getattr(self, "_base_price", 3500.0)
        markup = float(self.sp_markup.value())     if hasattr(self, "sp_markup")     else getattr(self, "_markup", 0.0)
        isc    = float(self.table.item(r, 5).data(Qt.ItemDataRole.UserRole) or 0.0)

        # İşçilik sütununda toplam işçiliği göster (ekranda adet*isc, hesapta isc)
        it_isc = self.table.item(r, 5)
        if it_isc:
            it_isc.setText(tl(adet * isc))  # Ekranda toplam işçilik
            # UserRole'da birim işçilik kalsın (hesaplamalar için)

        # Birim Fiyat = Gram × (Milyem/1000) × Baz × (1+Kâr)
        raw_unit = gram * (mil / 1000.0) * base
        unit_with_markup = raw_unit * (1.0 + markup / 100.0)
        unit_price = self._round_to_step(unit_with_markup)

        # kol.6: Birim Fiyat
        it_price = self.table.item(r, 6)
        if it_price is None:
            it_price = QTableWidgetItem()
            it_price.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(r, 6, it_price)
        it_price.setData(Qt.ItemDataRole.UserRole, unit_price)
        it_price.setText(tl(unit_price))

        # kol.7: Tutar = adet*(birim + işçilik)
        total = adet * (unit_price + isc)   # veya: adet*unit_price + adet*isc
        it_total = self.table.item(r, 7)
        if it_total is None:
            it_total = QTableWidgetItem()
            it_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(r, 7, it_total)
        it_total.setData(Qt.ItemDataRole.UserRole, total)
        it_total.setText(tl(total))

    def _reprice_all(self):
        for r in range(self.table.rowCount()):
            self._refresh_row_pricing(r)
        self._recalc()

    def _calc_row_total(self, r: int) -> float:
        # toplam tutarı güvenle üret (gerekirse satırı tazeler)
        self._refresh_row_pricing(r)
        return float(self.table.item(r, 7).data(Qt.ItemDataRole.UserRole) or 0.0)

    def _apply_summary_layout(self, grid, max_cols: int):
        """Flex benzeri: verilen sütun sayısına göre (etiket, değer) çiftlerini ızgaraya dizer."""
        # Önce mevcut item'ları temizle
        while grid.count():
            item = grid.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
        # Çiftleri sırayla doldur
        r = c = 0
        for (lab, val) in self._summary_pairs:
            grid.addWidget(lab, r, c)
            grid.addWidget(val, r, c+1)
            # her bir çift 2 sütun kullanıyor → sonraki blok
            c += 2
            if c >= (max_cols * 2):
                r += 1
                c = 0
        # Esneme — değer sütunları esnesin
        total_cols = min(max_cols, max(1, len(self._summary_pairs))) * 2
        for i in range(total_cols):
            grid.setColumnStretch(i, 1 if i % 2 == 1 else 0)  # değer sütunları 1

    def _recalc(self):
        rows = self.table.rowCount()
        total = self._calc_total()
        self.lbl_sum_count.setText(f"{rows}")
        self.lbl_sum_sub.setText(f"{tl(total)}")
        self.lbl_sum_total.setText(f"{tl(total)}")
        self._total_big.setText(f"Genel Toplam: {tl(total)}")
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
        self._apply_customer_completer()

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

            # Otomatik doldurma: kullanıcı hiç yazmadıysa (0.00) total'i öner
            if total > 0 and paid == 0.0:
                self.in_paid.blockSignals(True)
                self.in_paid.setValue(total)
                self.in_paid.blockSignals(False)
                paid = total

            if paid < total and paid > 0:
                # Eksik ödeme durumunda kırmızı uyarı
                self.lbl_change.setText(f"Eksik: {tl(total - paid)}")
                self.lbl_change.setStyleSheet("""
                    QLabel {
                        color: #FF6B6B; font-weight: 600; padding: 8px 10px;
                        border-radius: 10px; background: rgba(255,107,107,0.10);
                        border: 1px solid rgba(255,107,107,0.25);
                    }
                """)
            else:
                # Normal para üstü veya tam ödeme
                change = max(0.0, paid - total)
                self.lbl_change.setText(f"Para Üstü: {tl(change)}")
                self.lbl_change.setStyleSheet("""
                    QLabel {
                        color: #2ECC71; font-weight: 600; padding: 8px 10px;
                        border-radius: 10px; background: rgba(46,204,113,0.10);
                        border: 1px solid rgba(46,204,113,0.25);
                    }
                """)
            if self.lbl_remaining.parentWidget() is not None:
                parent = self.lbl_remaining.parentWidget().layout()
                if parent is not None:
                    parent.replaceWidget(self.lbl_remaining, self.lbl_change)

    # — satır işlemleri (mock)
    def bulk_add_items(self):
        dlg = MultiProductPickerDialog(self, PRODUCTS)
        if not dlg.exec():
            return
        items = dlg.data()
        if not items:
            return
        # Stok kontrolü + ekleme
        for d in items:
            product = next((p for p in PRODUCTS if p["Kod"] == d["Kod"]), None)
            if product and self.cmb_type.currentText() == "Satış":
                if d["Adet"] > product.get("Stok", 0):
                    QMessageBox.warning(self, "Stok Uyarısı",
                                        f"{product['Ad']} için yeterli stok yok!\n"
                                        f"Mevcut: {product['Stok']} adet • İstenen: {d['Adet']}")
                    continue
            self._append_row(d)
        self._recalc()


    def edit_item(self):
        row = self._selected_row()
        if row is None:
            return

        current = {
            "Kod": self.table.item(row,0).text(),
            "Ad":  self.table.item(row,1).text(),
            "Gram": float(self.table.item(row,2).text().replace(",", ".")),
            "Adet": int(self.table.item(row,3).text()),
            "BirimFiyat": float(self.table.item(row,6).data(Qt.ItemDataRole.UserRole) or 0.0),  # <- 6. sütun
            # >>> EK: mevcut milyem & işçilik’i dialoga taşı
            "Milyem": self.table.item(row,4).text().strip(),
            "Iscilik": float(self.table.item(row,5).data(Qt.ItemDataRole.UserRole) or 0.0),
        }

        dlg = NewSaleItemDialog(self, PRODUCTS, current)
        if dlg.exec():
            data = dlg.data()
            self._set_row(row, data)
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
        d.setdefault("Milyem", str(int(self._guess_milyem(d.get("Ad",""), ""))))
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

        # Milyem
        mil = str(d.get("Milyem",""))
        it_m = QTableWidgetItem(mil)
        it_m.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(r,4, it_m)

        # İşçilik
        isc = float(d.get("Iscilik", 0.0))
        it_i = QTableWidgetItem(tl(isc))
        it_i.setData(Qt.ItemDataRole.UserRole, isc)
        it_i.setTextAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(r,5, it_i)

        # 6. sütun (Birim Fiyat) — formülden hesaplanacağı için boş item oluştur
        it_price = QTableWidgetItem()
        it_price.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(r, 6, it_price)

        # 7. sütun (Tutar) için placeholder
        it_total = QTableWidgetItem()
        it_total.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(r, 7, it_total)

        # SON: bu satırı formüle göre fiyatla
        self._refresh_row_pricing(r)

    def _row_to_item(self, r: int) -> dict:
        """Tablo satırını DB item dict'ine çevir"""
        def to_float(txt):
            return parse_money(txt)

        code = self.table.item(r, 0).text()
        name = self.table.item(r, 1).text()
        gram = float(self.table.item(r, 2).text() or 0)
        qty = int(self.table.item(r, 3).text() or 1)
        milyem = self.table.item(r, 4).text() or ""
        isc_item = self.table.item(r, 5)
        iscilik = isc_item.data(Qt.ItemDataRole.UserRole) if isc_item else 0.0
        unit_price = to_float(self.table.item(r, 6).text())
        line_total = to_float(self.table.item(r, 7).text())

        return {
            "code": code, "name": name, "gram": gram, "qty": qty, "milyem": milyem,
            "iscilik": float(iscilik or 0.0), "unit_price": unit_price, "line_total": line_total
        }

    def save_transaction(self):
        """DB'ye işlemleri kaydet"""
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Uyarı", "Kaydedilecek satır bulunamadı!")
            return
        if not self.cmb_customer.currentText().strip():
            QMessageBox.warning(self, "Uyarı", "Lütfen bir cari seçin.")
            return

        # Etkin ödeme hesapla
        total_amount = self._calc_total()
        paid_req = float(self.in_paid.value()) if self.cmb_pay.currentText() != "Veresiye" else 0.0
        paid_eff = min(paid_req, total_amount)  # para üstü hariç net tahsilat

        if self.cmb_pay.currentText() != "Veresiye" and paid_req < total_amount:
            reply = QMessageBox.question(self, "Eksik Ödeme Onayı",
                f"Ödeme tutarı toplam tutardan az!\n\n"
                f"Toplam Tutar: {tl(total_amount)}\n"
                f"Ödenen Tutar: {tl(paid_req)}\n"
                f"Eksik Tutar: {tl(total_amount - paid_req)}\n\n"
                f"İşlemi eksik ödeme ile kaydetmek istiyor musunuz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return

        # DB'ye kaydet
        if not self.data:
            QMessageBox.critical(self, "Hata", "Veritabanı bağlantısı yok!")
            return

        items = [self._row_to_item(r) for r in range(self.table.rowCount())]
        header = {
            "type": self.cmb_type.currentText(),  # 'Satış' | 'Alış'
            "doc_no": self.in_docno.text().strip(),
            "date": self.in_date.date().toString("yyyy-MM-dd"),
            "notes": self.in_notes.text().strip(),
            "customer_text": self.cmb_customer.currentText().strip(),
            "pay_type": self.cmb_pay.currentText().strip() if hasattr(self, "cmb_pay") else "Nakit",
            "paid_amount": paid_eff,
            "discount": float(getattr(self, "_discount", 0.0))
        }

        try:
            payload = self.data.create_sale(header, items)
            self.transactionCommitted.emit(payload)
            QMessageBox.information(self, "Başarılı", "İşlem kaydedildi.")

            # Makbuz otomatik oluştur
            self._auto_generate_receipt_pdf()

            # Formu temizle
            self.clear_form_for_new_sale()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"İşlem kaydedilemedi:\n{e}")

    def clear_form_for_new_sale(self):
        """Yeni satış için formu temizle"""
        self.table.setRowCount(0)
        self.in_notes.clear()
        self.in_paid.setValue(0)
        self.lbl_sum_count.setText("0")
        self.lbl_sum_sub.setText(tl(0))
        self.lbl_sum_total.setText(tl(0))
        self.lbl_change.setText(f"Para Üstü: {tl(0)}")
        self.lbl_remaining.setText(f"Kalan (Veresiye): {tl(0)}")

        # Yeni belge numarası oluştur
        import random
        doc_no = f"SL{f'{random.randint(1, 9999):04d}'}"
        self.in_docno.setText(doc_no)

    def generate_receipt_pdf(self):
        """PDF makbuz oluştur"""
        if not PDF_AVAILABLE:
            QMessageBox.warning(self, "PDF Kütüphanesi Yok",
                "PDF oluşturmak için reportlab kütüphanesini yükleyin:\n\n"
                "pip install reportlab")
            return

        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Uyarı", "Makbuz oluşturulacak satır bulunamadı!")
            return

        # Font kontrolü - eğer fontlar mevcut değilse uyarı ver
        if not FONTS_AVAILABLE:
            reply = QMessageBox.question(self, "Unicode Font Uyarısı",
                "Türkçe karakterler (ç, ğ, ş, ö, ü) ve ₺ işareti için\n"
                "DejaVu fontları önerilir.\n\n"
                "Fontları indirmek için:\n"
                "https://dejavu-fonts.github.io/Download.html\n\n"
                "İndirdikten sonra:\n"
                "app/assets/fonts/ dizinine koyun:\n"
                "• DejaVuSans.ttf\n"
                "• DejaVuSans-Bold.ttf\n\n"
                "Devam etmek istiyor musunuz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes)
            if reply != QMessageBox.StandardButton.Yes:
                return

        # PDF dosya adı oluştur
        from PyQt6.QtWidgets import QFileDialog
        d = self.in_date.date().toString("yyyyMMdd")
        cust = self._safe_name(self.cmb_customer.currentText().split(" — ")[0])
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Makbuz Kaydet", f"makbuz_{d}_{cust}_{self.in_docno.text()}.pdf",
            "PDF Dosyaları (*.pdf)"
        )

        if not file_name:
            return

        try:
            # PDF oluştur
            doc = SimpleDocTemplate(file_name, pagesize=A5)
            styles = getSampleStyleSheet()

            # Font kullanılabilirliğini kontrol et
            use_unicode_font = FONTS_AVAILABLE if 'FONTS_AVAILABLE' in globals() else False
            if use_unicode_font:
                # Hangi font türü yüklendiyse onu kullan
                try:
                    pdfmetrics.getFont("DejaVu")
                    normal_font = "DejaVu"
                    bold_font = "DejaVu-Bold"
                except:
                    normal_font = "SystemFont"
                    bold_font = "SystemFont-Bold"
            else:
                normal_font = "Helvetica"
                bold_font = "Helvetica-Bold"

            # Özel stiller - Unicode fontlarla
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                fontName=bold_font,
                fontSize=16,
                spaceAfter=10,
                alignment=1,  # Center
                textColor=colors.darkblue
            )

            header_style = ParagraphStyle(
                'Header',
                parent=styles['Normal'],
                fontName=normal_font,
                fontSize=12,
                spaceAfter=5,
                alignment=0
            )

            table_style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), bold_font),    # başlık satırı
                ('FONTNAME', (0, 1), (-1, -1), normal_font), # gövde
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ])

            # PDF içeriği
            story = []

            # Başlık
            story.append(Paragraph("ORBİTX KUYUMCU", title_style))
            story.append(Paragraph("SATIŞ MAKBUZU", title_style))
            story.append(Spacer(1, 0.5*cm))

            # İşlem bilgileri
            customer_info = self.cmb_customer.currentText()
            doc_no = self.in_docno.text()
            date = self.in_date.text()
            transaction_type = self.cmb_type.currentText()

            story.append(Paragraph(f"<b>Belge No:</b> {doc_no}", header_style))
            story.append(Paragraph(f"<b>Tarih:</b> {date}", header_style))
            story.append(Paragraph(f"<b>İşlem Türü:</b> {transaction_type}", header_style))
            story.append(Paragraph(f"<b>Müşteri:</b> {customer_info}", header_style))
            story.append(Spacer(1, 0.3*cm))

            # Ürün tablosu
            table_data = [['Ürün Adı', 'Gram', 'Adet', 'Birim Fiyat', 'Toplam']]

            for row in range(self.table.rowCount()):
                product_name = self.table.item(row, 1).text()
                gram = self.table.item(row, 2).text()
                adet = self.table.item(row, 3).text()
                unit_price = self.table.item(row, 6).text()
                total = self.table.item(row, 7).text()

                table_data.append([product_name, gram, adet, unit_price, total])

            # Toplamlar için boş satır
            table_data.append(['', '', '', 'TOPLAM:', self.lbl_sum_total.text()])

            # Tabloyu oluştur
            col_widths = [4*cm, 2*cm, 1.5*cm, 2.5*cm, 2.5*cm]
            table = Table(table_data, colWidths=col_widths)
            table.setStyle(table_style)
            story.append(table)
            story.append(Spacer(1, 0.5*cm))

            # Ödeme bilgileri
            payment_type = self.cmb_pay.currentText()
            story.append(Paragraph(f"<b>Ödeme Türü:</b> {payment_type}", header_style))

            if payment_type != "Veresiye":
                paid_amount = tl(float(self.in_paid.value()))
                total_amount = self.lbl_sum_total.text()
                change = self.lbl_change.text()
                story.append(Paragraph(f"<b>Alınan Tutar:</b> {paid_amount}", header_style))
                story.append(Paragraph(f"<b>Toplam Tutar:</b> {total_amount}", header_style))
                story.append(Paragraph(f"<b>{change}</b>", header_style))
            else:
                remaining = self.lbl_remaining.text()
                story.append(Paragraph(f"<b>{remaining}</b>", header_style))

            story.append(Spacer(1, 0.5*cm))

            # Alt bilgi - Unicode font ile
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontName=normal_font,
                fontSize=10,
                alignment=1,  # Center
                spaceBefore=20
            )
            story.append(Paragraph("Teşekkür ederiz!", footer_style))

            # PDF'i oluştur
            doc.build(story)

            # Font durumu hakkında bilgi ver
            font_info = ""
            if use_unicode_font:
                font_info = "\n\n✓ Unicode fontlar kullanıldı (Türkçe karakterler ve ₺ işareti destekleniyor)"
            else:
                font_info = "\n\n⚠️ Varsayılan font kullanıldı (bazı karakterler doğru görünmeyebilir)"

            QMessageBox.information(self, "Makbuz Oluşturuldu",
                f"Makbuz başarıyla kaydedildi:\n\n{file_name}{font_info}")

        except Exception as e:
            QMessageBox.critical(self, "Hata",
                f"Makbuz oluşturulurken hata oluştu:\n\n{str(e)}")

    def _clear_form(self):
        """Formu temizle"""
        self.table.setRowCount(0)
        self.in_notes.clear()
        self.in_paid.setValue(0)
        self.lbl_sum_count.setText("0")
        self.lbl_sum_sub.setText(tl(0))
        self.lbl_sum_total.setText(tl(0))
        self.lbl_change.setText(f"Para Üstü: {tl(0)}")
        self.lbl_remaining.setText(f"Kalan (Veresiye): {tl(0)}")

        # Yeni belge numarası oluştur
        import random
        doc_no = f"SL{f'{random.randint(1, 9999):04d}'}"
        self.in_docno.setText(doc_no)

    # === MAKBUZ OTO KAYIT ===
    def _safe_name(self, s: str) -> str:
        """Dosya adı için güvenli isim oluştur"""
        import re
        s = re.sub(r"[^0-9A-Za-zÇĞİÖŞÜçğıöşü\s\-]+", "", s).strip()
        return re.sub(r"\s+", "_", s)

    def _auto_generate_receipt_pdf(self, file_path: str|None=None):
        """Kullanıcıya sormadan PDF makbuz üretir. Yol verilmezse ./receipts/SLxxxx.pdf'e kaydeder."""
        if not PDF_AVAILABLE:
            # sessiz çık: kitaplık yoksa zorlamayalım
            return

        # hedef yol
        if not file_path:
            # ./receipts klasörü
            base_dir = os.path.join(os.getcwd(), "receipts")
            os.makedirs(base_dir, exist_ok=True)
            d = self.in_date.date().toString("yyyyMMdd")
            cust = self._safe_name(self.cmb_customer.currentText().split(" — ")[0])
            file_path = os.path.join(base_dir, f"makbuz_{d}_{cust}_{self.in_docno.text()}.pdf")

        # Aşağıda, mevcut generate_receipt_pdf ile aynı içerik üretimini KISACA kullanıyoruz.
        # En güvenlisi: generate_receipt_pdf'i parametreli hale getirip tekrar kullanmak.
        try:
            self._generate_receipt_core(file_path)
        except Exception as e:
            # hata olduğunda kullanıcıyı boğma
            print("Makbuz oluşturulamadı:", e)

    def _generate_receipt_core(self, file_path: str):
        """Var olan generate_receipt_pdf'in gövdesinden türetilmiş çekirdek. Diyalog yok."""
        from reportlab.lib.pagesizes import A5
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.pdfbase import pdfmetrics

        doc = SimpleDocTemplate(file_path, pagesize=A5)
        styles = getSampleStyleSheet()

        # font seçimi
        use_unicode_font = FONTS_AVAILABLE if 'FONTS_AVAILABLE' in globals() else False
        if use_unicode_font:
            try:
                pdfmetrics.getFont("DejaVu")
                normal_font = "DejaVu"; bold_font = "DejaVu-Bold"
            except:
                normal_font = "SystemFont"; bold_font = "SystemFont-Bold"
        else:
            normal_font = "Helvetica"; bold_font = "Helvetica-Bold"

        title_style = ParagraphStyle('Title', parent=styles['Heading1'],
                                     fontName=bold_font, fontSize=16,
                                     spaceAfter=10, alignment=1, textColor=colors.darkblue)
        header_style = ParagraphStyle('Header', parent=styles['Normal'],
                                      fontName=normal_font, fontSize=12, spaceAfter=5, alignment=0)

        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), bold_font),
            ('FONTNAME', (0, 1), (-1, -1), normal_font),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ])

        story = []
        story.append(Paragraph("ORBİTX KUYUMCU", title_style))
        story.append(Paragraph("SATIŞ MAKBUZU" if self.cmb_type.currentText()=="Satış" else "ALIŞ MAKBUZU", title_style))
        story.append(Spacer(1, 0.5*cm))

        customer_info = self.cmb_customer.currentText()
        doc_no = self.in_docno.text()
        date = self.in_date.text()
        transaction_type = self.cmb_type.currentText()

        story.append(Paragraph(f"<b>Belge No:</b> {doc_no}", header_style))
        story.append(Paragraph(f"<b>Tarih:</b> {date}", header_style))
        story.append(Paragraph(f"<b>İşlem Türü:</b> {transaction_type}", header_style))
        story.append(Paragraph(f"<b>{'Müşteri' if transaction_type=='Satış' else 'Tedarikçi'}:</b> {customer_info}", header_style))
        story.append(Spacer(1, 0.3*cm))

        # satırlar
        table_data = [['Ürün Adı', 'Gram', 'Adet', 'Birim Fiyat', 'Toplam']]
        for row in range(self.table.rowCount()):
            product_name = self.table.item(row, 1).text()
            gram = self.table.item(row, 2).text()
            adet = self.table.item(row, 3).text()
            unit_price = self.table.item(row, 6).text()
            total = self.table.item(row, 7).text()
            table_data.append([product_name, gram, adet, unit_price, total])

        table_data.append(['', '', '', 'TOPLAM:', self.lbl_sum_total.text()])
        table = Table(table_data, colWidths=[4*cm, 2*cm, 1.5*cm, 2.5*cm, 2.5*cm])
        table.setStyle(table_style)
        story.append(table)
        story.append(Spacer(1, 0.5*cm))

        payment_type = self.cmb_pay.currentText()
        story.append(Paragraph(f"<b>Ödeme Türü:</b> {payment_type}", header_style))
        if payment_type != "Veresiye":
            paid_amount = tl(float(self.in_paid.value()))
            total_amount = self.lbl_sum_total.text()
            change = self.lbl_change.text()
            story.append(Paragraph(f"<b>Alınan Tutar:</b> {paid_amount}", header_style))
            story.append(Paragraph(f"<b>Toplam Tutar:</b> {total_amount}", header_style))
            story.append(Paragraph(f"<b>{change}</b>", header_style))
        else:
            remaining = self.lbl_remaining.text()
            story.append(Paragraph(f"<b>{remaining}</b>", header_style))

        doc.build(story)

    def _build_finance_payload(self) -> dict:
        """Finans sayfasına gönderilecek ham veri."""
        kind = "Gelir" if self.cmb_type.currentText() == "Satış" else "Gider"
        total_float = self._calc_total()
        items = []
        for r in range(self.table.rowCount()):
            items.append({
                "kod":   self.table.item(r, 0).text(),
                "ad":    self.table.item(r, 1).text(),
                "gram":  float(self.table.item(r, 2).text().replace(",", ".")),
                "adet":  int(self.table.item(r, 3).text()),
                "milyem": self.table.item(r, 4).text(),
                "iscilik": float(self.table.item(r, 5).data(Qt.ItemDataRole.UserRole) or 0.0),
                "birim": float(self.table.item(r, 6).data(Qt.ItemDataRole.UserRole) or 0.0),
                "tutar": float(self.table.item(r, 7).data(Qt.ItemDataRole.UserRole) or 0.0),
            })

        payload = {
            "tip": kind,                                 # "Gelir" / "Gider"
            "kategori": self.cmb_type.currentText(),     # "Satış" / "Alış"
            "tarih": self.in_date.date().toString("dd.MM.yyyy"),
            "belge_no": self.in_docno.text(),
            "cari": self.cmb_customer.currentText(),
            "odeme_turu": self.cmb_pay.currentText(),
            "tutar": total_float,
            "aciklama": self.in_notes.text().strip(),
            "kalemler": items,
        }
        return payload

    def _post_to_finance(self, payload: dict):
        """Finans ekranına veri ilet. Hem sinyal, hem de opsiyonel API."""
        # 1) Sinyal
        try:
            self.transactionCommitted.emit(payload)
        except Exception as e:
            print("transactionCommitted emit hata:", e)

        # 2) Opsiyonel doğrudan API
        try:
            from finance import FinanceAPI  # sana verdiğin dosyada böyle bir sınıf varsa
            if hasattr(FinanceAPI, "add_entry"):
                FinanceAPI.add_entry(payload)
        except Exception as e:
            # API yoksa sessizce geç
            print("FinanceAPI.add_entry bulunamadı/çalışmadı:", e)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Delete:
            self.remove_item()
        else:
            super().keyPressEvent(e)
