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
from solders.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.system_program import transfer, TransferParams
from solders.pubkey import Pubkey
from solders.rpc.commitment import Confirmed
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class WalletManager:
    def __init__(self):
        """Initialize wallet manager with configuration from environment"""
        self.rpc_client = AsyncClient(
            os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com"),
            commitment=Confirmed
        )
        self.main_wallet_key = os.getenv("MAIN_WALLET_PRIVATE_KEY")
        self.max_wallets = int(os.getenv("MAX_WALLETS", "10"))
        self.min_sol_per_wallet = float(os.getenv("MIN_SOL_PER_WALLET", "0.1"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.delay_range = (
            int(os.getenv("MIN_DELAY", "2")),
            int(os.getenv("MAX_DELAY", "5"))
        )

        # Track wallets by round
        self.current_round = 0
        self.wallets: Dict[int, List[Tuple[Keypair, str]]] = {}
        self.trading_wallets: Dict[str, Keypair] = {}

    async def _random_delay(self):
        """Add random delay between operations for anti-detection"""
        delay = random.uniform(self.delay_range[0], self.delay_range[1])
        await asyncio.sleep(delay)

    async def _retry_transaction(self, transaction_func, *args, **kwargs):
        """Retry failed transactions with exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                return await transaction_func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Transaction failed after {self.max_retries} attempts: {str(e)}")
                    raise
                wait_time = 2 ** attempt
                logger.warning(f"Transaction attempt {attempt + 1} failed, retrying in {wait_time}s")
                await asyncio.sleep(wait_time)

    async def create_trading_wallet(self) -> Tuple[Keypair, str]:
        """Creates a new Solana wallet for trading"""
        try:
            wallet = Keypair()
            public_key = str(wallet.public_key)
            self.trading_wallets[public_key] = wallet
            return wallet, public_key
        except Exception as e:
            logger.error(f"Error creating trading wallet: {str(e)}")
            raise

    async def create_wallet_group(self, size: int) -> List[str]:
        """Creates a group of trading wallets for the current round"""
        try:
            if len(self.trading_wallets) + size > self.max_wallets:
                raise ValueError(f"Cannot create {size} wallets. Would exceed maximum of {self.max_wallets}")

            wallet_group = []
            for _ in range(size):
                wallet, public_key = await self.create_trading_wallet()
                wallet_group.append(public_key)
                await self._random_delay()

            self.wallets[self.current_round] = [(self.trading_wallets[pk], pk) for pk in wallet_group]
            logger.info(f"Created wallet group of size {size} for round {self.current_round}")
            return wallet_group

        except Exception as e:
            logger.error(f"Error creating wallet group: {str(e)}")
            raise

    async def distribute_sol(self, wallet_keys: List[str], amount_per_wallet: float) -> List[str]:
        """Distributes SOL from main wallet to trading wallets"""
        try:
            signatures = []
            main_keypair = Keypair.from_secret_key(bytes.fromhex(self.main_wallet_key))

            for wallet_key in wallet_keys:
                recent_blockhash = await self.rpc_client.get_recent_blockhash()

                transfer_tx = Transaction().add(
                    transfer(
                        TransferParams(
                            from_pubkey=main_keypair.public_key,
                            to_pubkey=Pubkey(wallet_key),
                            lamports=int(amount_per_wallet * 1e9)
                        )
                    )
                )
                transfer_tx.recent_blockhash = recent_blockhash["result"]["value"]["blockhash"]
                transfer_tx.sign(main_keypair)

                # Send transaction with retry mechanism
                signature = await self._retry_transaction(
                    self.rpc_client.send_transaction,
                    transfer_tx,
                    main_keypair
                )
                signatures.append(signature["result"])

                # Add random delay between transfers
                await self._random_delay()

            logger.info(f"Successfully distributed {amount_per_wallet} SOL to {len(wallet_keys)} wallets")
            return signatures

        except Exception as e:
            logger.error(f"Error distributing SOL: {str(e)}")
            raise

    async def recall_sol(self, wallet_keys: List[str]) -> float:
        """Recalls SOL from trading wallets back to main wallet"""
        total_recalled = 0.0
        try:
            main_pubkey = Pubkey(Keypair.from_secret_key(bytes.fromhex(self.main_wallet_key)).public_key)

            for wallet_key in wallet_keys:
                wallet = self.trading_wallets[wallet_key]
                balance = await self._retry_transaction(self.get_wallet_balance, str(wallet.public_key))

                if balance > self.min_sol_per_wallet:
                    transfer_amount = (balance - self.min_sol_per_wallet) * 1e9
                    recent_blockhash = await self.rpc_client.get_recent_blockhash()

                    transfer_tx = Transaction().add(
                        transfer(
                            TransferParams(
                            from_pubkey=wallet.public_key,
                            to_pubkey=main_pubkey,
                            lamports=int(transfer_amount)
                            )
                        )
                    )
                    transfer_tx.recent_blockhash = recent_blockhash["result"]["value"]["blockhash"]
                    transfer_tx.sign(wallet)

                    await self._retry_transaction(
                        self.rpc_client.send_transaction,
                        transfer_tx,
                        wallet
                    )
                    total_recalled += balance - self.min_sol_per_wallet
                    await self._random_delay()

            logger.info(f"Successfully recalled {total_recalled} SOL from {len(wallet_keys)} wallets")
            self.current_round += 1  # Increment round after successful recall
            return total_recalled

        except Exception as e:
            logger.error(f"Error recalling SOL: {str(e)}")
            return total_recalled

    async def get_wallet_balance(self, public_key: str) -> float:
        """Gets the SOL balance of a wallet"""
        try:
            response = await self.rpc_client.get_balance(public_key)
            if response["result"]["value"] is not None:
                return float(response["result"]["value"]) / 1e9
            return 0.0
        except Exception as e:
            logger.error(f"Error getting wallet balance: {str(e)}")
            raise
