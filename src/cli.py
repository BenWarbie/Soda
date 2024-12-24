"""
Command-line interface for Solana trading bot.
Provides terminal-based access to trading operations.
"""
import os
import asyncio
import argparse
import logging
from typing import Optional
from dotenv import load_dotenv
from wallet.wallet_manager import WalletManager
from trading.trade_executor import TradeExecutor, TradingMode
from trading.dex_interface import RaydiumDEX

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_argparse() -> argparse.ArgumentParser:
    """Configure command line argument parser"""
    parser = argparse.ArgumentParser(description='Solana Trading Bot CLI')
    parser.add_argument('--mode', choices=['SAFE', 'NORMAL', 'AGGRESSIVE', 'HIGH_FREQUENCY'],
                      default='SAFE', help='Trading mode')
    parser.add_argument('--duration', type=int, default=60,
                      help='Trading session duration in minutes')
    parser.add_argument('--wallets', type=int, default=10,
                      help='Number of trading wallets to create')
    parser.add_argument('--min-amount', type=float, default=0.1,
                      help='Minimum trade amount in SOL')
    parser.add_argument('--max-amount', type=float, default=1.0,
                      help='Maximum trade amount in SOL')
    parser.add_argument('--pattern', choices=['PUMP', 'MILKSHAKE', 'HIGH_FREQUENCY'],
                      default='MILKSHAKE', help='Trading pattern to execute')
    return parser

async def run_trading_session(args: argparse.Namespace):
    """Execute trading session with provided configuration"""
    try:
        # Initialize components
        wallet_manager = WalletManager()
        dex = RaydiumDEX()

        config = {
            'wallet_group_size': args.wallets,
            'session_duration': args.duration,
            'min_amount': args.min_amount,
            'max_amount': args.max_amount,
            'pattern': args.pattern,
            'high_frequency': {
                'enabled': args.pattern == 'HIGH_FREQUENCY',
                'trades_per_minute': 300,
                'burst_duration': 30
            }
        }

        executor = TradeExecutor(wallet_manager, dex, config)

        # Start trading session
        logger.info(f"Starting trading session in {args.mode} mode")
        logger.info(f"Pattern: {args.pattern}")
        logger.info(f"Duration: {args.duration} minutes")
        logger.info(f"Wallet count: {args.wallets}")

        await executor.start_trading_session()

        # Generate and display report
        report = await executor.get_session_report()
        logger.info("\nSession Report:")
        logger.info(f"Total Volume: {report.get('total_volume', 0)} SOL")
        logger.info(f"Trade Count: {report.get('trade_count', 0)}")
        logger.info(f"Average Trade Size: {report.get('avg_trade_size', 0)} SOL")

    except Exception as e:
        logger.error(f"Error in trading session: {str(e)}")
        raise

def main():
    """Main CLI entry point"""
    parser = setup_argparse()
    args = parser.parse_args()

    # Set trading mode in environment
    os.environ["TRADING_MODE"] = args.mode

    # Run trading session
    asyncio.run(run_trading_session(args))

if __name__ == "__main__":
    main()
