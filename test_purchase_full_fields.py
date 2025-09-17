import os
from app.data.service import DataService


def test_full_purchase_with_iscilik_and_paid(tmp_path):
    db_file = tmp_path / "test_orbitx_full.db"
    svc = DataService(str(db_file))

    header = {
        'type': 'Alış',
        'doc_no': 'ALIS_FULL_001',
        'date': '2025-09-17',
        'notes': 'Full test purchase',
        'customer_text': 'GoldCenter — 0555 555 6666',
        'pay_type': 'Nakit',
        'paid_amount': '500',
        'discount': '0'
    }

    items = [
        {'code': 'STKTESTFULL1', 'name': 'Test Ürün Full', 'gram': '5.00', 'qty': 2, 'unit_price': '200', 'milyem': None, 'iscilik': '200', 'line_total': '600'}
    ]

    payload = svc.create_sale(header, items)
    assert payload['type'] == 'Alış'
    # sale must exist
    with svc.db.tx() as cx:
        sale = cx.execute("SELECT * FROM sales WHERE id=?", (payload['sale_id'],)).fetchone()
        assert sale is not None

        # cash_ledger should have a Çıkış record for paid amount
        cash = cx.execute("SELECT * FROM cash_ledger WHERE sale_id=?", (payload['sale_id'],)).fetchone()
        assert cash is not None
        assert cash['type'] == 'Çıkış'
        assert float(cash['amount']) == 500.0

        # stock item should be created
        stock = cx.execute("SELECT * FROM stock_items WHERE code=?", ('STKTESTFULL1',)).fetchone()
        assert stock is not None
        assert int(stock['qty']) >= 2

        # stock_moves IN exists
        move = cx.execute("SELECT * FROM stock_moves WHERE stock_id=?", (stock['id'],)).fetchone()
        assert move is not None
        assert move['move_type'] == 'IN'
        assert int(move['qty']) >= 2

    try:
        os.remove(str(db_file))
    except Exception:
        pass
