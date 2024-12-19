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
from ..wallet.wallet_manager import WalletManager
from .dex_interface import RaydiumDEX
from .trading_patterns import TradingPattern
from ..analytics.volume_tracker import VolumeTracker, TradeRecord

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
