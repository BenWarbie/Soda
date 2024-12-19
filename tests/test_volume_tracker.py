"""
Unit tests for volume tracking functionality.
"""
import pytest
from datetime import datetime, timedelta
from src.analytics.volume_tracker import VolumeTracker, TradeRecord

@pytest.fixture
def volume_tracker():
    """Create VolumeTracker instance for testing"""
    return VolumeTracker()

def test_record_trade(volume_tracker):
    """Test trade recording"""
    trade = TradeRecord(
        timestamp=datetime.now().timestamp(),
        wallet_address="wallet1",
        token_address="token1",
        side="buy",
        amount=1.0,
        price=100.0
    )

    volume_tracker.record_trade(trade)
    assert len(volume_tracker.trades) == 1
    assert volume_tracker.trades[0] == trade

def test_get_session_volume(volume_tracker):
    """Test session volume calculation"""
    # Add test trades
    trades = [
        TradeRecord(
            timestamp=datetime.now().timestamp(),
            wallet_address=f"wallet{i}",
            token_address="token1",
            side="buy",
            amount=1.0,
            price=100.0
        ) for i in range(3)
    ]

    for trade in trades:
        volume_tracker.record_trade(trade)

    total_volume = volume_tracker.get_session_volume()
    assert total_volume == 300.0  # 3 trades * 1.0 amount * 100.0 price

def test_get_trade_count(volume_tracker):
    """Test trade count calculation"""
    # Add test trades
    trades = [
        TradeRecord(
            timestamp=datetime.now().timestamp(),
            wallet_address="wallet1",
            token_address="token1",
            side="buy",
            amount=1.0,
            price=100.0
        ),
        TradeRecord(
            timestamp=datetime.now().timestamp(),
            wallet_address="wallet2",
            token_address="token1",
            side="sell",
            amount=1.0,
            price=100.0
        )
    ]

    for trade in trades:
        volume_tracker.record_trade(trade)

    counts = volume_tracker.get_trade_count()
    assert counts['buy'] == 1
    assert counts['sell'] == 1

def test_get_wallet_performance(volume_tracker):
    """Test wallet performance analysis"""
    # Add test trades for multiple wallets
    trades = [
        TradeRecord(
            timestamp=datetime.now().timestamp(),
            wallet_address="wallet1",
            token_address="token1",
            side="buy",
            amount=1.0,
            price=100.0
        ),
        TradeRecord(
            timestamp=datetime.now().timestamp(),
            wallet_address="wallet1",
            token_address="token1",
            side="sell",
            amount=2.0,
            price=100.0
        )
    ]

    for trade in trades:
        volume_tracker.record_trade(trade)

    stats = volume_tracker.get_wallet_performance()
    wallet1_stats = stats['wallet1']

    assert wallet1_stats['volume'] == 300.0  # (1.0 + 2.0) * 100.0
    assert wallet1_stats['trade_count'] == 2
    assert wallet1_stats['buys'] == 1
    assert wallet1_stats['sells'] == 1

def test_generate_report(volume_tracker):
    """Test report generation"""
    # Start session
    volume_tracker.start_session(target_volume=1000.0, duration_hours=1)

    # Add test trades
    trade = TradeRecord(
        timestamp=datetime.now().timestamp(),
        wallet_address="wallet1",
        token_address="token1",
        side="buy",
        amount=1.0,
        price=100.0
    )
    volume_tracker.record_trade(trade)

    report = volume_tracker.generate_report()

    assert report['total_volume'] == 100.0
    assert report['target_volume'] == 1000.0
    assert report['progress'] == 10.0  # (100.0 / 1000.0 * 100)
    assert report['trade_counts']['buy'] == 1
    assert report['trade_counts']['sell'] == 0
