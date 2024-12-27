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

## Windows Setup Guide
1. Install Prerequisites
   - Download and install Python 3.10 from [python.org](https://www.python.org/downloads/)
     - **IMPORTANT**: Check "Add Python 3.10 to PATH" during installation
   - Download and install Git from [git-scm.com](https://git-scm.com/download/win)
     - Select "Git from the command line and also from 3rd-party software"
     - Choose "Use Windows' default console window"
     - Select "Default (fast-forward or merge)" for pull behavior

2. Clone and Setup
   ```powershell
   # Open PowerShell as Administrator
   git clone https://github.com/BenWarbie/Soda.git
   cd Soda
   ```

3. Run Setup Script
   ```powershell
   # This will create a virtual environment and install dependencies
   .\setup_windows.ps1
   ```

4. Verify Installation
   ```powershell
   # Check package versions
   pip freeze | findstr "solana solders"
   # Expected output:
   # solana==0.30.2
   # solders>=0.18.1,<0.19.0
   ```

5. Run the Bot
   ```powershell
   # Example command with safe mode
   python src/cli.py --mode SAFE --duration 30 --wallets 5 --min-amount 0.1
   ```

### Windows Troubleshooting
1. ModuleNotFoundError
   - Ensure virtual environment is activated:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - Verify package installation:
     ```powershell
     pip install -r requirements.txt
     pip install -e .
     ```

2. Package Version Conflicts
   - Check installed versions:
     ```powershell
     pip freeze | findstr "solana solders"
     ```
   - If versions mismatch, run setup script again:
     ```powershell
     .\setup_windows.ps1
     ```

3. Permission Issues
   - Run PowerShell as Administrator
   - Ensure Git is configured properly:
     ```powershell
     git config --global user.name "Your Name"
     git config --global user.email "your.email@example.com"
     ```

## Development Workflow
1. Create feature branch
2. Implement changes
3. Test your changes (see Testing section below)
4. Submit pull request

## Testing

### Local Testing
```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests with coverage
pytest tests/ --cov=src/

# View coverage report in terminal
pytest tests/ --cov=src/ --cov-report=term-missing

# Run specific test file
pytest tests/test_trade_executor.py
```

### Test Configuration
The project uses pytest for testing with the following configuration:
- `pytest.ini`: Configures test discovery and coverage settings
- `.coveragerc`: Defines coverage measurement rules
- Test files are located in the `tests/` directory
- Coverage reports track code in the `src/` directory

### CI/CD
Tests run automatically on pull requests via GitHub Actions:
- Multi-OS testing:
  - Windows (windows-latest)
  - Linux (ubuntu-latest)
- Python 3.10 environment
- Automated dependency installation
- Coverage reporting via Codecov

### Writing Tests
1. Create test files in the `tests/` directory
2. Use `pytest.mark.asyncio` for async tests
3. Follow existing test patterns:
```python
import pytest

@pytest.mark.asyncio
async def test_example():
    # Arrange
    expected = "result"

    # Act
    actual = await some_async_function()

    # Assert
    assert actual == expected
```

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
