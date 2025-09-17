#!/usr/bin/env python3
"""
Müşteri sayfasındaki bakiye kaldırma testini doğrula
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

# Müşteri sayfasındaki değişiklikleri test et
from pages.customers import generate_customers

# Mock müşteriler oluştur
customers = generate_customers(3)
print('✓ Mock müşteriler oluşturuldu:')
for customer in customers:
    print(f'   - {customer["Kod"]}: {customer["AdSoyad"]} | Telefon: {customer["Telefon"]} | Son İşlem: {customer["Son İşlem"]} | Durum: {customer["Durum"]}')
    # Bakiye alanının olmadığını doğrula
    if 'Bakiye' not in customer:
        print('   ✅ Bakiye alanı kaldırıldı')
    else:
        print('   ❌ Bakiye alanı hala var!')

print(f'\n✓ Toplam müşteri sayısı: {len(customers)}')
print('✓ Müşteri alanları:', list(customers[0].keys()) if customers else 'Boş')
