# Solana Trading Bot

Terminal-based multi-wallet trading bot for Solana blockchain with coordinated buy/sell capabilities.

## Features
- Multi-wallet management and coordination
- Automated trading patterns (Pump, Milkshake, High-Frequency)
- SOL distribution and recall functionality
- Configurable trading modes (Safe/Normal/Aggressive/High-Frequency)
- Terminal-based execution and monitoring

## Setup
1. Create and activate Python virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Usage
Run the trading bot from the command line:
```bash
python src/cli.py --mode SAFE --duration 30 --wallets 5 --min-amount 0.1
```

### Command Line Arguments
- `--mode`: Trading mode (SAFE/NORMAL/AGGRESSIVE/HIGH_FREQUENCY)
- `--duration`: Trading session duration in minutes
- `--wallets`: Number of trading wallets to create
- `--min-amount`: Minimum trade amount in SOL
- `--pattern`: Trading pattern (PUMP/MILKSHAKE/HIGH_FREQUENCY)

## Project Structure
```
solana-trading-bot/
├── src/
│   ├── wallet/       # Wallet management
│   ├── trading/      # Trading operations
│   └── utils/        # Utility functions
└── tests/            # Test suite
```
