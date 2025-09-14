# app/data/db.py
import os, sqlite3, threading
from contextlib import contextmanager

_LOCK = threading.RLock()

def _connect(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True) if os.path.dirname(path) else None
    cx = sqlite3.connect(path, check_same_thread=False)
    cx.row_factory = sqlite3.Row
    cx.execute("PRAGMA foreign_keys = ON;")
    cx.execute("PRAGMA journal_mode = WAL;")
    cx.execute("PRAGMA synchronous = NORMAL;")
    return cx

class DB:
    def __init__(self, path="orbitx.db"):
        self.path = path
        self.cx = _connect(path)
        self._init_schema()

    @contextmanager
    def tx(self):
        with _LOCK:
            try:
                self.cx.execute("BEGIN;")
                yield self.cx
                self.cx.commit()
            except Exception:
                self.cx.rollback()
                raise

    def _init_schema(self):
        self.cx.executescript("""
        CREATE TABLE IF NOT EXISTS customers(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          code TEXT UNIQUE, name TEXT NOT NULL, phone TEXT,
          status TEXT DEFAULT 'Aktif',
          balance REAL NOT NULL DEFAULT 0.0,
          last_txn_at TEXT,
          created_at TEXT DEFAULT (datetime('now')),
          updated_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS stock_items(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          code TEXT UNIQUE NOT NULL, name TEXT NOT NULL,
          category TEXT, milyem INTEGER, ayar INTEGER,
          gram REAL DEFAULT 0.0, qty INTEGER DEFAULT 0,
          buy_price REAL DEFAULT 0.0, sell_price REAL DEFAULT 0.0,
          isc_tip TEXT, isc_alinan REAL DEFAULT 0.0, isc_verilen REAL DEFAULT 0.0,
          vat REAL DEFAULT 0.0, critical_qty INTEGER DEFAULT 5, photo TEXT
        );

        CREATE TABLE IF NOT EXISTS sales(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          type TEXT NOT NULL,             -- 'Satış' | 'Alış'
          doc_no TEXT, date TEXT NOT NULL, notes TEXT,
          customer_id INTEGER, pay_type TEXT,
          paid_amount REAL DEFAULT 0.0, discount REAL DEFAULT 0.0,
          total REAL NOT NULL, due REAL NOT NULL,
          created_at TEXT DEFAULT (datetime('now')),
          FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS sale_items(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          sale_id INTEGER NOT NULL, stock_id INTEGER,
          code TEXT NOT NULL, name TEXT NOT NULL,
          gram REAL DEFAULT 0.0, qty INTEGER NOT NULL,
          unit_price REAL NOT NULL, milyem TEXT, iscilik REAL DEFAULT 0.0,
          line_total REAL NOT NULL,
          FOREIGN KEY(sale_id) REFERENCES sales(id) ON DELETE CASCADE,
          FOREIGN KEY(stock_id) REFERENCES stock_items(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS customer_ledger(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          customer_id INTEGER NOT NULL, sale_id INTEGER,
          direction TEXT NOT NULL,     -- 'Borç' | 'Alacak'
          amount REAL NOT NULL, desc TEXT, date TEXT NOT NULL,
          FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE CASCADE,
          FOREIGN KEY(sale_id) REFERENCES sales(id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS stock_moves(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          stock_id INTEGER NOT NULL, sale_id INTEGER,
          move_type TEXT NOT NULL,     -- 'OUT' | 'IN' | 'ADJ'
          qty INTEGER NOT NULL, note TEXT, date TEXT NOT NULL,
          FOREIGN KEY(stock_id) REFERENCES stock_items(id) ON DELETE CASCADE,
          FOREIGN KEY(sale_id) REFERENCES sales(id) ON DELETE SET NULL
        );

        -- Kasa & Banka (Finance)
        CREATE TABLE IF NOT EXISTS cash_ledger(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          date TEXT NOT NULL, time TEXT,
          account TEXT NOT NULL,       -- 'Kasa' | 'Banka — …'
          type TEXT NOT NULL,          -- 'Giriş' | 'Çıkış'
          category TEXT, description TEXT,
          amount REAL NOT NULL,
          customer_id INTEGER, sale_id INTEGER,
          FOREIGN KEY(customer_id) REFERENCES customers(id) ON DELETE SET NULL,
          FOREIGN KEY(sale_id) REFERENCES sales(id) ON DELETE SET NULL
        );

        CREATE INDEX IF NOT EXISTS idx_cust_code ON customers(code);
        CREATE INDEX IF NOT EXISTS idx_stock_code ON stock_items(code);
        CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(date);
        CREATE INDEX IF NOT EXISTS idx_items_sale ON sale_items(sale_id);
        CREATE INDEX IF NOT EXISTS idx_cash_date ON cash_ledger(date);
        """)
