"""
Volume tracking system for monitoring trading activity and performance.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict

@dataclass
class TradeRecord:
    timestamp: float
    wallet_address: str
    token_address: str
    side: str  # 'buy' or 'sell'
    amount: float
    price: float
    profit_loss: float = 0.0
    price_impact: float = 0.0

    def to_dict(self) -> Dict:
        return asdict(self)

class VolumeTracker:
    def __init__(self):
        self.trades: List[TradeRecord] = []
        self.session_start: Optional[datetime] = None
        self.target_volume: Optional[float] = None
        self.session_duration: Optional[timedelta] = None
        self.initial_balances: Dict[str, float] = {}
        self.price_impacts: Dict[str, float] = {}

    def start_session(self, target_volume: Optional[float] = None, duration_hours: Optional[int] = None):
        """Starts a new trading session with optional volume target or duration"""
        self.session_start = datetime.now()
        self.target_volume = target_volume
        self.session_duration = timedelta(hours=duration_hours) if duration_hours else None
        self.trades = []

    def record_trade(self, trade: TradeRecord):
        """Records a new trade in the session"""
        self.trades.append(trade)

    def track_price_impact(self, token_address: str, pre_price: float, post_price: float) -> float:
        impact = abs(post_price - pre_price) / pre_price
        self.price_impacts[token_address] = impact
        return impact

    def calculate_wallet_pl(self, wallet_address: str) -> Dict[str, float]:
        wallet_pl = {}
        for trade in self.trades:
            if trade.wallet_address == wallet_address:
                token = trade.token_address
                if token not in wallet_pl:
                    wallet_pl[token] = 0.0
                if trade.side == 'buy':
                    wallet_pl[token] -= trade.amount * trade.price
                else:
                    wallet_pl[token] += trade.amount * trade.price
        return wallet_pl

    def calculate_roi(self, wallet_address: str) -> float:
        pl = self.calculate_wallet_pl(wallet_address)
        initial = self.initial_balances.get(wallet_address, 0)
        if initial == 0:
            return 0.0
        return sum(pl.values()) / initial * 100

    def get_session_volume(self) -> float:
        """Calculates total volume for current session"""
        return sum(trade.amount * trade.price for trade in self.trades)

    def get_trade_count(self) -> Dict[str, int]:
        """Gets trade counts by side (buy/sell)"""
        counts = {'buy': 0, 'sell': 0}
        for trade in self.trades:
            counts[trade.side] += 1
        return counts

    def get_wallet_performance(self) -> Dict[str, Dict]:
        """Analyzes performance by wallet"""
        wallet_stats = {}
        for trade in self.trades:
            if trade.wallet_address not in wallet_stats:
                wallet_stats[trade.wallet_address] = {
                    'volume': 0,
                    'trade_count': 0,
                    'buys': 0,
                    'sells': 0
                }
            stats = wallet_stats[trade.wallet_address]
            stats['volume'] += trade.amount * trade.price
            stats['trade_count'] += 1
            stats['buys' if trade.side == 'buy' else 'sells'] += 1
        return wallet_stats

    def get_positions(self) -> Dict[str, Dict]:
        """Get current positions for all wallets"""
        positions = {}
        for trade in self.trades:
            wallet = trade.wallet_address
            token = trade.token_address

            if wallet not in positions:
                positions[wallet] = {}

            if token not in positions[wallet]:
                positions[wallet][token] = {
                    'amount': 0.0,
                    'avg_price': 0.0,
                    'total_cost': 0.0,
                    'unrealized_pl': 0.0
                }

            pos = positions[wallet][token]
            if trade.side == 'buy':
                total_cost = pos['amount'] * pos['avg_price'] + trade.amount * trade.price
                new_amount = pos['amount'] + trade.amount
                pos['avg_price'] = total_cost / new_amount if new_amount > 0 else 0
                pos['amount'] = new_amount
                pos['total_cost'] = total_cost
            else:
                pos['amount'] -= trade.amount
                if pos['amount'] <= 0:
                    pos['amount'] = 0
                    pos['avg_price'] = 0
                    pos['total_cost'] = 0

            pos['unrealized_pl'] = pos['amount'] * (trade.price - pos['avg_price'])

        return positions

    def get_price_impacts(self) -> Dict[str, float]:
        """Get latest price impacts for all tokens"""
        return self.price_impacts

    def generate_report(self) -> Dict:
        """Generates comprehensive session report with P/L metrics"""
        if not self.session_start:
            return {"error": "No active session"}

        duration = datetime.now() - self.session_start
        total_volume = self.get_session_volume()
        trade_counts = self.get_trade_count()
        wallet_stats = self.get_wallet_performance()

        # Add P/L metrics
        for wallet in wallet_stats:
            stats = wallet_stats[wallet]
            stats['profit_loss'] = self.calculate_wallet_pl(wallet)
            stats['roi'] = self.calculate_roi(wallet)
            stats['price_impacts'] = self.price_impacts

        return {
            "session_start": self.session_start.isoformat(),
            "duration": str(duration),
            "total_volume": total_volume,
            "target_volume": self.target_volume,
            "progress": (total_volume / self.target_volume * 100) if self.target_volume else None,
            "trade_counts": trade_counts,
            "wallet_performance": wallet_stats,
            "trades_per_hour": len(self.trades) / (duration.total_seconds() / 3600),
            "cumulative_profit": sum(trade.profit_loss for trade in self.trades)
        }

    def export_session_data(self, filename: str):
        """Exports session data to JSON file"""
        data = {
            "session_info": {
                "start_time": self.session_start.isoformat() if self.session_start else None,
                "target_volume": self.target_volume,
                "session_duration": str(self.session_duration) if self.session_duration else None
            },
            "trades": [trade.to_dict() for trade in self.trades],
            "summary": self.generate_report()
        }

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
