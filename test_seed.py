### test_seed.py ###
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

from data.service import DataService

# DataService oluştur
service = DataService('orbitx.db')

# Mevcut stok sayısını kontrol et
current_stock = len(service.list_stock())
print(f'✓ Mevcut stok sayısı: {current_stock}')

# Yeni sahte stok ekle
print('✓ Sahte stok ekleniyor...')
service.seed_fake_stock(n=20, replace=False)

# Yeni stok sayısını kontrol et
new_stock = len(service.list_stock())
print(f'✓ Yeni stok sayısı: {new_stock}')

# İlk 5 ürünü göster
stock_items = service.list_stock()[:5]
print('✓ İlk 5 ürün:')
for item in stock_items:
    print(f'  - {item["code"]}: {item["name"]} (Adet: {item["qty"]})')
