#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

from data.db import DB

try:
    db = DB()
    print("✓ Veritabanı bağlantısı başarılı")

    tables = [row[0] for row in db.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print("✓ Oluşturulan tablolar:", tables)

    # Test verisi ekle
    db.conn.execute("INSERT OR IGNORE INTO customers(name, phone) VALUES (?, ?)", ("Test Müşteri", "0555 123 4567"))
    db.conn.execute("INSERT OR IGNORE INTO stock_items(code, name, qty, sell_price) VALUES (?, ?, ?, ?)",
                   ("TEST001", "Test Ürün", 10, 100.0))
    db.conn.commit()

    customers = db.conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    stock = db.conn.execute("SELECT COUNT(*) FROM stock_items").fetchone()[0]

    print(f"✓ Müşteri sayısı: {customers}")
    print(f"✓ Stok öğesi sayısı: {stock}")

    # Service katmanını test et
    print("\n--- Service Katmanı Testi ---")
    from data.service import DataService
    service = DataService()
    print("✓ DataService oluşturuldu")

    # Seed testi
    print("✓ Seed işlemi başlatılıyor...")
    service.seed_if_empty([], [])  # Boş listelerle test

    customers_after_seed = service.list_customers()
    stock_after_seed = service.list_stock()
    print(f"✓ Seed sonrası müşteri sayısı: {len(customers_after_seed)}")
    print(f"✓ Seed sonrası stok öğesi sayısı: {len(stock_after_seed)}")

except Exception as e:
    print(f"✗ Hata: {e}")
    import traceback
    traceback.print_exc()
