"""
Trade execution system for coordinating trades across multiple wallets.
Implements high-frequency trading and volume-based patterns.
"""
from typing import List, Dict, Optional
from enum import Enum
import os
import time
import asyncio
import random
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from ..wallet.wallet_manager import WalletManager
from .dex_interface import RaydiumDEX
from .trading_patterns import TradingPattern
from ..analytics.volume_tracker import VolumeTracker, TradeRecord
from .bundler import JitoBundler
from .mev_protection import MEVProtection
from .risk_manager import RiskManager, Position

logger = logging.getLogger(__name__)

class TradingMode(Enum):
    SAFE = "SAFE"
    NORMAL = "NORMAL"
    AGGRESSIVE = "AGGRESSIVE"
    HIGH_FREQUENCY = "HIGH_FREQUENCY"

class TradeExecutor:
    def __init__(self, wallet_manager: WalletManager, dex: RaydiumDEX, config: Dict):
        """
        Initialize trade executor with configuration

        Args:
            wallet_manager: WalletManager instance
            dex: RaydiumDEX instance
            config: Configuration dictionary containing trading parameters
        """
        self.wallet_manager = wallet_manager
        self.dex = dex
        self.config = config
        self.mode = TradingMode(os.getenv("TRADING_MODE", "SAFE"))
        self.active_trades: Dict[str, Dict] = {}
        self.volume_tracker = VolumeTracker()
        self.bundler = JitoBundler(wallet_manager, dex)
        self.mev_protection = MEVProtection(self.bundler)
        self.risk_manager = RiskManager(self, dex, wallet_manager, config)
        self.trading_pattern = TradingPattern(
            wallet_manager=wallet_manager,
            dex=dex,
            config=config
        )

        # Trading parameters
        self.wallet_group_size = config.get('wallet_group_size', 10)
        self.session_duration = config.get('session_duration', 60)  # minutes
        self.trading_interval = config.get('trading_interval', 5)  # seconds
        self.high_frequency = config.get('high_frequency', {
            'enabled': False,
            'trades_per_minute': 300,
            'burst_duration': 30  # seconds
        })

    async def execute_trading_round(self):
        """Execute complete trading round with new wallet group"""
        try:
            logger.info("Starting new trading round")
            wallet_group = await self.wallet_manager.create_wallet_group(
                self.wallet_group_size
            )

            # Distribute initial SOL
            initial_amount = random.uniform(
                self.config.get('min_amount', 0.1),
                self.config.get('max_amount', 1.0)
            )
            await self.wallet_manager.distribute_sol(wallet_group, initial_amount)

            # Execute trading patterns
            start_time = datetime.now()
            end_time = start_time + timedelta(minutes=self.session_duration)

            while datetime.now() < end_time:
                # Randomly select and execute trading pattern
                pattern = random.choice(['pump', 'milkshake'])

                if pattern == 'pump':
                    await self.trading_pattern.execute_pump_pattern(wallet_group)
                else:
                    await self.trading_pattern.execute_milkshake_pattern(wallet_group)

                # Add random delay between patterns
                delay = random.uniform(
                    self.trading_interval * 0.5,
                    self.trading_interval * 1.5
                )
                await asyncio.sleep(delay)

            # Recall SOL from wallets
            total_recalled = await self.wallet_manager.recall_sol(wallet_group)
            logger.info(f"Trading round completed. Total SOL recalled: {total_recalled}")

        except Exception as e:
            logger.error(f"Error executing trading round: {str(e)}")
            raise

    async def execute_high_frequency_round(self):
        """Execute high-frequency trading round"""
        try:
            if not self.high_frequency['enabled']:
                logger.warning("High-frequency trading is not enabled")
                return

            logger.info("Starting high-frequency trading round")

            # Create larger wallet group for high-frequency trading
            wallet_group = await self.wallet_manager.create_wallet_group(
                self.wallet_group_size * 2
            )

            # Distribute initial SOL
            initial_amount = self.config.get('min_amount', 0.1)
            await self.wallet_manager.distribute_sol(wallet_group, initial_amount)

            # Calculate delays for target trades per minute
            delay = 60 / self.high_frequency['trades_per_minute']
            burst_end = datetime.now() + timedelta(
                seconds=self.high_frequency['burst_duration']
            )

            # Execute rapid trades
            while datetime.now() < burst_end:
                # Execute trades in parallel for higher throughput
                tasks = []
                for _ in range(min(10, len(wallet_group))):  # Process in batches of 10
                    wallet_key = random.choice(wallet_group)
                    is_buy = random.random() < 0.67  # Maintain 2:1 ratio

                    if is_buy:
                        tasks.append(
                            self.trading_pattern.execute_pump_pattern([wallet_key])
                        )
                    else:
                        tasks.append(
                            self.trading_pattern.execute_milkshake_pattern([wallet_key])
                        )

                # Wait for batch completion
                await asyncio.gather(*tasks)
                await asyncio.sleep(delay)

            # Recall SOL from wallets
            total_recalled = await self.wallet_manager.recall_sol(wallet_group)
            logger.info(
                f"High-frequency trading round completed. "
                f"Total SOL recalled: {total_recalled}"
            )

        except Exception as e:
            logger.error(f"Error executing high-frequency round: {str(e)}")
            raise

    async def start_trading_session(self):
        """Start a complete trading session"""
        try:
            logger.info("Starting trading session")
            session_start = datetime.now()
            session_end = session_start + timedelta(minutes=self.session_duration)

            while datetime.now() < session_end:
                if random.random() < 0.2 and self.high_frequency['enabled']:  # 20% chance
                    await self.execute_high_frequency_round()
                else:
                    await self.execute_trading_round()

                # Add random delay between rounds
                delay = random.uniform(
                    self.trading_interval * 2,
                    self.trading_interval * 4
                )
                await asyncio.sleep(delay)

            logger.info("Trading session completed")

        except Exception as e:
            logger.error(f"Error in trading session: {str(e)}")
            raise

    async def get_session_report(self) -> Dict:
        """Gets the current session's analytics report"""
        return self.volume_tracker.generate_report()

    async def export_session_data(self, filename: str):
        """Exports session data to JSON file"""
        self.volume_tracker.export_session_data(filename)

    async def execute_bundled_purchase(self, token_address: str, total_amount: float):
        """Execute a bundled token purchase split across multiple wallets"""
        return await self.bundler.split_purchase(token_address, total_amount)

    async def execute_incremental_sell(self, token_address: str, sell_percentage: float = 0.1):
        """Execute an incremental sell operation across multiple wallets"""
        return await self.bundler.incremental_sell(token_address, sell_percentage, 60)

    async def execute_protected_trade(self, trade_params: Dict) -> str:
        """
        Execute a trade with MEV protection using JITO bundles.

        Args:
            trade_params: Dictionary containing trade parameters:
                - token_address: Address of token to trade
                - amount: Amount to trade
                - is_buy: True for buy, False for sell
                - slippage: Maximum acceptable slippage

        Returns:
            Transaction signature
        """
        try:
            # Create swap instruction
            swap_tx = await self.dex.create_swap_instruction(
                self.wallet_manager.get_active_wallet(),
                trade_params['amount'],
                trade_params['is_buy'],
                trade_params.get('slippage', 0.5)
            )

            # Create protected bundle
            protected_bundle = self.mev_protection.create_protected_bundle(
                swap_tx,
                self.wallet_manager.get_wallet_group()
            )

            # Execute bundle through JITO
            return await self.bundler.send_bundle(protected_bundle)

        except Exception as e:
            logger.error(f"Error executing protected trade: {str(e)}")
            raise

    async def start_position_monitoring(self):
        """Start monitoring positions for stop-loss conditions."""
        await self.risk_manager.start_monitoring()

    async def stop_position_monitoring(self):
        """Stop monitoring positions."""
        await self.risk_manager.stop_monitoring()

    async def add_monitored_position(
        self,
        token_address: str,
        entry_price: float,
        amount: float,
        wallet_address: str,
        stop_loss_threshold: Optional[float] = None,
        trailing_stop: bool = False,
        trailing_distance: Optional[float] = None
    ) -> Position:
        """
        Add a position to be monitored for stop-loss.

        Args:
            token_address: Address of the token
            entry_price: Entry price of the position
            amount: Position size
            wallet_address: Address of the wallet holding the position
            stop_loss_threshold: Optional custom stop-loss threshold
            trailing_stop: Whether to use trailing stop
            trailing_distance: Distance for trailing stop

        Returns:
            Created Position instance
        """
        return self.risk_manager.add_position(
            token_address=token_address,
            entry_price=Decimal(str(entry_price)),
            amount=Decimal(str(amount)),
            wallet_address=wallet_address,
            stop_loss_threshold=(
                Decimal(str(stop_loss_threshold)) if stop_loss_threshold else None
            ),
            trailing_stop=trailing_stop,
            trailing_distance=(
                Decimal(str(trailing_distance)) if trailing_distance else None
            )
        )

    async def remove_monitored_position(
        self,
        wallet_address: str,
        token_address: str
    ):
        """
        Remove a position from stop-loss monitoring.

        Args:
            wallet_address: Address of the wallet
            token_address: Address of the token
        """
        self.risk_manager.remove_position(wallet_address, token_address)
