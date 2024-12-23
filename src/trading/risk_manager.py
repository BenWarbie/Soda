"""
Risk management module for the Soda trading bot.
Implements position monitoring and stop-loss automation.
"""
from typing import List, Dict, Optional
from decimal import Decimal
import asyncio
import logging
from datetime import datetime
from .dex_interface import RaydiumDEX
from ..wallet.wallet_manager import WalletManager
from .trade_executor import TradeExecutor

logger = logging.getLogger(__name__)

class Position:
    """Represents a trading position with risk management parameters."""
    def __init__(
        self,
        token_address: str,
        entry_price: Decimal,
        amount: Decimal,
        wallet_address: str,
        stop_loss_threshold: Decimal = Decimal('0.95'),  # 5% loss by default
        trailing_stop: bool = False,
        trailing_distance: Decimal = Decimal('0.02')  # 2% trailing distance
    ):
        self.token_address = token_address
        self.entry_price = entry_price
        self.amount = amount
        self.wallet_address = wallet_address
        self.stop_loss_threshold = stop_loss_threshold
        self.trailing_stop = trailing_stop
        self.trailing_distance = trailing_distance
        self.highest_price = entry_price
        self.stop_loss_price = entry_price * stop_loss_threshold

class RiskManager:
    """Manages trading risk through position monitoring and stop-loss automation."""

    def __init__(
        self,
        trade_executor: TradeExecutor,
        dex: RaydiumDEX,
        wallet_manager: WalletManager,
        config: Dict
    ):
        """
        Initialize risk manager.

        Args:
            trade_executor: TradeExecutor instance
            dex: RaydiumDEX instance
            wallet_manager: WalletManager instance
            config: Configuration dictionary
        """
        self.trade_executor = trade_executor
        self.dex = dex
        self.wallet_manager = wallet_manager
        self.config = config
        self.positions: Dict[str, Position] = {}
        self.monitoring = False
        self.monitor_interval = config.get('monitor_interval', 1.0)  # seconds

    def add_position(
        self,
        token_address: str,
        entry_price: Decimal,
        amount: Decimal,
        wallet_address: str,
        stop_loss_threshold: Optional[Decimal] = None,
        trailing_stop: bool = False,
        trailing_distance: Optional[Decimal] = None
    ) -> Position:
        """
        Add a new position to monitor.

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
        position = Position(
            token_address=token_address,
            entry_price=entry_price,
            amount=amount,
            wallet_address=wallet_address,
            stop_loss_threshold=stop_loss_threshold or Decimal('0.95'),
            trailing_stop=trailing_stop,
            trailing_distance=trailing_distance or Decimal('0.02')
        )
        position_key = f"{wallet_address}:{token_address}"
        self.positions[position_key] = position
        return position

    def remove_position(self, wallet_address: str, token_address: str):
        """Remove a position from monitoring."""
        position_key = f"{wallet_address}:{token_address}"
        self.positions.pop(position_key, None)

    async def start_monitoring(self):
        """Start monitoring all positions."""
        self.monitoring = True
        while self.monitoring:
            try:
                await self._check_positions()
                await asyncio.sleep(self.monitor_interval)
            except Exception as e:
                logger.error(f"Error monitoring positions: {str(e)}")
                await asyncio.sleep(self.monitor_interval * 2)  # Back off on error

    async def stop_monitoring(self):
        """Stop monitoring positions."""
        self.monitoring = False

    async def _check_positions(self):
        """Enhanced position monitoring with price impact tracking"""
        for position in self.positions.values():
            try:
                current_price = await self.dex.get_market_price()
                price_impact = await self.dex.calculate_price_impact(
                    position.token_address,
                    float(position.amount)
                )

                # Update trailing stop with price impact consideration
                if position.trailing_stop and current_price > position.highest_price:
                    position.highest_price = current_price
                    # Adjust stop loss based on price impact
                    impact_adjusted_distance = position.trailing_distance + (Decimal(str(price_impact)) * 2)
                    position.stop_loss_price = current_price * (
                        Decimal('1') - impact_adjusted_distance
                    )

                # Check if stop-loss is triggered
                if current_price <= position.stop_loss_price:
                    await self._execute_stop_loss(position, current_price)

            except Exception as e:
                logger.error(
                    f"Error checking position {position.token_address}: {str(e)}"
                )


    async def _execute_stop_loss(self, position: Position, current_price: Decimal):
        """
        Execute stop-loss for a position.

        Args:
            position: Position to execute stop-loss for
            current_price: Current price that triggered stop-loss
        """
        try:
            logger.info(
                f"Executing stop-loss for {position.token_address} at "
                f"price {current_price}"
            )

            # Execute emergency sell with higher slippage tolerance
            trade_params = {
                'token_address': position.token_address,
                'amount': float(position.amount),
                'is_buy': False,
                'slippage': 1.0  # Higher slippage tolerance for emergency
            }

            # Use protected trade execution
            await self.trade_executor.execute_protected_trade(trade_params)

            # Remove position from monitoring
            self.remove_position(position.wallet_address, position.token_address)

            logger.info(
                f"Stop-loss executed for {position.token_address}. "
                f"Entry: {position.entry_price}, Exit: {current_price}"
            )

        except Exception as e:
            logger.error(
                f"Failed to execute stop-loss for {position.token_address}: {str(e)}"
            )
