from fastapi import APIRouter, HTTPException
from typing import Dict, List
from analytics.volume_tracker import VolumeTracker
from datetime import datetime, timedelta

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/volume")
async def get_volume_analytics(timeframe: str = "24h"):
    """Get trading volume analytics for the specified timeframe"""
    try:
        tracker = VolumeTracker()

        # Convert timeframe to timedelta
        if timeframe == "24h":
            delta = timedelta(hours=24)
        elif timeframe == "7d":
            delta = timedelta(days=7)
        else:
            delta = timedelta(hours=24)  # Default to 24h

        start_time = datetime.now() - delta
        return tracker.get_volume_analytics(start_time)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance")
async def get_performance_metrics():
    """Get trading performance metrics"""
    try:
        tracker = VolumeTracker()
        return {
            "total_profit": tracker.get_total_profit(),
            "roi": tracker.get_roi(),
            "price_impact": tracker.get_price_impact(),
            "wallet_performance": tracker.get_wallet_performance()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trades")
async def get_trade_history(limit: int = 50):
    """Get recent trade history"""
    try:
        tracker = VolumeTracker()
        return tracker.get_trade_history(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/positions")
async def get_positions():
    """Get current positions with risk metrics"""
    try:
        tracker = VolumeTracker()
        return {
            "positions": tracker.get_positions(),
            "price_impacts": tracker.get_price_impacts()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
