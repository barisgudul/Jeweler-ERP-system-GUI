#!/usr/bin/env python3
"""
Dashboard başlatma testi
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

try:
    from pages.dashboard import DashboardPage
    from data.service import DataService

    # DataService oluştur
    service = DataService('orbitx.db')

    # Dashboard oluştur
    dashboard = DashboardPage(service)

    print('✅ Dashboard başarıyla oluşturuldu!')
    print(f'   - Data servisi: {"Evet" if dashboard.data else "Hayır"}')
    print(f'   - Son işlemler limiti: {dashboard._recent_max}')
    print(f'   - recent_layout var mı: {"Evet" if hasattr(dashboard, "recent_layout") else "Hayır"}')

    # reload_recent_from_db metodunu test et
    dashboard.reload_recent_from_db()
    print('✅ reload_recent_from_db başarıyla çalıştı!')

except Exception as e:
    print(f'❌ Hata: {e}')
    import traceback
    traceback.print_exc()
