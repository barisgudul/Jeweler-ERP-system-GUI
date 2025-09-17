#!/usr/bin/env python3
"""
Dashboard veri testi
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

from data.service import DataService

def test_dashboard_data():
    service = DataService('orbitx.db')

    # Mevcut satış verilerini kontrol et
    sales = service.db.cx.execute('SELECT COUNT(*) FROM sales').fetchone()[0]
    print(f'✓ Mevcut satış kaydı sayısı: {sales}')

    # Son işlemleri göster
    recent_sales = service.db.cx.execute('''
        SELECT s.type, s.date, s.total, c.name, c.phone
        FROM sales s
        LEFT JOIN customers c ON c.id = s.customer_id
        ORDER BY s.id DESC LIMIT 3
    ''').fetchall()

    print('✓ Son işlemler:')
    for sale in recent_sales:
        print(f'  - {sale["type"]} | {sale["date"]} | {sale["total"]} ₺ | {sale["name"]}')

if __name__ == "__main__":
    test_dashboard_data()
