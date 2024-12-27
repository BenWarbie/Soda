"""
Wallet management system for Solana trading bot.
Handles creation, coordination, and management of multiple trading wallets.
Includes anti-detection mechanisms and comprehensive error handling.
"""
from typing import Dict, List, Optional, Tuple
import os
import logging
import asyncio
import random
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solders.system_program import transfer, TransferParams
from solana.publickey import PublicKey
from solana.keypair import Keypair
# Type hints
from solana.publickey import PublicKey as PubkeyType
from solana.keypair import Keypair as KeypairType
from solana.transaction import Transaction as TransactionType
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class WalletManager:
    def __init__(self):
        """Initialize wallet manager with configuration from environment"""
        self.rpc_client: AsyncClient = AsyncClient(
            os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com"),
            commitment='confirmed'
        )
        self.main_wallet_key: str = os.getenv("MAIN_WALLET_PRIVATE_KEY")
        self.max_wallets: int = int(os.getenv("MAX_WALLETS", "10"))
        self.min_sol_per_wallet: float = float(os.getenv("MIN_SOL_PER_WALLET", "0.1"))
        self.max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
        self.delay_range: Tuple[int, int] = (
            int(os.getenv("MIN_DELAY", "2")),
            int(os.getenv("MAX_DELAY", "5"))
        )

        # Track wallets by round
        self.current_round: int = 0
        self.wallets: Dict[int, List[Tuple[KeypairType, str]]] = {}
        self.trading_wallets: Dict[str, KeypairType] = {}

    async def _random_delay(self):
        """Add random delay between operations for anti-detection"""
        delay = random.uniform(self.delay_range[0], self.delay_range[1])
        await asyncio.sleep(delay)

    async def _retry_transaction(
        self,
        transaction: TransactionType,
        signer: KeypairType,
        max_retries: int = None
    ) -> bool:
        """Retry a transaction with exponential backoff"""
        retries = max_retries or self.max_retries
        for attempt in range(retries):
            try:
                await self.rpc_client.send_transaction(transaction, signer)
                return True
            except Exception as e:
                if attempt == retries - 1:
                    logging.error(f"Transaction failed after {retries} attempts: {str(e)}")
                    return False
                await asyncio.sleep(2 ** attempt)

    async def create_trading_wallet(self) -> Tuple[KeypairType, str]:
        """Create a new trading wallet"""
        try:
            keypair = Keypair()
            public_key = str(keypair.pubkey())
            self.trading_wallets[public_key] = keypair
            return keypair, public_key
        except Exception as e:
            logging.error(f"Error creating trading wallet: {str(e)}")
            raise

    async def create_wallet_group(
        self,
        size: int
    ) -> List[Tuple[KeypairType, str]]:
        """Create a group of trading wallets for coordinated trading"""
        try:
            if size > self.max_wallets:
                raise ValueError(f"Requested wallet group size {size} exceeds maximum {self.max_wallets}")

            wallet_group = []
            for _ in range(size):
                await self._random_delay()
                wallet = await self.create_trading_wallet()
                wallet_group.append(wallet)

            self.current_round += 1
            self.wallets[self.current_round] = wallet_group
            return wallet_group
        except Exception as e:
            logging.error(f"Error creating wallet group: {str(e)}")
            raise

    async def distribute_sol(
        self,
        wallet_keys: List[str],
        amount_per_wallet: float
    ) -> bool:
        """Distribute SOL to trading wallets"""
        try:
            if not self.main_wallet_key:
                raise ValueError("Main wallet private key not configured")

            main_wallet = Keypair.from_base58_string(self.main_wallet_key)
            lamports_per_wallet = int(amount_per_wallet * 1e9)

            for wallet_key in wallet_keys:
                await self._random_delay()

                # Create transfer instruction
                transfer_ix = transfer(
                    TransferParams(
                        from_pubkey=main_wallet.pubkey(),
                        to_pubkey=PublicKey(wallet_key),
                        lamports=lamports_per_wallet
                    )
                )

                # Create and sign transaction
                recent_blockhash = await self.rpc_client.get_latest_blockhash()
                transaction = Transaction()
                transaction.add(transfer_ix)
                transaction.recent_blockhash = recent_blockhash.value.blockhash
                transaction.sign(main_wallet)

                # Send transaction with retry
                if not await self._retry_transaction(transaction, main_wallet):
                    return False

            return True
        except Exception as e:
            logging.error(f"Error distributing SOL: {str(e)}")
            return False

    async def recall_sol(
        self,
        wallet_keys: List[str]
    ) -> bool:
        """Recall SOL from trading wallets back to main wallet"""
        try:
            if not self.main_wallet_key:
                raise ValueError("Main wallet private key not configured")

            main_wallet = Keypair.from_base58_string(self.main_wallet_key)
            main_wallet_pubkey = main_wallet.pubkey()

            for wallet_key in wallet_keys:
                await self._random_delay()

                if wallet_key not in self.trading_wallets:
                    logging.warning(f"Wallet {wallet_key} not found in trading wallets")
                    continue

                wallet = self.trading_wallets[wallet_key]
                balance = await self.get_wallet_balance(wallet_key)

                if balance <= 0:
                    continue

                # Leave enough for transaction fees
                lamports = int((balance - 0.001) * 1e9)
                if lamports <= 0:
                    continue

                # Create transfer instruction
                transfer_ix = transfer(
                    TransferParams(
                        from_pubkey=wallet.pubkey(),
                        to_pubkey=main_wallet_pubkey,
                        lamports=lamports
                    )
                )

                # Create and sign transaction
                recent_blockhash = await self.rpc_client.get_latest_blockhash()
                transaction = Transaction()
                transaction.add(transfer_ix)
                transaction.recent_blockhash = recent_blockhash.value.blockhash
                transaction.sign(wallet)

                # Send transaction with retry
                if not await self._retry_transaction(transaction, wallet):
                    return False

            return True
        except Exception as e:
            logging.error(f"Error recalling SOL: {str(e)}")
            return False

    async def get_wallet_balance(
        self,
        public_key: str
    ) -> float:
        """Gets the SOL balance of a wallet"""
        try:
            response = await self.rpc_client.get_balance(public_key)
            if response["result"]["value"] is not None:
                return float(response["result"]["value"]) / 1e9
            return 0.0
        except Exception as e:
            logging.error(f"Error getting wallet balance: {str(e)}")
            raise
