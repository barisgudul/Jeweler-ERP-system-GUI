# OrbitX Jewelry ERP

<div align="center">

![OrbitX Logo](assets/logo.png)

**Comprehensive ERP System for Modern Jewelry Businesses**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.0+-green.svg)](https://pypi.org/project/PyQt6/)
[![ReportLab](https://img.shields.io/badge/ReportLab-4.0+-orange.svg)](https://www.reportlab.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Elegant Design, Powerful Functionality, Cosmic Theme*

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Architecture](#architecture-and-technology) • [Contributing](#contributing)

</div>

---

## 📋 Table of Contents

- [OrbitX Jewelry ERP](#orbitx-jewelry-erp)
  - [📋 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [🏗️ Architecture and Technology](#️-architecture-and-technology)
  - [📦 Installation](#-installation)
  - [🚀 Usage](#-usage)
  - [📖 Detailed Module Descriptions](#-detailed-module-descriptions)
  - [🎨 Theme System](#-theme-system)
  - [📊 Data Management](#-data-management)
  - [🔧 Developer Guide](#-developer-guide)
  - [📈 Performance and Scalability](#-performance-and-scalability)
  - [🔒 Security](#-security)
  - [📋 Requirements](#-requirements)
  - [🤝 Contributing](#-contributing)
  - [📄 License](#-license)
  - [🙏 Acknowledgments](#-acknowledgments)
  - [📞 Contact](#-contact)

---

## ✨ Features

### 🎯 Core Functionality
- **🔐 User Management**: Multi-user profiles, photo support, secure login
- **📊 Dashboard**: KPI cards, live metrics, quick action buttons
- **📦 Stock Management**: Category-based inventory, critical stock alerts, labor tracking
- **👥 Customer Accounts**: Customer management, debt/credit tracking, transaction history
- **💰 Sales Transactions**: Purchase/sales operations, receipt generation, multi-product selection
- **💼 Finance Management**: Cash/bank operations, income/expense tracking, voucher creation
- **📋 Reporting**: Date/category/customer filtering, CSV/PDF export
- **⚙️ System Parameters**: Company information, prefix settings, theme selection

### 🎨 User Experience
- **🌌 Cosmic Theme**: Starry sky background, modern glass effects
- **🌙 Multiple Themes**: Dark, dim, light theme options
- **🇹🇷 Turkish Localization**: Full Turkish support, local date/time format
- **📱 Responsive Design**: Screen-size adaptive, intuitive interface
- **⌨️ Keyboard Shortcuts**: Common shortcuts are supported by dialogs (Enter/ESC)

### 📄 Document Management
- **🧾 PDF Receipts**: Professional sales receipts, Unicode font support
- **📊 CSV Export**: Stock, customer, finance reports (Excel-compatible)
- **🖨️ Print Support**: Direct printer integration

---

## 🏗️ Architecture and Technology

### 🛠️ Technology Stack

```mermaid
graph TB
    A[PyQt6 GUI Framework] --> B[OrbitX Jewelry ERP]
    C[ReportLab PDF Engine] --> B
    D[QSS Theme System] --> B
    E[Future DB Layer (SQLite planned)] --> B
    F[DejaVu Fonts] --> B

    B --> G[Login System]
    B --> H[Dashboard]
    B --> I[Stock Management]
    B --> J[Customer Accounts]
    B --> K[Sales Transactions]
    B --> L[Finance]
    B --> M[Reports]
    B --> N[Parameters]
```

### 📁 Project Structure

```
OrbitX_Jewelry_ERP/
├── app/
│   ├── __init__.py            # Package initialization
│   ├── main.py                # Main application entry point
│   ├── theme.py               # QSS-based theme engine
│   ├── sidebar.py             # Navigation sidebar
│   ├── dialogs.py             # Modal dialog windows
│   ├── pages/
│   │   ├── __init__.py        # Package initialization
│   │   ├── login.py           # User login page
│   │   ├── dashboard.py       # Main dashboard panel
│   │   ├── stock.py           # Stock management module
│   │   ├── customers.py       # Customer account management
│   │   ├── sales.py           # Sales transactions
│   │   ├── finance.py         # Finance and cash register
│   │   ├── reports.py         # Reporting system
│   │   └── parameters.py      # System parameters
│   └── assets/
│       ├── fonts/             # Unicode fonts (DejaVu)
│       ├── logo.png           # OrbitX logo
│       └── users/             # User avatars
├── receipts/                  # Generated PDF receipts
├── environment.yml            # Conda environment
└── README.md
```

### 🔧 Core Components

#### **main.py** - Main Application Controller
```python
class MainWindow(QMainWindow):
    """Main window class - Page routing and layout"""
    - Responsive window sizing
    - Sidebar navigation integration
    - Theme application system
    - Inter-page signal connections
```

#### **theme.py** - Theme Management System
```python
SCHEMES = {
    "dark": {...},   # Dark theme
    "dim": {...},    # Medium dark (default)
    "light": {...}   # Light theme
}
```
- **QSS-based dynamic theming**
- **Glass effects** and shadow support
- **Responsive color palette**
- **Dialog theme integration**

#### **sidebar.py** - Navigation System
- **OrbitX logo** integration
- **Active page** indicator
- **Cosmic background** animation
- **Responsive button layout**

---

## 📦 Installation

### 🔧 System Requirements

- **Python**: 3.10 or higher
- **RAM**: Minimum 4GB
- **Disk**: 500MB free space
- **OS**: Windows 10/11, macOS 10.15+, Linux

### 📥 Step-by-Step Installation

#### 1. Python Installation
```bash
# Check Python version
python --version
# Python 3.10+ required
```

#### 2. Clone the Repository
```bash
git clone https://github.com/your-username/OrbitX_Jewelry_ERP.git
cd OrbitX_Jewelry_ERP
```

#### 3. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

#### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 5. Start the Application
```bash
python app/main.py
```

### 🐳 Docker Installation (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "app/main.py"]
```

```bash
docker build -t orbitx-erp .
docker run -it --rm orbitx-erp
```

---

## 🚀 Usage

### 🔑 First Login

1. **Start the application**: `python app/main.py`
2. **Select user**: Choose a profile from the left panel
3. **Enter password**: Use your configured credentials (demo uses mock auth UI)
4. **Access dashboard**: After successful login

### 📊 Basic Workflows

#### New Sales Transaction
1. **Sidebar** → **Sales** page
2. **Click "New Sale"** button
3. **Select products**: Multi-product selector dialog
4. **Set quantities**: Amount/weight for each product
5. **Select customer**: From customer account list
6. **Save**: PDF receipt automatically generated

#### Stock Entry
1. **Sidebar** → **Stock Management**
2. **Click "New Stock"** button
3. **Product details**: Code, category, gram, carat
4. **Price information**: Purchase/sale price, labor costs
5. **Critical level**: Set alert threshold

#### Finance Transaction
1. **Sidebar** → **Cash & Finance**
2. **Click "New Record"** button
3. **Transaction type**: Income/Expense selection
4. **Account**: Cash/Bank selection
5. **Category**: Income/Expense type
6. **Related account**: Link customer/supplier

### ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `ESC` | Close dialog/Cancel window |
| `Enter` | Submit form/Confirm save |
| `Ctrl+S` | Save (where implemented) |
| `Ctrl+N` | New record (where implemented) |

---

## 📖 Detailed Module Descriptions

### 🔐 Login System (`login.py`)

**Features:**
- **Multi-user profiles** with photo support
- **Rotating banner** system (product images)
- **Password visibility** toggle
- **Responsive grid** layout
- **Turkish date/time** display

**Security:**
- **Mock authentication** (should be replaced with real auth in production)
- **Profile management** (add/edit/delete)
- **Avatar system** (circular cropping)

### 📊 Dashboard (`dashboard.py`)

**KPI Indicators:**
- **Gold per Gram**: Live price information
- **Daily Sales**: Today's total transactions
- **Total Stock Value**: Inventory value
- **Monthly Turnover**: Monthly total sales
- **Pending Payment**: Supplier debts
- **Critical Stock**: Low-level products

**Quick Access:**
- **New Sales Transaction**
- **Add New Customer**
- **New Stock Entry**
- **Reports**

### 📦 Stock Management (`stock.py`)

**Product Categories:**
- **Bracelet**, **Ring**, **Necklace**
- **Ingot**, **Gram** (gold types)

**Detailed Tracking:**
- **Millesimal**: Purity degree (22K = 916.00)
- **Carat**: Carat information (22, 24)
- **Gram**: Weight
- **Quantity**: Stock amount
- **Labor**: Received/given labor costs
- **VAT**: Tax rate

**Features:**
- **Critical stock alerts** (color coding)
- **Search and filtering**
- **Bulk editing**
- **Excel export**

### 👥 Customer Accounts (`customers.py`)

**Customer Information:**
- **Code**: Unique customer code (CAR0001 format)
- **Name Surname**: Customer name
- **Phone**: Contact number
- **Balance**: Debt/credit status
- **Last Transaction**: Last transaction date
- **Status**: Active/Passive

**Functions:**
- **Search and filtering**
- **Debt/credit tracking**
- **Transaction history**
- **PDF/Excel export**

### 💰 Sales Transactions (`sales.py`)

**Transaction Types:**
- **Purchase**: Product entry from supplier
- **Sale**: Product exit to customer

**PDF Receipt System:**
- **ReportLab** integration
- **Unicode font** support (Turkish characters)
- **Professional layout**
- **Automatic numbering**

**Multi-Product Selection:**
- **Batch selection** dialog
- **Dynamic quantity** adjustment
- **Total calculation**

### 💼 Finance Management (`finance.py`)

**Account Types:**
- **Cash**: Cash operations
- **Bank**: VakıfBank, Ziraat accounts

**Transaction Categories:**
- **Income**: Sales collection, customer payment
- **Expense**: Expense, supplier payment, rent

**Voucher System:**
- **Expense voucher** creation
- **Date/time** stamp
- **Related account** linking

### 📋 Reporting (`reports.py`)

**Filter Options:**
- **Date range**: Start/end dates
- **Transaction type**: Purchase/Sale/All
- **Account**: Customer-based filter
- **Category**: Product category

**Export:**
- **CSV format**: Excel compatible
- **PDF reports**: Professional layout
- **Print support**: Direct printer

### ⚙️ Parameters (`parameters.py`)

**System Settings:**
- **Company information**: Name, tax no, address
- **Code prefixes**: SAT-, CAR- formats
- **Number digits**: 6-digit numbering
- **Currency**: TRY, USD, EUR
- **Reset period**: Annual/Monthly
- **Theme selection**: Dark/Dim/Light

---

## 🎨 Theme System

### 🌙 Available Themes

#### Dark Theme
```css
PRIMARY: #5B8CFF    /* Primary blue */
BG: #0C1016        /* Dark background */
TEXT: #E9EDF2      /* Light text */
SURFACE: rgba(22,28,38,0.92)  /* Glass effect */
```

#### Dim Theme (Default)
```css
PRIMARY: #4C7DFF    /* Medium blue */
BG: #171C23        /* Medium dark */
TEXT: #F1F4F8      /* Very light text */
SURFACE: rgba(28,34,44,0.96)  /* Transparent surface */
```

#### Light Theme
```css
PRIMARY: #3C6DFF    /* Dark blue */
BG: #F5F7FA        /* Light background */
TEXT: #1B2430      /* Dark text */
SURFACE: #FFFFFF   /* White surface */
```

### 🎭 Special Effects

- **Glass Effect**: Transparent glass-like surfaces
- **Elevation**: Shadow effects for depth
- **Cosmic Background**: Animated starry sky
- **Smooth Transitions**: Smooth transition animations

---

## 📊 Data Management

### 🗄️ Data Structure

```python
# Stock record example
stock_record = {
    "Code": "STK0123",
    "Category": "Ring",
    "Name": "22K Ring",
    "Millesimal": 916.00,
    "Carat": 22,
    "Gram": 5.20,
    "Quantity": 3,
    "PurchasePrice": 1250.00,
    "SalePrice": 1450.00,
    "LaborType": "Millesimal",
    "LaborReceived": 15.50,
    "LaborGiven": 18.75,
    "VAT": 20.00,
    "CriticalStock": 5
}
```

### 💾 Persistence

- **Parameters via QSettings**; business data currently seeded in-memory.
A SQLite persistence layer is planned.
- **JSON** configuration files
- **PDF** receipt archive
- **CSV** export (Excel-compatible)

### 🔄 Data Flow

```
User Login → Dashboard KPIs → Transaction Modules → Data Saving → Reporting
```

---

## 🔧 Developer Guide

### 🏃‍♂️ Quick Start

```python
from PyQt6.QtWidgets import QApplication
from app.main import MainWindow
from app.theme import apply_theme

app = QApplication([])
apply_theme(app, scheme="dim")
window = MainWindow()
window.show()
app.exec()
```

### 🧪 Creating Test Data

```python
# Mock data generator
from app.pages.stock import generate_rows
test_stock = generate_rows(50)  # 50 test products
```

### 🔌 Adding New Module

1. **Create page class** (`pages/new_module.py`)
2. **Import in** `main.py`
3. **Add button to sidebar**
4. **Set up route mapping**

### 🎨 Theme Extension

```python
# Add new theme
SCHEMES["custom"] = {
    "PRIMARY": "#FF6B6B",
    "BG": "#2D1B69",
    "TEXT": "#FFFFFF",
    # ... other colors
}
```

### 📋 Code Standards

- **PEP 8** compliance
- **Type hints** usage
- **English docstrings**
- **Modular structure**

---

## 📈 Performance and Scalability

### ⚡ Optimization Features

- **Lazy loading** table data
- **Pagination** for large lists
- **Background processing** report generation
- **Memory efficient** image processing

### 📊 Scalability

- **Modular architecture** for new features
- **Database abstraction** for different DB support
- **API-ready** structure (for future web version)
- **Plugin system** potential

### 🔍 Monitoring

- **Memory usage** tracking
- **Query performance** logging
- **Error handling** centralized system
- **User action** logging

---

## 🔒 Security

### 🛡️ Current Security

- **Input validation** across dialogs and fields
- **PDF generation** with embedded fonts (Unicode/Turkish support)
- **Dialog-based access** (no web surface)
- **In-memory data** isolation

### 🔐 Security Improvements

```python
# Example: Password hashing
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

### 📋 Future Security Enhancements

- [ ] **Real authentication** system (replace mock UI)
- [ ] **Database encryption** for data persistence
- [ ] **Audit logging** for transaction tracking
- [ ] **Role-based access** control
- [ ] **Automatic backups** and data recovery

---

## 📖 Documentation

For now, this README serves as the main guide. Additional documentation can be found in:

- **Inline docstrings** in `pages/*.py` and `dialogs.py`
- **Code comments** throughout the application
- **GitHub Issues** for bug reports and feature requests
- **GitHub Discussions** for community questions

A comprehensive developer wiki and user manual are planned for future releases.

## 📋 Requirements

### Python Packages

```
PyQt6>=6.6            # Modern GUI framework (actively maintained)
reportlab>=4.0        # PDF generation and receipts
```

### Optional Dependencies

```
pillow>=9.0           # Only if you need additional image processing
bcrypt>=4.0           # For future authentication system
pandas>=1.5.0         # For advanced data analysis (planned)
openpyxl>=3.0.0       # For direct Excel file support (planned)
```

### System Requirements

- **OS**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.10 - 3.12
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 500MB application + data space

### 🔧 Development Environment

```bash
# Development dependencies
pip install black flake8 mypy pytest

# Code quality control
black .                    # Code formatting
flake8 .                   # Lint checking
mypy .                     # Type checking
pytest                     # Test running
```

---

## 🤝 Contributing

### 🚀 How to Contribute

1. **Fork** the repo: `https://github.com/your-username/OrbitX_Jewelry_ERP/fork`
2. **Create branch**: `git checkout -b feature/new-feature`
3. **Make changes** and **commit**
4. **Push**: `git push origin feature/new-feature`
5. **Create Pull Request**

### 📝 Coding Standards

```python
# ✅ Correct: With type hints
def calculate_total(price: float, quantity: int) -> float:
    """Calculate total amount."""
    return price * quantity

# ❌ Wrong: Without type hints
def calculate_total(price, quantity):
    return price * quantity
```

### 🧪 Writing Tests

```python
def test_sales_calculation():
    """Test sales total calculation."""
    price = 100.0
    quantity = 5
    vat = 20.0

    total = calculate_sales_total(price, quantity, vat)
    assert total == 600.0  # 500 + 100 VAT
```

### 📚 Documentation

- **README** updates
- **English docstrings**
- **Explanatory code comments**
- **API documentation**

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 OrbitX Jewelry ERP

This software and associated documentation files ("Software") are freely
available to any person for any purpose, and may be copied, modified, and distributed.
```

See [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

### 🤝 Contributors

- **Project Developer**: [Name Surname]
- **UI/UX Design**: OrbitX Design Team
- **Testing and QA**: Beta users

### 📚 Technologies Used

- **[PyQt6](https://pypi.org/project/PyQt6/)**: Modern GUI framework
- **[ReportLab](https://www.reportlab.com/)**: PDF generation engine
- **[DejaVu Fonts](https://dejavu-fonts.github.io/)**: Unicode font support
- **[Qt6](https://www.qt.io/)**: Cross-platform application framework

### 🌟 Inspiration Sources

- **Material Design**: Modern UI principles
- **Cosmic Theme**: Science fiction aesthetics
- **Turkish UX**: Local user experience

---

## 📞 Contact

Have questions about the **OrbitX Jewelry ERP** project?

- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/OrbitX_Jewelry_ERP/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-username/OrbitX_Jewelry_ERP/discussions)

---

<div align="center">

**OrbitX Jewelry ERP** - Modern, reliable solution for jewelry businesses

⭐ If this project is helpful, don't forget to star it!

</div>
