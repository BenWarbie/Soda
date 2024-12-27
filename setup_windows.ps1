# Soda Trading Bot - Windows Setup Script
# This script automates the setup process for the Soda trading bot on Windows

# Error handling
$ErrorActionPreference = "Stop"

Write-Host "Starting Soda Trading Bot Setup..." -ForegroundColor Green

# Check Git installation
try {
    $gitVersion = git --version
    Write-Host "Git version: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Git is not installed. Please install Git from https://git-scm.com/download/win" -ForegroundColor Red
    Write-Host "During installation:" -ForegroundColor Yellow
    Write-Host "- Select 'Git from the command line and also from 3rd-party software'" -ForegroundColor Yellow
    Write-Host "- Choose 'Use Windows' default console window'" -ForegroundColor Yellow
    Write-Host "- Select 'Default (fast-forward or merge)' for pull behavior" -ForegroundColor Yellow
    exit 1
}

# Check Python installation
try {
    $pythonVersion = python --version
    if (-not $pythonVersion.Contains("Python 3.10")) {
        Write-Host "Error: Python 3.10 is required. Please install Python 3.10 from python.org" -ForegroundColor Red
        Write-Host "IMPORTANT: Check 'Add Python 3.10 to PATH' during installation" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python is not installed. Please install Python 3.10 from python.org" -ForegroundColor Red
    Write-Host "IMPORTANT: Check 'Add Python 3.10 to PATH' during installation" -ForegroundColor Yellow
    exit 1
}

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "venv"
}

# Create Python virtual environment
Write-Host "Creating Python virtual environment..." -ForegroundColor Green
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Green
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools wheel
Write-Host "Note: If package installation fails, you may need to install Microsoft C++ Build Tools" -ForegroundColor Yellow
Write-Host "Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Yellow
Write-Host "Select 'Desktop development with C++' workload during installation" -ForegroundColor Yellow
pip install -r requirements.txt
pip install -e .

# Setup environment configuration
Write-Host "Setting up environment configuration..." -ForegroundColor Green
if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
    Write-Host "Created .env file from template. Please update the configuration in .env" -ForegroundColor Yellow
}

Write-Host "`nSetup completed successfully!" -ForegroundColor Green
Write-Host "`nNext steps:"
Write-Host "1. Update the .env file with your configuration"
Write-Host "2. Run the trading bot: python src/cli.py --mode SAFE --duration 30 --wallets 5"
Write-Host "3. For help with available options: python src/cli.py --help"
