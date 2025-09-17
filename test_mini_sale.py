#!/usr/bin/env python3
"""
Mini satış testi: Mevcut stoktan 2 adet satan basit bir satış işlemi
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

from data.service import DataService

def test_mini_sale():
    # DataService oluştur
    service = DataService('orbitx.db')

    # Mevcut stok durumunu kontrol et
    all_stock = service.list_stock()
    print(f"✓ Toplam stok öğesi sayısı: {len(all_stock)}")

    if not all_stock:
        print("❌ Stok boş! Önce sahte stok üretin: python test_seed.py")
        return

    # İlk ürünü seç
    first_item = all_stock[0]
    code = first_item["code"]
    name = first_item["name"]
    initial_qty = first_item["qty"]

    print(f"✓ Test ürünü: {code} - {name} (Mevcut adet: {initial_qty})")

    if initial_qty < 2:
        print(f"❌ Bu ürünün yeterli stoğu yok! (İstenen: 2, Mevcut: {initial_qty})")
        return

    # Mini satış verisi hazırla
    sale_header = {
        "type": "Satış",
        "doc_no": "TEST001",
        "date": "2025-09-15",
        "notes": "Mini satış testi",
        "customer_text": "Ahmet Yılmaz — 5xx xxx xx xx",
        "pay_type": "Nakit",
        "paid_amount": "200.00",
        "discount": "0.00"
    }

    sale_items = [{
        "code": code,
        "name": name,
        "gram": first_item["gram"],
        "qty": "2",
        "unit_price": first_item["sell_price"],
        "milyem": first_item["milyem"],
        "iscilik": "0.00",
        "line_total": str(first_item["sell_price"] * 2)
    }]

    print("✓ Satış işlemi başlatılıyor...")

    try:
        # Satış işlemini gerçekleştir
        result = service.create_sale(sale_header, sale_items)

        print("✅ Satış işlemi başarılı!")
        print(f"   - Satış ID: {result['sale_id']}")
        print(f"   - Toplam tutar: {result['total']:.2f} ₺")
        print(f"   - Ödenen: {result['paid']:.2f} ₺")
        print(f"   - Ödeme tipi: {result['pay_type']}")

        # Stok durumunu yeniden kontrol et
        updated_stock = service.list_stock()
        updated_item = next((item for item in updated_stock if item["code"] == code), None)

        if updated_item:
            new_qty = updated_item["qty"]
            print(f"✓ Stok güncellendi: {initial_qty} → {new_qty} (Azalma: {initial_qty - new_qty})")
        else:
            print("❌ Stok öğesi bulunamadı!")

        # Stok hareketlerini kontrol et
        stock_moves = service.db.cx.execute("""
            SELECT * FROM stock_moves
            WHERE stock_id IN (SELECT id FROM stock_items WHERE code=?)
            ORDER BY date DESC, id DESC LIMIT 5
        """, (code,)).fetchall()

        print(f"✓ Son stok hareketleri ({len(stock_moves)} adet):")
        for move in stock_moves:
            move_dict = dict(move)
            print(f"   - {move_dict['move_type']} | {move_dict['qty']} adet | {move_dict['note']} | {move_dict['date']}")

    except ValueError as e:
        print(f"❌ Stok kontrol hatası: {e}")
    except Exception as e:
        print(f"❌ Satış hatası: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== Mini Satış Testi ===")
    test_mini_sale()
    print("=== Test Tamamlandı ===")
