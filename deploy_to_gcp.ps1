#!/usr/bin/env powershell
# Deploy Django Backend to Google Cloud Platform
# Make sure you have gcloud CLI installed and configured

Write-Host "🚀 Deploying EVM Backend to Google Cloud Platform..." -ForegroundColor Green
Write-Host "=" * 60

# Check if gcloud is installed
try {
    $gcloudVersion = gcloud --version 2>$null
    Write-Host "✅ Google Cloud SDK found" -ForegroundColor Green
} catch {
    Write-Host "❌ Google Cloud SDK not found!" -ForegroundColor Red
    Write-Host "Please install Google Cloud SDK from: https://cloud.google.com/sdk/docs/install"
    Write-Host "After installation, run: gcloud auth login"
    exit 1
}

# Check if user is authenticated
try {
    $currentAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
    if ([string]::IsNullOrEmpty($currentAccount)) {
        Write-Host "⚠️  No active authentication found" -ForegroundColor Yellow
        Write-Host "Please run: gcloud auth login"
        exit 1
    }
    Write-Host "✅ Authenticated as: $currentAccount" -ForegroundColor Green
} catch {
    Write-Host "❌ Authentication check failed" -ForegroundColor Red
    exit 1
}

# Set project ID (you can change this)
$PROJECT_ID = "fingerprint-evm-backend"

Write-Host "🏗️  Setting up GCP project..." -ForegroundColor Cyan
Write-Host "Project ID: $PROJECT_ID"

# Check if project exists
$projectExists = gcloud projects list --filter="projectId:$PROJECT_ID" --format="value(projectId)" 2>$null

if ([string]::IsNullOrEmpty($projectExists)) {
    Write-Host "📋 Creating new GCP project: $PROJECT_ID" -ForegroundColor Yellow
    gcloud projects create $PROJECT_ID --name="EVM Fingerprint Backend"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create project. Try using a different project ID." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Project $PROJECT_ID already exists" -ForegroundColor Green
}

# Set the project
Write-Host "🔧 Setting active project..." -ForegroundColor Cyan
gcloud config set project $PROJECT_ID

# Enable required APIs
Write-Host "🔌 Enabling required Google Cloud APIs..." -ForegroundColor Cyan
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Check if App Engine app exists
$appExists = gcloud app describe 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "📱 Creating App Engine application..." -ForegroundColor Cyan
    Write-Host "Choose a region (recommended: us-central for low latency)"
    gcloud app create
} else {
    Write-Host "✅ App Engine application already exists" -ForegroundColor Green
}

# Collect static files for Django
Write-Host "📦 Collecting static files..." -ForegroundColor Cyan
if (Test-Path "venv") {
    .\venv\Scripts\python.exe manage.py collectstatic --noinput
} else {
    python manage.py collectstatic --noinput
}

# Deploy to App Engine
Write-Host "🚀 Deploying to Google App Engine..." -ForegroundColor Cyan
Write-Host "This may take several minutes..."
gcloud app deploy --quiet

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Deployment successful!" -ForegroundColor Green
    $appUrl = gcloud app describe --format="value(defaultHostname)"
    Write-Host "🌐 Your backend is now live at: https://$appUrl" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Next steps:" -ForegroundColor Yellow
    Write-Host "1. Update your ESP32 config.h with the new URL:"
    Write-Host "   #define BACKEND_URL `"https://$appUrl`""
    Write-Host "2. Upload the updated firmware to ESP32"
    Write-Host "3. Test fingerprint enrollment!"
} else {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    Write-Host "Check the error messages above for troubleshooting."
}

Write-Host ""
Write-Host "📚 Useful commands:" -ForegroundColor Cyan
Write-Host "View logs: gcloud app logs tail -s default"
Write-Host "Open in browser: gcloud app browse"
Write-Host "View project: gcloud projects describe $PROJECT_ID"