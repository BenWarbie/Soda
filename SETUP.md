# Soda Trading Bot Setup Guide

## Prerequisites
- Git
- Python 3.10 (required for Solana compatibility)
- Solana CLI tools

## Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/BenWarbie/Soda.git
cd Soda
```

2. Create environment configuration:
```bash
cp .env.example .env
```

3. Configure environment variables in `.env`:
```bash
# Required configurations detailed in .env.example
```

## Development Environment

### Local Setup
1. Create a Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Trading Configuration

### Trading Modes
- SAFE: Conservative trading with minimal risk
- NORMAL: Balanced risk/reward trading
- AGGRESSIVE: Higher risk trading for potential higher returns
- HIGH_FREQUENCY: Rapid trading with multiple transactions

### Trading Patterns
1. Pump Pattern
   - Coordinated buy pressure across multiple wallets
   - Configurable volume distribution

2. Milkshake Pattern
   - Sequential trading across wallet groups
   - Customizable timing intervals

3. High-Frequency Pattern
   - Rapid trading execution
   - Automated position management

## Health Checks
The bot includes built-in health monitoring:
- Wallet balance verification
- Transaction success monitoring
- Error logging and reporting

## Troubleshooting

### Common Issues
1. Solana RPC connection:
   - Verify RPC endpoint in .env
   - Check network connectivity

2. Environment variables:
   - Verify `.env` file exists
   - Check all required variables are set

3. Wallet issues:
   - Ensure sufficient SOL balance
   - Verify wallet permissions

## Development Workflow
1. Create feature branch
2. Implement changes
3. Run tests: `pytest tests/`
4. Submit pull request

## Error Handling
The bot includes comprehensive error handling:
- Transaction failure recovery
- Network interruption handling
- Automatic retry mechanisms

## Logging
Logs are written to the terminal and include:
- Trading activity
- Wallet operations
- Error messages
- Performance metrics
