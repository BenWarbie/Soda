from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class TradingMode(str, Enum):
    SAFE = "SAFE"
    NORMAL = "NORMAL"
    AGGRESSIVE = "AGGRESSIVE"
    HIGH_FREQUENCY = "HIGH_FREQUENCY"

class TradeRequest(BaseModel):
    mode: TradingMode
    token_address: str
    amount: float
    wallet_count: Optional[int] = 1
    slippage: Optional[float] = 0.5

class WalletInfo(BaseModel):
    address: str
    balance: float
    trades: List[dict]

class TradeResponse(BaseModel):
    success: bool
    transaction_hash: Optional[str] = None
    error: Optional[str] = None
