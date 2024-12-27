from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class TradingMode(str, Enum):
    SAFE = "SAFE"
    NORMAL = "NORMAL"
    AGGRESSIVE = "AGGRESSIVE"
    HIGH_FREQUENCY = "HIGH_FREQUENCY"

class SwapRequest(BaseModel):
    wallet_address: str = Field(..., description="Public key of the wallet initiating the swap")
    amount: float = Field(..., gt=0, description="Amount to swap")
    is_buy: bool = Field(..., description="True for buy, False for sell")
    slippage: float = Field(..., ge=0, le=100, description="Slippage tolerance in percentage")
    mode: TradingMode = Field(default=TradingMode.SAFE, description="Trading mode for the swap")

class SwapResponse(BaseModel):
    status: str = Field(..., description="Status of the swap request")
    transaction_id: Optional[str] = Field(None, description="Transaction signature if available")
    error: Optional[str] = Field(None, description="Error message if the swap failed")
