"""
Unit tests for wallet management functionality.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from src.wallet.wallet_manager import WalletManager
from solders.rpc.async_api import AsyncClient
from solders.keypair import Keypair

@pytest.fixture
async def wallet_manager():
    """Create WalletManager instance for testing"""
    rpc_client = AsyncClient("http://localhost:8899")
    manager = WalletManager(rpc_client)
    yield manager
    await manager.close()

@pytest.mark.asyncio
async def test_create_wallet_group(wallet_manager):
    """Test wallet group creation"""
    group_size = 5
    wallets = await wallet_manager.create_wallet_group(group_size)

    assert len(wallets) == group_size
    for wallet in wallets:
        assert isinstance(wallet, Keypair)

@pytest.mark.asyncio
async def test_distribute_sol(wallet_manager):
    """Test SOL distribution to wallets"""
    group_size = 3
    amount = 0.1
    wallets = await wallet_manager.create_wallet_group(group_size)

    # Mock RPC responses
    with patch.object(wallet_manager.rpc_client, 'get_balance') as mock_balance:
        mock_balance.return_value = {'result': {'value': 100000000}}  # 0.1 SOL

        with patch.object(wallet_manager.rpc_client, 'send_transaction') as mock_send:
            mock_send.return_value = {'result': 'transaction_signature'}

            # Test distribution
            result = await wallet_manager.distribute_sol(
                [str(w.public_key) for w in wallets],
                amount
            )

            assert result is True
            assert mock_send.call_count == group_size

@pytest.mark.asyncio
async def test_recall_sol(wallet_manager):
    """Test SOL recall from wallets"""
    group_size = 3
    wallets = await wallet_manager.create_wallet_group(group_size)

    # Mock RPC responses
    with patch.object(wallet_manager.rpc_client, 'get_balance') as mock_balance:
        mock_balance.return_value = {'result': {'value': 100000000}}  # 0.1 SOL

        with patch.object(wallet_manager.rpc_client, 'send_transaction') as mock_send:
            mock_send.return_value = {'result': 'transaction_signature'}

            # Test recall
            total_recalled = await wallet_manager.recall_sol(
                [str(w.public_key) for w in wallets]
            )

            assert total_recalled > 0
            assert mock_send.call_count == group_size

@pytest.mark.asyncio
async def test_wallet_manager_error_handling(wallet_manager):
    """Test error handling in wallet operations"""
    # Test invalid group size
    with pytest.raises(ValueError):
        await wallet_manager.create_wallet_group(0)

    # Test invalid amount
    with pytest.raises(ValueError):
        await wallet_manager.distribute_sol(['wallet1'], -1.0)

    # Test RPC failure
    with patch.object(wallet_manager.rpc_client, 'send_transaction') as mock_send:
        mock_send.side_effect = Exception("RPC Error")

        result = await wallet_manager.distribute_sol(['wallet1'], 0.1)
        assert result is False
