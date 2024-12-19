"""
DEX interface for Solana trading bot.
Handles interactions with Raydium DEX for trading operations.
"""
from typing import Dict, Optional, Tuple
import logging
import asyncio
import random
from solana.rpc.async_api import AsyncClient
from solana.keypair import Keypair
from solana.transaction import Transaction
from solana.system_program import TransferParams
from solana.publickey import PublicKey
from solana.rpc.commitment import Confirmed

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
        self.program_id = PublicKey(config['program_id'])
        self.amm_id = PublicKey(config['amm_id'])
        self.pool_id = PublicKey(config['pool_id'])
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
        slippage: float = 0.5
    ) -> str:
        """
        Execute a swap on Raydium

        Args:
            wallet: Wallet keypair for the transaction
            amount: Amount to swap
            is_buy: True for buy, False for sell
            slippage: Maximum acceptable slippage percentage

        Returns:
            Transaction signature
        """
        try:
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

            logger.info(
                f"Successfully executed {'buy' if is_buy else 'sell'} swap "
                f"of {amount} with expected output {expected_output}"
            )
            return signature["result"]

        except Exception as e:
            logger.error(f"Error executing swap: {str(e)}")
            raise

    async def get_market_price(self) -> float:
        """Get current market price from the pool"""
        try:
            pool_info = await self.get_pool_info()
            # Note: Actual implementation will calculate price from pool reserves
            # This is a placeholder for price calculation
            return 1.0

        except Exception as e:
            logger.error(f"Error getting market price: {str(e)}")
            raise
