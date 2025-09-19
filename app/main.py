# app/main.py
import sys
import os

# Python path'ine mevcut klasörü ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from PyQt6.QtCore import QTimer
from theme import apply_theme
from data.service import DataService

# Import other modules after QApplication is created in main
def create_main_window():
    from sidebar import Sidebar
    from pages.login import LoginPage
    from pages.dashboard import DashboardPage
    from pages.stock import StockPage
    from pages.customers import CustomersPage
    from pages.sales import SalesPage
    from pages.finance import FinancePage
    from pages.reports import ReportsPage
    from pages.parameters import ParametersPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kuyumcu ERP — Zarif")

        # Ekran boyutuna göre responsive pencere (şimdilik varsayılan boyutlar)
        window_width = 1400
        window_height = 800

        # Minimum boyutları koru
        min_width = 1200
        min_height = 700
        window_width = max(window_width, min_width)
        window_height = max(window_height, min_height)

        self.resize(window_width, window_height)
        self.setMinimumSize(min_width, min_height)

        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Import sidebar first
        from sidebar import Sidebar

        # Sidebar (girişte gizli)
        self.sidebar = Sidebar()
        self.sidebar.setVisible(False)  # <— önemli
        layout.addWidget(self.sidebar)

        # DataService oluştur
        self.data = DataService("orbitx.db")
        # İlk kez açılışta boşsa demo verisi yükle
        self.data.seed_demo_if_empty()

        # Periodically fetch external market prices and notify UI
        self._market_timer = QTimer(self)
        self._market_timer.setInterval(30 * 1000)  # 30s (can be tuned)
        self._market_timer.timeout.connect(lambda: self.data.fetch_market_prices())
        self._market_timer.start()

        # Sayfa yığını
        self.stack = QStackedWidget()
        self.page_index = {"login": 0, "dashboard": 1, "stock": 2, "customers": 3, "sales": 4, "finance": 5, "reports": 6, "parameters": 7}

        # Import modules and create pages
        from sidebar import Sidebar
        from pages.login import LoginPage
        from pages.dashboard import DashboardPage
        from pages.stock import StockPage
        from pages.customers import CustomersPage
        from pages.sales import SalesPage
        from pages.finance import FinancePage
        from pages.reports import ReportsPage
        from pages.parameters import ParametersPage

        # Sayfalar
        self.login = LoginPage()
        self.dashboard = DashboardPage(self.data)
        self.stock = StockPage(self.data)
        self.customers = CustomersPage(self.data)
        self.sales = SalesPage(self.data)
        self.finance = FinancePage(self.data)
        self.reports = ReportsPage()
        self.parameters = ParametersPage()

        # Sinyal bağlantıları
        self.sales.transactionCommitted.connect(self.finance.add_row_from_sales)
        self.sales.transactionCommitted.connect(self.customers.on_transaction_from_sales)
        self.sales.transactionCommitted.connect(self.stock.on_transaction_from_sales)

        self.data.stockChanged.connect(self.stock.reload_from_db)
        self.data.customersChanged.connect(self.customers.reload_from_db)
        self.data.cashChanged.connect(self.finance.reload_from_db)

        # Satış/Alış sonrası Dashboard "Son İşlemler"i canlı güncelle
        self.data.saleCommitted.connect(self.dashboard.on_sale_committed)

        self.stack.addWidget(self.login)      # 0
        self.stack.addWidget(self.dashboard)  # 1
        self.stack.addWidget(self.stock)      # 2
        self.stack.addWidget(self.customers)  # 3
        self.stack.addWidget(self.sales)      # 4
        self.stack.addWidget(self.finance)    # 5
        self.stack.addWidget(self.reports)    # 6
        self.stack.addWidget(self.parameters) # 7

        layout.addWidget(self.stack, 1)
        self.setCentralWidget(root)

        # İlk sayfa: login
        self.stack.setCurrentIndex(self.page_index["login"])

        # Bağlantılar
        self.sidebar.routeChanged.connect(self.switch_route)
        self.login.loggedIn.connect(self.on_logged_in)
        self.dashboard.quick_action_triggered.connect(self.handle_quick_action)

    def handle_quick_action(self, payload: dict):
        """Dashboard'dan gelen hızlı eylem sinyalini işle"""
        route = payload.get('route')
        action = payload.get('action')

        if not route:
            return

        # 1. Sidebar'ı güncelle
        self.sidebar.set_active(route)

        # 2. Sayfayı değiştir
        self.switch_route(route)

        # 3. İlgili eylemi tetikle
        if action == 'new':
            if route == 'customers':
                # Kısa bir gecikme ile diyalogu aç, sayfa geçişinin bitmesini bekle
                QTimer.singleShot(100, self.customers.on_new)
            elif route == 'sales':
                # Satış sayfasında yeni satış formu için gerekli hazırlıklar
                QTimer.singleShot(100, lambda: self.sales.clear_form_for_new_sale() if hasattr(self.sales, 'clear_form_for_new_sale') else None)
            elif route == 'stock':
                # Stok sayfasında yeni stok ekleme
                QTimer.singleShot(100, self.stock.on_new if hasattr(self.stock, 'on_new') else None)
            elif route == 'finance':
                # Finans sayfasında yeni kayıt
                QTimer.singleShot(100, lambda: self.finance.open_new_record_dialog("Giriş"))

    def on_logged_in(self, payload: dict):
        # Login başarılı → sidebar görünür, dashboard'a geç
        self.sidebar.setVisible(True)
        self.switch_route("dashboard")

    def switch_route(self, route: str):
        idx = self.page_index.get(route, 1)
        self.stack.setCurrentIndex(idx)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_theme(app, scheme="dim")
    w = MainWindow()
    w.showMaximized()  # Tam ekranda aç
    sys.exit(app.exec())
