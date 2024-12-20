"""Helper functions for Solana blockchain interactions."""
from typing import Dict
from solders.rpc.async_api import AsyncClient

async def get_token_balance(
    client: AsyncClient,
    wallet_address: str,
    token_address: str
) -> Dict:
    """Gets the balance of a specific token for a wallet"""
    try:
        response = await client.get_token_accounts_by_owner(
            wallet_address,
            {"mint": token_address}
        )
        return response["result"]
    except Exception as e:
        print(f"Error getting token balance: {e}")
        return {"value": None}

async def get_recent_blockhash(client: AsyncClient) -> str:
    """Gets the most recent blockhash"""
    try:
        response = await client.get_recent_blockhash()
        return response["result"]["value"]["blockhash"]
    except Exception as e:
        print(f"Error getting recent blockhash: {e}")
        return None
