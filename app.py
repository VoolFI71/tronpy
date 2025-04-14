from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from database import SessionLocal, WalletRequest
from tronpy import Tron
from pydantic import BaseModel
from typing import List
from tronpy import Tron
from tronpy.providers import HTTPProvider

api_keys = ["661a0379-4588-4708-9e6a-21c0d3cf06e2"]
provider = HTTPProvider(api_key=api_keys[0])
tron = Tron(provider)
print(dir(tron)) 

app = FastAPI()

class WalletInfo(BaseModel):
    address: str

class WalletResponse(BaseModel):
    address: str
    bandwidth: int
    energy: int
    balance: float

class WalletRequestResponse(BaseModel):
    id: int
    address: str
    bandwidth: int
    energy: int
    balance: float

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/wallet_info/")
async def get_wallet_info(wallet: WalletInfo, db: Session = Depends(get_db)):
    try:
        account = tron.get_account(wallet.address)
        
        balance = tron.get_account_balance(wallet.address) / 1_000_000  

        bandwidth = account.get('bandwidth', 0)
        energy = account.get('energy', 0)

        wallet_request = WalletRequest(
            address=wallet.address,
            bandwidth=bandwidth,
            energy=energy,
            balance=balance
        )
        db.add(wallet_request)
        db.commit()
        db.refresh(wallet_request)

        return {
            "address": wallet.address,
            "bandwidth": bandwidth,
            "energy": energy,
            "balance": balance
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/wallet_requests/", response_model=List[WalletRequestResponse])
async def get_wallet_requests(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    requests = db.query(WalletRequest).offset(skip).limit(limit).all()
    return [
        WalletRequestResponse(
            id=req.id,
            address=req.address,
            bandwidth=req.bandwidth,
            energy=req.energy,
            balance=req.balance
        ) for req in requests
    ]