#!/usr/bin/env python3
"""
Canlı dashboard güncelleme testi
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

from data.service import DataService

def test_live_update():
    service = DataService('orbitx.db')

    # Yeni bir satış ekle
    sale_header = {
        "type": "Satış",
        "doc_no": "DASHBOARD_TEST",
        "date": "2025-09-15",
        "notes": "Dashboard canlı güncelleme testi",
        "customer_text": "Ahmet Yılmaz — 5xx xxx xx xx",
        "pay_type": "Nakit",
        "paid_amount": "150.00",
        "discount": "0.00"
    }

    # Stok kontrolü - mevcut bir ürünü kullan
    stock_items = service.list_stock()
    if not stock_items:
        print("❌ Stok boş! Önce test_seed.py çalıştırın.")
        return

    test_item = stock_items[0]
    qty_to_sell = min(1, test_item["qty"])  # En fazla 1 adet sat

    if qty_to_sell == 0:
        print("❌ Seçilen ürünün stoğu yok!")
        return

    sale_items = [{
        "code": test_item["code"],
        "name": test_item["name"],
        "gram": test_item["gram"],
        "qty": str(qty_to_sell),
        "unit_price": test_item["sell_price"],
        "milyem": test_item["milyem"],
        "iscilik": "0.00",
        "line_total": str(test_item["sell_price"] * qty_to_sell)
    }]

    print("✓ Dashboard canlı güncelleme testi başlatılıyor...")
    print(f"✓ Satılacak ürün: {test_item['name']} (Kod: {test_item['code']})")
    print(f"✓ Satış miktarı: {qty_to_sell} adet")
    print(f"✓ Toplam tutar: {test_item['sell_price'] * qty_to_sell:.2f} ₺")

    try:
        result = service.create_sale(sale_header, sale_items)
        print("✅ Satış başarıyla eklendi!")
        print(f"   - Satış ID: {result['sale_id']}")
        print(f"   - Dashboard'da 'Son İşlemler' listesinin güncellendiğini kontrol edin")

        # Son işlemleri göster
        recent_sales = service.db.cx.execute('''
            SELECT s.type, s.doc_no, s.date, s.total, c.name
            FROM sales s
            LEFT JOIN customers c ON c.id = s.customer_id
            ORDER BY s.id DESC LIMIT 3
        ''').fetchall()

        print("\n✓ Güncel son işlemler:")
        for i, sale in enumerate(recent_sales, 1):
            print(f"   {i}. {sale['type']} | {sale['doc_no']} | {sale['date']} | {sale['total']} ₺ | {sale['name']}")

    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    test_live_update()
