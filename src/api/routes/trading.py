from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from ...trading.trade_executor import TradeExecutor
from ...trading.bundler import Bundler
from ...wallet.wallet_manager import WalletManager
from ...utils.config import Config
from ..models.trading import TradeRequest, TradeResponse, WalletInfo, TradingMode
from ..websocket.manager import WebSocketManager

router = APIRouter(prefix="/trading", tags=["trading"])
ws_manager = WebSocketManager()

@router.get("/modes")
async def get_trading_modes():
    """Get available trading modes and their configurations"""
    config = Config()
    return config.trading_modes

@router.post("/execute", response_model=TradeResponse)
async def execute_trade(trade_request: TradeRequest):
    """Execute a trade with specified parameters"""
    try:
        # Initialize components
        wallet_manager = WalletManager()
        bundler = Bundler(wallet_manager)
        trade_executor = TradeExecutor(bundler)

        # Execute trade
        result = await trade_executor.execute_trade(
            mode=trade_request.mode,
            token_address=trade_request.token_address,
            amount=trade_request.amount,
            wallet_count=trade_request.wallet_count,
            slippage=trade_request.slippage
        )

        # Broadcast trade update
        await ws_manager.broadcast_trade({
            "trade_id": result.get("trade_id"),
            "status": "completed",
            "transaction_hash": result.get("transaction_hash")
        })

        return TradeResponse(
            success=True,
            transaction_hash=result.get("transaction_hash")
        )
    except Exception as e:
        return TradeResponse(
            success=False,
            error=str(e)
        )

@router.get("/wallets", response_model=List[WalletInfo])
async def get_wallets():
    """Get information about all managed wallets"""
    try:
        wallet_manager = WalletManager()
        wallets = wallet_manager.get_all_wallets()
        return [
            WalletInfo(
                address=wallet.address,
                balance=wallet.balance,
                trades=wallet.trade_history
            ) for wallet in wallets
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
