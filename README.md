# Solana Trading Bot

Multi-wallet trading bot for Solana blockchain with coordinated buy/sell capabilities.

## Features
- Multi-wallet management and coordination
- Automated trading patterns across wallet groups
- SOL distribution and recall functionality
- Configurable trading modes (Safe/Normal/Aggressive)

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

## Project Structure
```
solana-trading-bot/
├── src/
│   ├── wallet/       # Wallet management
│   ├── trading/      # Trading operations
│   └── utils/        # Utility functions
└── tests/            # Test suite
```
