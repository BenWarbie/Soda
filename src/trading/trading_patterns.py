"""
Trading patterns implementation for Solana trading bot.
Implements various trading strategies with anti-detection mechanisms.
"""
from typing import List, Dict, Optional
import asyncio
import logging
import random
from datetime import datetime
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from wallet.wallet_manager import WalletManager
from trading.dex_interface import RaydiumDEX

logger = logging.getLogger(__name__)

class TradingPattern:
    """Implements trading patterns with anti-detection mechanisms"""

    def __init__(self, wallet_manager: WalletManager, dex: RaydiumDEX, config: Dict):
        """
        Initialize trading pattern executor

        Args:
            wallet_manager: WalletManager instance for wallet operations
            dex: RaydiumDEX instance for DEX operations
            config: Configuration dictionary containing:
                - min_amount: Minimum trade amount in SOL
                - max_amount: Maximum trade amount in SOL
                - min_delay: Minimum delay between trades
                - max_delay: Maximum delay between trades
                - buy_ratio: Number of buys per sell (default: 2)
                - slippage: Maximum acceptable slippage percentage
                - price_impact: Price impact percentage for trades
        """
        self.wallet_manager = wallet_manager
        self.dex = dex
        self.config = config
        self.min_amount = config.get('min_amount', 0.1)
        self.max_amount = config.get('max_amount', 1.0)
        self.min_delay = config.get('min_delay', 2)
        self.max_delay = config.get('max_delay', 5)
        self.buy_ratio = config.get('buy_ratio', 2)
        self.slippage = config.get('slippage', 0.5)
        self.price_impact = config.get('price_impact', 0.01)

    async def _random_delay(self):
        """Add random delay between trades for anti-detection"""
        delay = random.uniform(self.min_delay, self.max_delay)
        await asyncio.sleep(delay)

    def _generate_trade_amount(self) -> float:
        """Generate random trade amount within configured range"""
        return random.uniform(self.min_amount, self.max_amount)

    async def execute_pump_pattern(self, wallet_group: List[str]):
        """
        Execute pump pattern with 2:1 buy ratio
        Performs two buys for every sell to maintain buy pressure
        """
        try:
            logger.info(f"Starting pump pattern execution for {len(wallet_group)} wallets")
            base_price = await self.dex.get_market_price()

            for wallet_key in wallet_group:
                wallet = self.wallet_manager.trading_wallets[wallet_key]
                current_price = base_price

                # Execute buy operations (2x)
                for i in range(self.buy_ratio):
                    amount = self._generate_trade_amount()
                    logger.info(f"Executing buy operation {i+1} of {amount} SOL from wallet {wallet_key}")

                    # Execute buy with price tracking
                    await self.dex.execute_swap(
                        wallet=wallet,
                        amount=amount,
                        is_buy=True,
                        slippage=self.slippage,
                        volume_tracker=self.config.get('volume_tracker')
                    )
                    current_price *= (1 + self.price_impact)
                    await self._random_delay()

                # Execute sell operation (1x)
                if random.random() > 0.3:  # 70% chance to execute sell
                    amount = self._generate_trade_amount()
                    logger.info(f"Executing sell operation of {amount} SOL from wallet {wallet_key}")

                    await self.dex.execute_swap(
                        wallet=wallet,
                        amount=amount,
                        is_buy=False,
                        slippage=self.slippage,
                        volume_tracker=self.config.get('volume_tracker')
                    )
                    await self._random_delay()

            logger.info("Completed pump pattern execution")

        except Exception as e:
            logger.error(f"Error executing pump pattern: {str(e)}")
            raise

    async def execute_milkshake_pattern(self, wallet_group: List[str]):
        """
        Execute coordinated buy/sell across wallets
        Implements the MilkShake pattern with randomized amounts and timing
        """
        try:
            logger.info(f"Starting milkshake pattern execution for {len(wallet_group)} wallets")
            base_price = await self.dex.get_market_price()

            # Split wallets into buy and sell groups with 2:1 ratio
            random.shuffle(wallet_group)
            buy_count = int(len(wallet_group) * 0.67)  # 67% buyers for 2:1 ratio
            buy_group = wallet_group[:buy_count]
            sell_group = wallet_group[buy_count:]

            # Prepare all transactions first
            buy_operations = []
            sell_operations = []

            # Create buy operations (higher quantity, smaller amounts)
            for wallet_key in buy_group:
                wallet = self.wallet_manager.trading_wallets[wallet_key]
                amount = self._generate_trade_amount() * 0.8  # Smaller amounts for buys
                logger.info(f"Creating buy operation of {amount} SOL from wallet {wallet_key}")
                buy_operations.append((wallet, amount))
                await self._random_delay()

            # Create sell operations (lower quantity, larger amounts)
            for wallet_key in sell_group:
                wallet = self.wallet_manager.trading_wallets[wallet_key]
                amount = self._generate_trade_amount() * 1.2  # Larger amounts for sells
                logger.info(f"Creating sell operation of {amount} SOL from wallet {wallet_key}")
                sell_operations.append((wallet, amount))
                await self._random_delay()

            # Execute buys first with slight delays
            for wallet, amount in buy_operations:
                await self.dex.execute_swap(
                    wallet=wallet,
                    amount=amount,
                    is_buy=True,
                    slippage=self.slippage,
                    volume_tracker=self.config.get('volume_tracker')
                )
                await self._random_delay()

            # Execute sells after a short pause
            await asyncio.sleep(random.uniform(5, 10))
            for wallet, amount in sell_operations:
                await self.dex.execute_swap(
                    wallet=wallet,
                    amount=amount,
                    is_buy=False,
                    slippage=self.slippage,
                    volume_tracker=self.config.get('volume_tracker')
                )
                await self._random_delay()

            logger.info("Completed milkshake pattern execution")

        except Exception as e:
            logger.error(f"Error executing milkshake pattern: {str(e)}")
            raise

    async def execute_high_frequency_pattern(self, wallet_group: List[str], duration_seconds: int):
        """
        Execute high-frequency trading pattern with improved coordination
        Implements rapid trading with parallel execution and anti-detection mechanisms
        """
        try:
            logger.info(f"Starting high-frequency pattern execution for {len(wallet_group)} wallets")
            start_time = datetime.now()

            # Split wallets into buy/sell groups with 2:1 ratio
            buy_group = wallet_group[:int(len(wallet_group) * 0.67)]  # 67% buyers
            sell_group = wallet_group[int(len(wallet_group) * 0.67):]  # 33% sellers

            while (datetime.now() - start_time).seconds < duration_seconds:
                # Execute parallel trades with coordination
                buy_tasks = []
                sell_tasks = []

                # Prepare buy operations (smaller amounts)
                for wallet_key in buy_group:
                    amount = self._generate_trade_amount() * 0.8  # Smaller amounts for buys
                    buy_tasks.append(self.dex.execute_swap(
                        wallet=self.wallet_manager.trading_wallets[wallet_key],
                        amount=amount,
                        is_buy=True,
                        slippage=self.slippage,
                        volume_tracker=self.config.get('volume_tracker')
                    ))

                # Prepare sell operations (larger amounts)
                for wallet_key in sell_group:
                    amount = self._generate_trade_amount() * 1.2  # Larger amounts for sells
                    sell_tasks.append(self.dex.execute_swap(
                        wallet=self.wallet_manager.trading_wallets[wallet_key],
                        amount=amount,
                        is_buy=False,
                        slippage=self.slippage,
                        volume_tracker=self.config.get('volume_tracker')
                    ))

                # Execute buys first
                await asyncio.gather(*buy_tasks)
                await asyncio.sleep(0.2)  # 200ms delay between buy/sell waves

                # Execute sells
                await asyncio.gather(*sell_tasks)
                await asyncio.sleep(0.2)  # 200ms delay between rounds

                logger.debug(f"Completed trading round at {datetime.now()}")

            logger.info("Completed high-frequency pattern execution")

        except Exception as e:
            logger.error(f"Error executing high-frequency pattern: {str(e)}")
            raise
