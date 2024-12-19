"""
Configuration management for Solana trading bot.
Handles trading modes, wallet configurations, and system parameters.
"""
import os
import logging
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TradingMode(Enum):
    SAFE = "SAFE"
    NORMAL = "NORMAL"
    AGGRESSIVE = "AGGRESSIVE"
    HIGH_FREQUENCY = "HIGH_FREQUENCY"

@dataclass
class TradingModeConfig:
    max_wallets: int
    interval: int  # seconds
    min_amount: float
    max_amount: float
    slippage: float
    price_impact: float

class Config:
    def __init__(self):
        """Initialize configuration with default values"""
        self.trading_modes = {
            TradingMode.SAFE: TradingModeConfig(
                max_wallets=5,
                interval=30,
                min_amount=0.1,
                max_amount=0.5,
                slippage=0.5,
                price_impact=0.01
            ),
            TradingMode.NORMAL: TradingModeConfig(
                max_wallets=10,
                interval=15,
                min_amount=0.2,
                max_amount=1.0,
                slippage=1.0,
                price_impact=0.02
            ),
            TradingMode.AGGRESSIVE: TradingModeConfig(
                max_wallets=20,
                interval=5,
                min_amount=0.5,
                max_amount=2.0,
                slippage=2.0,
                price_impact=0.05
            ),
            TradingMode.HIGH_FREQUENCY: TradingModeConfig(
                max_wallets=40,
                interval=1,
                min_amount=0.1,
                max_amount=0.5,
                slippage=2.0,
                price_impact=0.03
            )
        }

        # High-frequency trading configuration
        self.high_frequency = {
            'enabled': False,
            'trades_per_minute': 300,
            'burst_duration': 30,  # seconds
            'batch_size': 10
        }

        # Session configuration
        self.session = {
            'duration': int(os.getenv('SESSION_DURATION', '60')),  # minutes
            'target_volume': float(os.getenv('TARGET_VOLUME', '0')),
            'wallet_group_size': int(os.getenv('WALLET_GROUP_SIZE', '10'))
        }

        # DEX configuration
        self.dex = {
            'default_slippage': float(os.getenv('DEFAULT_SLIPPAGE', '1.0')),
            'max_retries': int(os.getenv('MAX_RETRIES', '3')),
            'retry_delay': int(os.getenv('RETRY_DELAY', '1'))
        }

        # Load environment-specific configurations
        self._load_env_config()

    def _load_env_config(self):
        """Load configuration from environment variables"""
        try:
            # Trading mode
            mode_str = os.getenv('TRADING_MODE', 'SAFE')
            self.current_mode = TradingMode(mode_str)

            # High-frequency trading settings
            self.high_frequency['enabled'] = os.getenv('HF_TRADING_ENABLED', '').lower() == 'true'
            if self.high_frequency['enabled']:
                self.high_frequency.update({
                    'trades_per_minute': int(os.getenv('HF_TRADES_PER_MINUTE', '300')),
                    'burst_duration': int(os.getenv('HF_BURST_DURATION', '30')),
                    'batch_size': int(os.getenv('HF_BATCH_SIZE', '10'))
                })

        except ValueError as e:
            logger.error(f"Configuration error: {str(e)}")
            # Fall back to SAFE mode
            self.current_mode = TradingMode.SAFE

    def get_mode_config(self) -> TradingModeConfig:
        """Get configuration for current trading mode"""
        return self.trading_modes[self.current_mode]

    def update_mode(self, mode: str):
        """Update trading mode"""
        try:
            self.current_mode = TradingMode(mode)
            logger.info(f"Trading mode updated to: {mode}")
        except ValueError:
            logger.error(f"Invalid trading mode: {mode}")
            raise ValueError(f"Invalid trading mode: {mode}")

    def to_dict(self) -> Dict:
        """Convert configuration to dictionary"""
        return {
            'trading_mode': self.current_mode.value,
            'mode_config': {
                'max_wallets': self.get_mode_config().max_wallets,
                'interval': self.get_mode_config().interval,
                'min_amount': self.get_mode_config().min_amount,
                'max_amount': self.get_mode_config().max_amount,
                'slippage': self.get_mode_config().slippage,
                'price_impact': self.get_mode_config().price_impact
            },
            'high_frequency': self.high_frequency,
            'session': self.session,
            'dex': self.dex
        }
