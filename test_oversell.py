#!/usr/bin/env python3
"""
Aşırı satış kontrolü testi
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

from data.service import DataService

def test_oversell():
    service = DataService('orbitx.db')
    all_stock = service.list_stock()

    # Az stoğu olan bir ürün bul
    low_stock_item = None
    for item in all_stock:
        if item['qty'] < 5 and item['qty'] > 0:
            low_stock_item = item
            break

    if not low_stock_item:
        print('❌ Yeterli az stoğu olan ürün bulunamadı')
        return

    code = low_stock_item['code']
    name = low_stock_item['name']
    available = low_stock_item['qty']
    requested = available + 5  # Fazla stok iste

    print(f'✓ Test ürünü: {code} - {name}')
    print(f'✓ Mevcut adet: {available}, İstenen: {requested}')

    # Aşırı satış testi
    sale_header = {
        'type': 'Satış',
        'doc_no': 'OVERSELL_TEST',
        'date': '2025-09-15',
        'customer_text': 'Test Müşteri',
        'pay_type': 'Nakit',
        'paid_amount': '100.00',
        'discount': '0.00'
    }

    sale_items = [{
        'code': code,
        'name': name,
        'qty': str(requested),
        'unit_price': low_stock_item['sell_price'],
        'line_total': str(low_stock_item['sell_price'] * requested)
    }]

    try:
        result = service.create_sale(sale_header, sale_items)
        print('❌ AŞIRI SATIŞ BAŞARILI OLDU! (Bu beklenmiyordu)')
    except ValueError as e:
        print(f'✅ AŞIRI SATIŞ BLOKLANDI: {e}')
    except Exception as e:
        print(f'❌ Beklenmeyen hata: {e}')

if __name__ == "__main__":
    print("=== Aşırı Satış Testi ===")
    test_oversell()
    print("=== Test Tamamlandı ===")
