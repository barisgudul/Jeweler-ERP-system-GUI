import os
import tempfile
from app.data.service import DataService


def test_purchase_creates_stock_and_moves(tmp_path):
    # Create a temporary DB file path
    db_file = tmp_path / "test_orbitx.db"
    svc = DataService(str(db_file))

    # Ensure DB starts empty
    rows = svc.list_stock()
    assert isinstance(rows, list)

    header = {
        'type': 'Alış',
        'doc_no': 'TEST_ALIS_0001',
        'date': '2025-09-17',
        'notes': 'Test purchase',
        'customer_text': 'GoldCenter — 0555 555 6666',
        'pay_type': 'Nakit',
        'paid_amount': '0',
        'discount': '0'
    }

    # Item code that does not exist yet
    items = [
        {'code': 'STKTEST100', 'name': 'Test Ürün', 'gram': '10.00', 'qty': 1, 'unit_price': '1000', 'milyem': None, 'iscilik': '200', 'line_total': '1200'}
    ]

    payload = svc.create_sale(header, items)
    assert payload['type'] == 'Alış'

    # After create_sale, stock_items should contain our code
    stocked = [s for s in svc.list_stock() if s['code'] == 'STKTEST100']
    assert len(stocked) == 1
    stock_row = stocked[0]
    # Quantity should be at least 1 given the purchase
    assert stock_row['qty'] >= 1

    # Check stock_moves for an IN move
    with svc.db.tx() as cx:
        moves = cx.execute("SELECT * FROM stock_moves WHERE stock_id=?", (stock_row['id'],)).fetchall()
        assert len(moves) >= 1
        move = moves[0]
        assert move['move_type'] == 'IN'
        assert move['qty'] >= 1

    # Clean up
    try:
        os.remove(str(db_file))
    except Exception:
        pass
