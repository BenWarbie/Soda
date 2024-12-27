from typing import List, Optional
from solders.rpc.types import TxOpts
from solders.transaction import Transaction
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from jito_bundler import Bundle, SearcherClient
from wallet.wallet_manager import WalletManager
from trading.dex_interface import RaydiumDEX
import logging
import random

logger = logging.getLogger(__name__)

JITO_FEE = 10000  # Fee in lamports (0.00001 SOL)

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

            # Create bundle and get recent blockhash
            bundle = Bundle([], self.bundle_size_limit)
            recent_blockhash = await self.dex.connection.get_recent_blockhash()

            # Add transactions to bundle
            for tx in transactions:
                bundle.add_transaction(tx)

            # Get tip accounts and select one randomly
            tip_accounts = await self.dex.connection.get_tip_accounts()
            tip_account = tip_accounts[min(int(random.random() * len(tip_accounts)), 3)]

            # Add tip transaction
            bundle.add_tip_tx(
                self.wallet_manager.get_fee_payer(),
                JITO_FEE,
                Pubkey.from_string(tip_account),
                recent_blockhash['result']['value']['blockhash']
            )

            # Submit bundle
            result = await self.dex.connection.send_bundle(
                bundle,
                opts={'skipPreflight': True}
            )
            return result['result']

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
