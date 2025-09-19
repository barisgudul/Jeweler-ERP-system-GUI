# app/data/service.py
try:
    from PyQt6.QtCore import QObject, pyqtSignal
except Exception:
    # Fallback shim for headless test environments where PyQt6 is not available.
    class _SignalPlaceholder:
        def __init__(self, *args, **kwargs):
            pass
        def emit(self, *a, **k):
            return None

    class QObject:
        def __init__(self, *args, **kwargs):
            pass

    def pyqtSignal(*args, **kwargs):
        return _SignalPlaceholder()
from .db import DB
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pages.parameters import parse_money
from random import randint, uniform, choice
from datetime import datetime

class DataService(QObject):
    stockChanged = pyqtSignal()
    customersChanged = pyqtSignal()
    cashChanged = pyqtSignal()
    saleCommitted = pyqtSignal(dict)  # {sale_id, total, paid, due, ...}
    marketDataUpdated = pyqtSignal()

    CATEGORIES = ["Bilezik","Yüzük","Kolye","Küpe","Külçe","Gram"]

    def __init__(self, path="orbitx.db", parent=None):
        super().__init__(parent)
        self.db = DB(path)
        # cached market data from external API
        self.market_data = {}

    # --- seed ---
    MOCK_STOCK = [
        {"Kod":"STK0001","Ad":"Bilezik 22 Ayar","Kategori":"Bilezik","Gram":8.20,"Stok":5,"Fiyat":21520},
        {"Kod":"STK0002","Ad":"Bilezik 18 Ayar","Kategori":"Bilezik","Gram":7.50,"Stok":7,"Fiyat":17600},
        {"Kod":"STK0003","Ad":"Yüzük 22 Ayar","Kategori":"Yüzük","Gram":4.50,"Stok":12,"Fiyat":14430},
        {"Kod":"STK0004","Ad":"Yüzük 18 Ayar","Kategori":"Yüzük","Gram":3.80,"Stok":15,"Fiyat": 9970},
        {"Kod":"STK0005","Ad":"Kolye 14 Ayar","Kategori":"Kolye","Gram":6.00,"Stok":9,"Fiyat": 8450},
        {"Kod":"STK0006","Ad":"Külçe 24 Ayar 10g","Kategori":"Külçe","Gram":10.0,"Stok":20,"Fiyat": 9500},
        {"Kod":"STK0007","Ad":"Gram Altın","Kategori":"Gram","Gram":1.00,"Stok":200,"Fiyat": 950},
        {"Kod":"STK0008","Ad":"Şahmeran 22 Ayar","Kategori":"Bilezik","Gram":9.10,"Stok":4,"Fiyat":23800},
        {"Kod":"STK0009","Ad":"Küpe 18 Ayar","Kategori":"Küpe","Gram":2.60,"Stok":30,"Fiyat": 4800},
        {"Kod":"STK0010","Ad":"Kolye 22 Ayar","Kategori":"Kolye","Gram":5.90,"Stok":6,"Fiyat":19500}
    ]

    def seed_if_empty(self, customers_list, products_list=None):
        with self.db.tx() as cx:
            if cx.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 0:
                for row in customers_list:
                    name, phone = (row.split(" — ", 1) + [""])[:2]
                    cx.execute("INSERT INTO customers(name, phone) VALUES(?,?)",(name.strip(), phone.strip()))
            if cx.execute("SELECT COUNT(*) FROM stock_items").fetchone()[0] == 0:
                for p in (products_list or self.MOCK_STOCK):
                    cx.execute("""INSERT OR IGNORE INTO stock_items
                        (code,name,category,gram,qty,sell_price)
                        VALUES (?,?,?,?,?,?)""",
                        (p["Kod"], p["Ad"], p.get("Kategori"), float(p.get("Gram",0)),
                         int(p.get("Stok",0)), float(p.get("Fiyat",0))))
        self.customersChanged.emit()
        self.stockChanged.emit()

    def seed_fake_stock(self, *, n: int = 60, replace: bool = False):
        """
        Demo/test için sahte stok üretir ve gerçek veritabanına yazar.
        - replace=True ise mevcut stokları temizler.
        - Satış/alış yaptığınızda qty alanı gerçek zamanlı değişir (create_sale zaten yapıyor).
        """
        with self.db.tx() as cx:
            if replace:
                cx.execute("DELETE FROM stock_moves")
                cx.execute("DELETE FROM stock_items")

            for i in range(n):
                code = f"STK{i+1:04}"
                cat  = self.CATEGORIES[i % len(self.CATEGORIES)]
                name = f"{cat} Ürün {i+1}"
                ayar = 22 if randint(0,1) else 24
                milyem = 916.00 if ayar == 22 else 995.00
                gram = round(uniform(0.50, 25.00), 2)
                qty  = randint(1, 25)

                buy_price  = round(uniform(500, 5000), 2)
                sell_price = round(buy_price * uniform(1.10, 1.45), 2)

                isc_tip     = choice(["Milyem","Gram","TL"])
                isc_alinan  = round(uniform(0,20), 2)
                isc_verilen = round(uniform(0,20), 2)
                vat         = 20.0
                critical    = randint(2, 10)

                cx.execute(
                    """INSERT OR REPLACE INTO stock_items
                       (code,name,category,milyem,ayar,gram,qty,buy_price,sell_price,
                        isc_tip,isc_alinan,isc_verilen,vat,critical_qty)
                       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (code, name, cat, milyem, ayar, gram, qty, buy_price, sell_price,
                     isc_tip, isc_alinan, isc_verilen, vat, critical)
                )

        self.stockChanged.emit()

    def upsert_stock_item(self, item_data: dict) -> dict:
        """
        Stok öğesi ekler veya günceller (code'a göre).
        item_data: {'code', 'name', 'category', 'milyem', 'ayar', 'gram', 'qty', 'buy_price', 'sell_price',
                   'isc_tip', 'isc_alinan', 'isc_verilen', 'vat', 'critical_qty'}
        """
        with self.db.tx() as cx:
            # Mevcut kaydı kontrol et
            existing = cx.execute("SELECT id FROM stock_items WHERE code=?", (item_data["code"],)).fetchone()

            if existing:
                # Güncelleme
                cx.execute("""UPDATE stock_items SET
                             name=?, category=?, milyem=?, ayar=?, gram=?, qty=?, buy_price=?, sell_price=?,
                             isc_tip=?, isc_alinan=?, isc_verilen=?, vat=?, critical_qty=?
                             WHERE code=?""",
                          (item_data["name"], item_data["category"], item_data["milyem"], item_data["ayar"],
                           item_data["gram"], item_data["qty"], item_data["buy_price"], item_data["sell_price"],
                           item_data["isc_tip"], item_data["isc_alinan"], item_data["isc_verilen"],
                           item_data["vat"], item_data["critical_qty"], item_data["code"]))
                stock_id = existing["id"]
                message = "Stok kaydı başarıyla güncellendi."
            else:
                # Yeni ekleme
                cx.execute("""INSERT INTO stock_items
                             (code, name, category, milyem, ayar, gram, qty, buy_price, sell_price,
                              isc_tip, isc_alinan, isc_verilen, vat, critical_qty)
                             VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                          (item_data["code"], item_data["name"], item_data["category"], item_data["milyem"],
                           item_data["ayar"], item_data["gram"], item_data["qty"], item_data["buy_price"],
                           item_data["sell_price"], item_data["isc_tip"], item_data["isc_alinan"],
                           item_data["isc_verilen"], item_data["vat"], item_data["critical_qty"]))
                stock_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
                message = "Stok kaydı başarıyla eklendi."

        self.stockChanged.emit()
        return {"success": True, "message": message, "stock_id": stock_id}

    def delete_stock_item(self, code: str) -> dict:
        """Stok öğesini siler (code'a göre)"""
        with self.db.tx() as cx:
            # İlişkili kayıtları kontrol et
            sale_items_count = cx.execute("SELECT COUNT(*) FROM sale_items WHERE code=?", (code,)).fetchone()[0]
            stock_moves_count = cx.execute("SELECT COUNT(*) FROM stock_moves WHERE stock_id IN (SELECT id FROM stock_items WHERE code=?)", (code,)).fetchone()[0]

            if sale_items_count > 0 or stock_moves_count > 0:
                return {
                    "success": False,
                    "message": f"Bu stok öğesi {sale_items_count} satış kaydı ve {stock_moves_count} hareket kaydı ile ilişkilidir. Silinemez."
                }

            # Stok öğesini sil
            cx.execute("DELETE FROM stock_items WHERE code=?", (code,))
            deleted_count = cx.execute("SELECT changes()").fetchone()[0]

        if deleted_count > 0:
            self.stockChanged.emit()
            return {"success": True, "message": "Stok kaydı başarıyla silindi."}
        else:
            return {"success": False, "message": "Stok kaydı bulunamadı."}

    def seed_demo_if_empty(self):
        """İlk kurulumda: müşteri + stok boşsa doldur."""
        customers = [
            "Ahmet Yılmaz — 5xx xxx xx xx",
            "Gizem Yıldız — 5xx xxx xx xx",
            "Burak Aydın — 5xx xxx xx xx",
            "Ecem Balkaya — 5xx xxx xx xx",
        ]
        self.seed_if_empty(customers_list=customers, products_list=None)  # MOCK_STOCK da hazır
        # Stok hâlâ boşsa daha zengin sahte stok üret:
        with self.db.tx() as cx:
            cnt = cx.execute("SELECT COUNT(*) FROM stock_items").fetchone()[0]
        if cnt == 0:
            self.seed_fake_stock(n=80, replace=False)

    # --- listeler ---
    def list_customers(self):
        rows = self.db.cx.execute("SELECT * FROM customers ORDER BY name").fetchall()
        return [dict(r) for r in rows]

    def list_stock(self):
        rows = self.db.cx.execute("SELECT * FROM stock_items ORDER BY code").fetchall()
        return [dict(r) for r in rows]

    def list_cash(self):
        rows = self.db.cx.execute("SELECT * FROM cash_ledger ORDER BY date DESC, id DESC").fetchall()
        return [dict(r) for r in rows]

    # --- external market data ---
    def fetch_market_prices(self, url: str = "https://displaydata01.orbitbulut.com/eyyupoglu_altin_v1/verileriGetir?tip=altin", timeout: int = 6, apply_to_stock: bool = False):
        """Fetch market gold/altar prices from external API and cache them in self.market_data.
        Emits marketDataUpdated on success. Does not raise on network errors.
        """
        try:
            # prefer requests if available
            try:
                import requests
                resp = requests.get(url, timeout=timeout)
                resp.raise_for_status()
                data = resp.json()
            except Exception:
                # fallback to urllib
                import urllib.request, json
                with urllib.request.urlopen(url, timeout=timeout) as u:
                    data = json.loads(u.read().decode('utf-8'))

            # normalize into dict keyed by kod
            md = {}
            for item in data:
                kod = item.get('kod') or item.get('ad')
                if not kod:
                    continue
                md[kod] = {
                    'id': item.get('id'),
                    'name': item.get('yeni_ad') or item.get('ad'),
                    'kod': kod,
                    'alis': float(item.get('alis') or 0.0),
                    'satis': float(item.get('satis') or 0.0),
                    'kapanis': float(item.get('kapanis') or 0.0),
                    'tarih': item.get('tarih')
                }

            self.market_data = md
            # Optionally apply market sell prices to existing stock items (match by code or name)
            if apply_to_stock:
                try:
                    with self.db.tx() as cx:
                        for kod, info in md.items():
                            # Try match by code first
                            updated = cx.execute("UPDATE stock_items SET sell_price=? WHERE code=?",
                                                (info['satis'], kod)).fetchone()
                            # If no row updated, try match by name (yeni_ad)
                            if cx.execute("SELECT changes()").fetchone()[0] == 0:
                                cx.execute("UPDATE stock_items SET sell_price=? WHERE name LIKE ?",
                                           (info['satis'], f"%{info['name']}%"))
                except Exception:
                    pass
                try:
                    self.stockChanged.emit()
                except Exception:
                    pass
            try:
                self.marketDataUpdated.emit()
            except Exception:
                pass
            return md
        except Exception as e:
            # network error or parsing error, don't raise to caller; return empty
            return {}

    # --- yardımcılar ---
    def _customer_id(self, display_text: str):
        if not display_text:
            return None
        name, phone = (display_text.split(" — ", 1) + [""])[:2]
        row = self.db.cx.execute("SELECT id FROM customers WHERE name=? AND phone=?", (name.strip(), phone.strip())).fetchone()
        if row: return row["id"]
        with self.db.tx() as cx:
            cx.execute("INSERT INTO customers(name, phone) VALUES(?,?)", (name.strip(), phone.strip()))
            return cx.execute("SELECT last_insert_rowid()").fetchone()[0]

    def _stock_by_code(self, cx, code):
        return cx.execute("SELECT * FROM stock_items WHERE code=?", (code,)).fetchone()

    # --- kasa kaydı ---
    def record_cash_entry(self, *, date, time, account, type, category, description, amount, customer_id=None, sale_id=None, ref_no=None):
        # Ensure time is populated (DB/UI expects a time column shown in Kasa Defteri)
        if not time:
            # store hours:minutes
            time = datetime.now().strftime("%H:%M")

        # Persist migrated fields as well (ref_no, currency_code, amount_foreign, fx_rate, type_code)
        # Keep signature backward-compatible by using defaults where callers don't provide them.
        with self.db.tx() as cx:
            cx.execute("""INSERT INTO cash_ledger(date,time,account,type,category,description,amount,customer_id,sale_id,
                          ref_no,currency_code,amount_foreign,fx_rate,type_code)
                          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                       (date, time, account, type, category, description, float(amount), customer_id, sale_id,
                        ref_no, '00', 0.0, 1.0, None))
        self.cashChanged.emit()

    # --- çekirdek satış/alış ---
    def create_sale(self, header: dict, items: list[dict]) -> dict:
        """
        header = {'type','doc_no','date','notes','customer_text','pay_type','paid_amount','discount'}
        items  = [{'code','name','gram','qty','unit_price','milyem','iscilik','line_total'}, ...]
        """
        is_sale = header["type"] == "Satış"
        cust_id = self._customer_id(header.get("customer_text",""))

        # AŞIRI SATIŞ KONTROLÜ: Satış için yeterli stok var mı kontrol et
        if is_sale:
            insufficient_stock = []
            for it in items:
                row = self.db.cx.execute("SELECT * FROM stock_items WHERE code=?", (it["code"],)).fetchone()
                if row:
                    current_qty = row["qty"]
                    requested_qty = int(it["qty"])
                    if requested_qty > current_qty:
                        insufficient_stock.append({
                            "code": it["code"],
                            "name": it["name"],
                            "requested": requested_qty,
                            "available": current_qty
                        })
                else:
                    insufficient_stock.append({
                        "code": it["code"],
                        "name": it["name"],
                        "requested": int(it["qty"]),
                        "available": 0
                    })

            if insufficient_stock:
                error_msg = "Yetersiz stok:\n" + "\n".join([
                    f"- {item['code']} ({item['name']}): {item['requested']} adet istenen, {item['available']} adet mevcut"
                    for item in insufficient_stock
                ])
                raise ValueError(error_msg)

        gross = sum(parse_money(i["line_total"]) for i in items)
        disc  = parse_money(header.get("discount",0.0))
        total = max(0.0, gross - disc)

        paid_req = parse_money(header.get("paid_amount",0.0))
        # ETKİN ÖDEME: toplamı aşan ödeme “para üstü”dür → cariye/deftere net yansımaz
        paid_eff = min(paid_req, total) if header.get("pay_type") != "Veresiye" else 0.0
        due = round(total - paid_eff, 2)

        with self.db.tx() as cx:
            cx.execute("""INSERT INTO sales(type,doc_no,date,notes,customer_id,pay_type,paid_amount,discount,total,due)
                          VALUES (?,?,?,?,?,?,?,?,?,?)""",
                       (header["type"], header.get("doc_no"), header["date"], header.get("notes"),
                        cust_id, header.get("pay_type"), paid_eff, disc, total, due))
            sale_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]

            for it in items:
                row = self._stock_by_code(cx, it["code"])
                stock_id = row["id"] if row else None

                # Eğer ALIŞ işlemi ise ve stokta kayıt yoksa, yeni bir stok öğesi oluştur
                # (küçük demo/otomatik-yansıtma). Böylece satın alınan ürünler stokta görünür.
                if not stock_id and not is_sale:
                    try:
                        cx.execute("INSERT INTO stock_items(code,name,gram,qty) VALUES (?,?,?,?)",
                                   (it["code"], it["name"], parse_money(it.get("gram", 0)), 0))
                        stock_id = cx.execute("SELECT last_insert_rowid()").fetchone()[0]
                        # Yeniden oku (isteğe bağlı, burada sadece id yeterli)
                        row = self._stock_by_code(cx, it["code"])
                    except Exception:
                        # Eğer ekleme başarısız olursa devam et (mevcut davranışı bozmamak için)
                        stock_id = None
                cx.execute("""INSERT INTO sale_items(sale_id,stock_id,code,name,gram,qty,unit_price,milyem,iscilik,line_total)
                              VALUES (?,?,?,?,?,?,?,?,?,?)""",
                           (sale_id, stock_id, it["code"], it["name"], parse_money(it.get("gram",0)), int(it["qty"]),
                            parse_money(it["unit_price"]), it.get("milyem"), parse_money(it.get("iscilik",0)), parse_money(it["line_total"])))
                if stock_id:
                    delta = -int(it["qty"]) if is_sale else +int(it["qty"])
                    cx.execute("UPDATE stock_items SET qty = MAX(0, qty + ?) WHERE id=?", (delta, stock_id))
                    cx.execute("""INSERT INTO stock_moves(stock_id,sale_id,move_type,qty,note,date)
                                  VALUES (?,?,?,?,?,?)""",
                               (stock_id, sale_id, 'OUT' if is_sale else 'IN', abs(delta), header["type"], header["date"]))

            if cust_id:
                if total > 0:
                    cx.execute("""INSERT INTO customer_ledger(customer_id,sale_id,direction,amount,desc,date)
                                  VALUES (?,?,?,?,?,?)""",
                               (cust_id, sale_id, 'Borç' if is_sale else 'Alacak', total if is_sale else -total,
                                header["type"], header["date"]))
                    cx.execute("UPDATE customers SET balance = balance + ?, last_txn_at=? WHERE id=?",
                               (total if is_sale else -total, header["date"], cust_id))
                if paid_eff > 0:
                    cx.execute("""INSERT INTO customer_ledger(customer_id,sale_id,direction,amount,desc,date)
                                  VALUES (?,?,?,?,?,?)""",
                               (cust_id, sale_id, 'Alacak', paid_eff, f'Ödeme ({header.get("pay_type")})', header["date"]))
                    cx.execute("UPDATE customers SET balance = balance - ? WHERE id=?", (paid_eff, cust_id))

        # Kasa/Banka defteri (net tahsilat = paid_eff)
        if paid_eff > 0:
            account = "Kasa" if (header.get("pay_type","").lower() == "nakit") else "Banka — POS"
            if is_sale:
                # Satış → kasa GİRİŞ
                self.record_cash_entry(
                    date=header["date"], time=None, account=account, type='Giriş',
                    category='Satış Tahsilatı', description=header.get("doc_no",""),
                    amount=paid_eff, customer_id=cust_id, sale_id=sale_id, ref_no=header.get("doc_no")
                )
            else:
                # Alış (müşteriden ürün aldık) → kasa ÇIKIŞ
                self.record_cash_entry(
                    date=header["date"], time=None, account=account, type='Çıkış',
                    category='Alım Ödemesi', description=header.get("doc_no",""),
                    amount=paid_eff, customer_id=cust_id, sale_id=sale_id, ref_no=header.get("doc_no")
                )

        payload = {"sale_id": sale_id, "type": header["type"],
                   "date": header["date"], "doc_no": header.get("doc_no"),
                   "customer_id": cust_id, "total": total, "paid": paid_eff, "due": due,
                   "pay_type": header.get("pay_type")}
        self.saleCommitted.emit(payload)
        self.stockChanged.emit(); self.customersChanged.emit()
        return payload

    def get_recent_transactions(self, limit: int = 7):
        """Son işlemleri getirir"""
        query = """
        SELECT
            s.id,
            s.type as kind,
            s.date,
            s.doc_no,
            COALESCE(c.name, 'Nakit') as who,
            s.total,
            s.pay_type,
            s.due,
            s.created_at
        FROM sales s
        LEFT JOIN customers c ON s.customer_id = c.id
        ORDER BY s.date DESC, s.id DESC
        LIMIT ?
        """
        rows = self.db.cx.execute(query, (limit,)).fetchall()
        return [dict(row) for row in rows]