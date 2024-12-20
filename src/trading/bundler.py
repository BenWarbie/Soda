from typing import List, Optional
from solders.rpc.types import TxOpts
from solders.transaction import Transaction
from solders.keypair import Keypair
from ..wallet.wallet_manager import WalletManager
from .dex_interface import RaydiumDEX
import logging

logger = logging.getLogger(__name__)

class JitoBundler:
    def __init__(self, wallet_manager: WalletManager, dex: RaydiumDEX):
        self.wallet_manager = wallet_manager
        self.dex = dex
        self.bundle_size_limit = 4  # From solana-raydium-volume-bot

    async def create_bundle(self, transactions: List[Transaction]) -> Optional[str]:
        """Creates a JITO bundle from multiple transactions"""
        try:
            tx_chunks = [transactions[i:i+3] for i in range(0, len(transactions), 3)]
            for chunk in tx_chunks:
                bundle_result = await self._build_bundle(chunk)
                if bundle_result:
                    return bundle_result
            return None
        except Exception as e:
            logger.error(f"Bundle creation failed: {e}")
            return None

    async def _build_bundle(self, transactions: List[Transaction]) -> Optional[str]:
        """Internal method to build and submit a JITO bundle"""
        try:
            if len(transactions) > self.bundle_size_limit:
                logger.warning(f"Transaction chunk size {len(transactions)} exceeds bundle limit {self.bundle_size_limit}")
                return None

            bundle = await self.dex.create_jito_bundle(transactions)
            if not bundle:
                return None

            result = await self.dex.submit_jito_bundle(bundle, timeout_seconds=30)
            return result
        except Exception as e:
            logger.error(f"Bundle building failed: {e}")
            return None

    async def split_purchase(self, token_address: str, total_amount: float, num_wallets: int = 21):
        """Splits a token purchase across multiple wallets using JITO bundles"""
        try:
            # Create wallet group
            wallets = await self.wallet_manager.create_wallet_group(num_wallets)

            # Calculate amount per wallet
            amount_per_wallet = total_amount / num_wallets

            # Create swap transactions
            transactions = []
            for wallet in wallets:
                tx = await self.dex.create_swap_transaction(
                    wallet,
                    token_address,
                    amount_per_wallet
                )
                if tx:  # Only add valid transactions
                    transactions.append(tx)

            if not transactions:
                logger.error("No valid transactions created for split purchase")
                return None

            # Bundle and execute transactions
            return await self.create_bundle(transactions)
        except Exception as e:
            logger.error(f"Split purchase failed: {e}")
            return None

    async def incremental_sell(self, token_address: str, sell_percentage: float, interval_seconds: int):
        """Incrementally sells token positions from multiple wallets"""
        try:
            # Get all wallets holding the token
            wallets = await self.wallet_manager.get_token_holders(token_address)

            if not wallets:
                logger.warning(f"No wallets found holding token {token_address}")
                return None

            # Calculate sell amounts for each wallet
            sell_transactions = []
            for wallet in wallets:
                balance = await self.dex.get_token_balance(wallet, token_address)
                sell_amount = balance * sell_percentage

                if sell_amount > 0:
                    tx = await self.dex.create_sell_transaction(
                        wallet,
                        token_address,
                        sell_amount
                    )
                    if tx:  # Only add valid transactions
                        sell_transactions.append(tx)

            if not sell_transactions:
                logger.error("No valid sell transactions created")
                return None

            # Bundle and execute sell transactions
            return await self.create_bundle(sell_transactions)
        except Exception as e:
            logger.error(f"Incremental sell failed: {e}")
            return None
