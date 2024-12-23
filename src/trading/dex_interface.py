"""
DEX interface for Solana trading bot.
Handles interactions with Raydium DEX for trading operations.
"""
from typing import Dict, Optional, Tuple
import logging
import asyncio
import random
import time
from solders.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.system_program import TransferParams
from solders.pubkey import Pubkey
from solders.rpc.commitment import Confirmed
from ..analytics.volume_tracker import TradeRecord

logger = logging.getLogger(__name__)

class RaydiumDEX:
    """Interface for Raydium DEX operations"""

    def __init__(self, config: Dict):
        """
        Initialize Raydium DEX interface

        Args:
            config: Configuration dictionary containing:
                - rpc_url: Solana RPC endpoint
                - program_id: Raydium program ID
                - amm_id: AMM program ID
                - pool_id: Trading pool ID
                - max_retries: Maximum retry attempts
        """
        self.config = config
        self.rpc_client = AsyncClient(
            config['rpc_url'],
            commitment=config.get('commitment', Confirmed)
        )
        self.program_id = Pubkey(config['program_id'])
        self.amm_id = Pubkey(config['amm_id'])
        self.pool_id = Pubkey(config['pool_id'])
        self.max_retries = config.get('max_retries', 3)

    async def _retry_operation(self, operation_func, *args, **kwargs):
        """Retry failed operations with exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                return await operation_func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Operation failed after {self.max_retries} attempts: {str(e)}")
                    raise
                wait_time = 2 ** attempt
                logger.warning(f"Operation attempt {attempt + 1} failed, retrying in {wait_time}s")
                await asyncio.sleep(wait_time)

    async def get_pool_info(self) -> Dict:
        """Get current pool information"""
        try:
            pool_info = await self._retry_operation(
                self.rpc_client.get_account_info,
                self.pool_id
            )
            return pool_info["result"]["value"]
        except Exception as e:
            logger.error(f"Error getting pool info: {str(e)}")
            raise

    async def create_swap_instruction(
        self,
        wallet: Keypair,
        amount: float,
        is_buy: bool,
        slippage: float = 0.5
    ) -> Tuple[Transaction, float]:
        """
        Create a swap instruction for Raydium AMM

        Args:
            wallet: Wallet keypair for the transaction
            amount: Amount to swap (in SOL for buys, tokens for sells)
            is_buy: True for buy, False for sell
            slippage: Maximum acceptable slippage percentage

        Returns:
            Tuple of (Transaction, expected_output_amount)
        """
        try:
            # Get pool state and calculate amounts
            pool_info = await self.get_pool_info()

            # Create transaction instruction
            recent_blockhash = await self.rpc_client.get_recent_blockhash()
            transaction = Transaction()
            transaction.recent_blockhash = recent_blockhash["result"]["value"]["blockhash"]

            # Add Raydium swap instruction
            # Note: Actual implementation will use Raydium SDK
            # This is a placeholder for the swap instruction
            expected_output = amount * (1 - slippage/100)

            return transaction, expected_output

        except Exception as e:
            logger.error(f"Error creating swap instruction: {str(e)}")
            raise

    async def execute_swap(
        self,
        wallet: Keypair,
        amount: float,
        is_buy: bool,
        slippage: float = 0.5,
        volume_tracker = None
    ) -> str:
        """
        Execute a swap on Raydium

        Args:
            wallet: Wallet keypair for the transaction
            amount: Amount to swap
            is_buy: True for buy, False for sell
            slippage: Maximum acceptable slippage percentage
            volume_tracker: Optional VolumeTracker instance for analytics

        Returns:
            Transaction signature
        """
        try:
            # Get pre-trade price
            pre_price = await self.get_market_price()

            # Create and execute swap transaction
            transaction, expected_output = await self.create_swap_instruction(
                wallet, amount, is_buy, slippage
            )

            # Sign and send transaction
            transaction.sign(wallet)
            signature = await self._retry_operation(
                self.rpc_client.send_transaction,
                transaction,
                wallet
            )

            # Wait for confirmation
            await self.rpc_client.confirm_transaction(signature["result"])

            # Get post-trade price and calculate metrics
            post_price = await self.get_market_price()

            # Track analytics if volume tracker provided
            if volume_tracker:
                # Calculate price impact
                price_impact = volume_tracker.track_price_impact(
                    str(self.pool_id),
                    pre_price,
                    post_price
                )

                # Calculate profit/loss for sell trades
                profit_loss = (post_price - pre_price) * amount if not is_buy else 0

                # Record trade
                volume_tracker.record_trade(TradeRecord(
                    timestamp=time.time(),
                    wallet_address=str(wallet.public_key),
                    token_address=str(self.pool_id),
                    side='buy' if is_buy else 'sell',
                    amount=amount,
                    price=post_price,
                    profit_loss=profit_loss,
                    price_impact=price_impact
                ))

            logger.info(
                f"Successfully executed {'buy' if is_buy else 'sell'} swap "
                f"of {amount} with expected output {expected_output}"
            )
            return signature["result"]

        except Exception as e:
            logger.error(f"Error executing swap: {str(e)}")
            raise

    async def get_market_price(self) -> float:
        """Get current market price from the pool with reserves calculation"""
        try:
            pool_info = await self.get_pool_info()
            token_a_amount = float(pool_info['data']['tokenAAmount'])
            token_b_amount = float(pool_info['data']['tokenBAmount'])

            if token_a_amount == 0:
                raise ValueError("Token A reserve is zero")

            # Calculate price from reserves
            price = token_b_amount / token_a_amount
            logger.debug(f"Calculated price {price} from reserves A:{token_a_amount} B:{token_b_amount}")
            return float(price)

        except Exception as e:
            logger.error(f"Error getting market price: {str(e)}")
            raise

    async def calculate_price_impact(self, token_address: str, amount: float) -> float:
        """
        Calculate the price impact of a trade.

        Args:
            token_address: Address of the token
            amount: Amount to trade

        Returns:
            Price impact as a decimal (e.g., 0.02 for 2% impact)
        """
        try:
            pool_info = await self.get_pool_info()
            token_a_reserve = float(pool_info['data']['tokenAAmount'])
            token_b_reserve = float(pool_info['data']['tokenBAmount'])

            # Calculate price impact using constant product formula
            # Impact = |1 - (x * y)/(x + Δx)(y - Δy)|
            impact = abs(1 - (token_a_reserve * token_b_reserve) /
                        ((token_a_reserve + amount) * (token_b_reserve - (amount * token_b_reserve/token_a_reserve))))

            logger.debug(f"Calculated price impact {impact} for amount {amount}")
            return float(impact)

        except Exception as e:
            logger.error(f"Error calculating price impact: {str(e)}")
            raise
