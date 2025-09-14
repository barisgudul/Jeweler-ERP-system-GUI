# app/data/service.py
from PyQt6.QtCore import QObject, pyqtSignal
from .db import DB
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pages.parameters import parse_money

class DataService(QObject):
    stockChanged = pyqtSignal()
    customersChanged = pyqtSignal()
    cashChanged = pyqtSignal()
    saleCommitted = pyqtSignal(dict)  # {sale_id, total, paid, due, ...}

    def __init__(self, path="orbitx.db", parent=None):
        super().__init__(parent)
        self.db = DB(path)

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
                for p in (products_list or MOCK_STOCK):
                    cx.execute("""INSERT OR IGNORE INTO stock_items
                        (code,name,category,gram,qty,sell_price)
                        VALUES (?,?,?,?,?,?)""",
                        (p["Kod"], p["Ad"], p.get("Kategori"), float(p.get("Gram",0)),
                         int(p.get("Stok",0)), float(p.get("Fiyat",0))))
        self.customersChanged.emit()
        self.stockChanged.emit()

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
    def record_cash_entry(self, *, date, time, account, type, category, description, amount, customer_id=None, sale_id=None):
        with self.db.tx() as cx:
            cx.execute("""INSERT INTO cash_ledger(date,time,account,type,category,description,amount,customer_id,sale_id)
                          VALUES (?,?,?,?,?,?,?,?,?)""",
                       (date, time, account, type, category, description, float(amount), customer_id, sale_id))
        self.cashChanged.emit()

    # --- çekirdek satış/alış ---
    def create_sale(self, header: dict, items: list[dict]) -> dict:
        """
        header = {'type','doc_no','date','notes','customer_text','pay_type','paid_amount','discount'}
        items  = [{'code','name','gram','qty','unit_price','milyem','iscilik','line_total'}, ...]
        """
        is_sale = header["type"] == "Satış"
        cust_id = self._customer_id(header.get("customer_text",""))

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
                cx.execute("""INSERT INTO sale_items(sale_id,stock_id,code,name,gram,qty,unit_price,milyem,iscilik,line_total)
                              VALUES (?,?,?,?,?,?,?,?,?,?)""",
                           (sale_id, stock_id, it["code"], it["name"], float(it.get("gram",0)), int(it["qty"]),
                            float(it["unit_price"]), it.get("milyem"), float(it.get("iscilik",0)), float(it["line_total"])))
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
                    amount=paid_eff, customer_id=cust_id, sale_id=sale_id
                )
            else:
                # Alış (müşteriden ürün aldık) → kasa ÇIKIŞ
                self.record_cash_entry(
                    date=header["date"], time=None, account=account, type='Çıkış',
                    category='Alım Ödemesi', description=header.get("doc_no",""),
                    amount=paid_eff, customer_id=cust_id, sale_id=sale_id
                )

        payload = {"sale_id": sale_id, "type": header["type"],
                   "date": header["date"], "doc_no": header.get("doc_no"),
                   "customer_id": cust_id, "total": total, "paid": paid_eff, "due": due,
                   "pay_type": header.get("pay_type")}
        self.saleCommitted.emit(payload)
        self.stockChanged.emit(); self.customersChanged.emit()
        return payload
