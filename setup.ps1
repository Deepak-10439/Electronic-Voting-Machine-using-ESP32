# EVM Django Backend - Quick Setup Script
# Run this script to set up the backend

Write-Host "🚀 Setting up EVM Django Backend..." -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists." -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Create .env file if it doesn't exist
Write-Host ""
Write-Host "Setting up environment variables..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host ".env file already exists." -ForegroundColor Yellow
} else {
    Copy-Item .env.example .env
    Write-Host "✓ Created .env file from template" -ForegroundColor Green
    Write-Host "⚠️  Please edit .env and add your Firebase configuration!" -ForegroundColor Yellow
}

# Run migrations
Write-Host ""
Write-Host "Running database migrations..." -ForegroundColor Yellow
python manage.py migrate
Write-Host "✓ Database migrations complete" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "✓ Setup Complete!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Add your firebase-credentials.json file to this folder"
Write-Host "2. Edit .env and set your FIREBASE_DATABASE_URL"
Write-Host "3. Run: python manage.py runserver"
Write-Host ""
Write-Host "API will be available at: http://127.0.0.1:8000" -ForegroundColor Cyan
Write-Host ""
