# app/main.py
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QStackedWidget
from theme import apply_theme
from sidebar import Sidebar
from pages.login import LoginPage
from pages.dashboard import DashboardPage
from pages.stock import StockPage


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kuyumcu ERP — Zarif")
        self.resize(1220, 740)

        # Kök layout
        root = QWidget()
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        layout.addWidget(self.sidebar)

        # Sayfa yığını
        self.stack = QStackedWidget()

        # Sıra: login(0) → dashboard(1) → stock(2)
        self.page_index = {
            "login": 0,
            "dashboard": 1,
            "stock": 2,
        }

        self.stack.addWidget(LoginPage())     # 0
        self.stack.addWidget(DashboardPage()) # 1
        self.stack.addWidget(StockPage())     # 2

        layout.addWidget(self.stack, 1)  # sağ taraf büyüsün
        self.setCentralWidget(root)

        # İlk açılışta login göster
        self.stack.setCurrentIndex(self.page_index["login"])

        # Sidebar rotası (şimdilik login'i atlamaz; istersen gizleyebiliriz)
        self.sidebar.routeChanged.connect(self.switch_route)

    def switch_route(self, route: str):
        idx = self.page_index.get(route, 0)
        self.stack.setCurrentIndex(idx)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_theme(app, scheme="dim")  # "light" istersen burayı değiştir
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
