import pytest
from app import is_fraud_bla

class DummyUser:
    def __init__(self, id, limit, last_location, avg_amount, tx_count):
        self.id = id
        self.transaction_limit = limit
        self.last_location = last_location
        self.avg_amount = avg_amount
        self.tx_count = tx_count

def make_row(id, limit, last_location, avg, txc):
    return {'id': id, 'transaction_limit': limit, 'last_location': last_location, 'avg_amount': avg, 'tx_count': txc}

def test_within_limit():
    u = make_row(1, 100, 'CityA', 50, 2)
    fraud, reason = is_fraud_bla(u, 50, 'CityA')
    assert fraud is False

def test_location_mismatch():
    u = make_row(1, 100, 'CityA', 50, 2)
    fraud, reason = is_fraud_bla(u, 200, 'CityB')
    assert fraud is True
    assert reason == 'location_mismatch'

def test_amount_far_above_avg():
    u = make_row(1, 100, 'CityA', 50, 5)
    fraud, reason = is_fraud_bla(u, 200, 'CityA')
    assert fraud is True
    assert reason == 'amount_far_above_avg'
