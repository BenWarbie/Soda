# Soda Trading Bot - Windows Setup Script
# This script automates the setup process for the Soda trading bot on Windows

# Error handling
$ErrorActionPreference = "Stop"

Write-Host "Starting Soda Trading Bot Setup..." -ForegroundColor Green

# Check Python installation
try {
    $pythonVersion = python --version
    if (-not $pythonVersion.Contains("Python 3.10")) {
        Write-Host "Error: Python 3.10 is required. Please install Python 3.10 from python.org" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "Error: Python is not installed. Please install Python 3.10 from python.org" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (Test-Path "venv-py310") {
    Write-Host "Removing existing virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "venv-py310"
}

# Create Python virtual environment
Write-Host "Creating Python virtual environment..." -ForegroundColor Green
python -m venv venv-py310

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
.\venv-py310\Scripts\Activate.ps1

# Install backend dependencies
Write-Host "Installing backend dependencies..." -ForegroundColor Green
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# Setup frontend
Write-Host "Setting up frontend..." -ForegroundColor Green
cd dashboard

# Check if pnpm is installed
try {
    pnpm --version
} catch {
    Write-Host "Installing pnpm..." -ForegroundColor Yellow
    npm install -g pnpm
}

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Green
pnpm install

# Return to root directory
cd ..

# Setup environment configuration
Write-Host "Setting up environment configuration..." -ForegroundColor Green
if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
    Write-Host "Created .env file from template. Please update the configuration in .env" -ForegroundColor Yellow
}

Write-Host "`nSetup completed successfully!" -ForegroundColor Green
Write-Host "`nNext steps:"
Write-Host "1. Update the .env file with your configuration"
Write-Host "2. Start the backend: cd src && python -m uvicorn api.main:app --reload"
Write-Host "3. Start the frontend: cd dashboard && pnpm dev"
