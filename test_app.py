import pytest
from fastapi.testclient import TestClient
from app import app 
from database import SessionLocal, WalletRequest
from sqlalchemy.orm import sessionmaker

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_get_wallet_info(test_db):
    wallet_address = "TKs3CbvQLE3avYddsX96kQHaPDDr3nT2nw"

    response = client.post("/wallet_info/", json={"address": wallet_address})
    
    assert response.status_code == 200
    data = response.json()
    assert data["address"] == wallet_address
    assert "bandwidth" in data
    assert "energy" in data
    assert "balance" in data

def test_add_wallet_request_unit(test_db):
    wallet_data = {
        "address": "TKs3CbvQLE3avYddsX96kQHaPDDr3nT2nw",
        "bandwidth": 0,
        "energy": 0,
        "balance": 0.000513464937
    }

    wallet_request = WalletRequest(**wallet_data)

    test_db.add(wallet_request)
    test_db.commit()

    saved_wallet = test_db.query(WalletRequest).filter_by(address=wallet_data["address"]).first()
    assert saved_wallet is not None
    assert saved_wallet.bandwidth == wallet_data["bandwidth"]
    assert saved_wallet.energy == wallet_data["energy"]
    assert saved_wallet.balance == wallet_data["balance"]
