# ESP32 EVM Django Backend - GCP Deployment PowerShell Script
# Automated deployment to Google Cloud Platform for Windows

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory=$false)]
    [string]$DatabaseInstance = "evm-postgres-instance"
)

# Configuration
$AppName = "esp32-evm-backend"
$DatabaseName = "evm_voting"
$DatabaseUser = "evm_user"

Write-Host "🚀 ESP32 EVM Django Backend - GCP Deployment" -ForegroundColor Blue
Write-Host "================================================" -ForegroundColor Blue
Write-Host "Project ID: $ProjectId" -ForegroundColor Yellow
Write-Host "Region: $Region" -ForegroundColor Yellow
Write-Host ""

# Function to check if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Check requirements
Write-Host "📋 Checking requirements..." -ForegroundColor Yellow

if (!(Test-Command "gcloud")) {
    Write-Host "❌ Google Cloud SDK not found. Please install it first." -ForegroundColor Red
    Write-Host "Visit: https://cloud.google.com/sdk/docs/install" -ForegroundColor Red
    exit 1
}

if (!(Test-Command "python")) {
    Write-Host "❌ Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Requirements check passed" -ForegroundColor Green

# Authenticate with GCP
Write-Host "🔐 Authenticating with Google Cloud..." -ForegroundColor Yellow

# Check if already authenticated
$currentAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null | Select-Object -First 1
if (!$currentAccount) {
    Write-Host "Please authenticate with Google Cloud:"
    gcloud auth login
}

# Set project
gcloud config set project $ProjectId
Write-Host "✅ Authenticated with project: $ProjectId" -ForegroundColor Green

# Enable required APIs
Write-Host "🔧 Enabling required APIs..." -ForegroundColor Yellow

$apis = @(
    "appengine.googleapis.com",
    "cloudsql.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "cloudbuild.googleapis.com",
    "secretmanager.googleapis.com",
    "redis.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "Enabling $api..." -ForegroundColor Gray
    gcloud services enable $api --project=$ProjectId
}

Write-Host "✅ APIs enabled" -ForegroundColor Green

# Create App Engine application
Write-Host "🏗️ Setting up App Engine..." -ForegroundColor Yellow

try {
    $appExists = gcloud app describe --project=$ProjectId 2>$null
    if (!$appExists) {
        Write-Host "Creating App Engine application..."
        gcloud app create --region=$Region --project=$ProjectId
    } else {
        Write-Host "App Engine application already exists"
    }
} catch {
    Write-Host "Creating App Engine application..."
    gcloud app create --region=$Region --project=$ProjectId
}

Write-Host "✅ App Engine ready" -ForegroundColor Green

# Create Cloud SQL instance
Write-Host "🗄️ Setting up PostgreSQL database..." -ForegroundColor Yellow

try {
    $instanceExists = gcloud sql instances describe $DatabaseInstance --project=$ProjectId 2>$null
    if (!$instanceExists) {
        Write-Host "Creating Cloud SQL PostgreSQL instance..."
        gcloud sql instances create $DatabaseInstance `
            --database-version=POSTGRES_14 `
            --tier=db-f1-micro `
            --region=$Region `
            --project=$ProjectId
        
        Write-Host "Creating database..."
        gcloud sql databases create $DatabaseName --instance=$DatabaseInstance --project=$ProjectId
        
        Write-Host "Creating database user..."
        $DbPassword = Read-Host "Enter database password" -AsSecureString
        $DbPasswordText = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($DbPassword))
        
        gcloud sql users create $DatabaseUser `
            --instance=$DatabaseInstance `
            --password=$DbPasswordText `
            --project=$ProjectId
            
        Write-Host "✅ Database created" -ForegroundColor Green
        Write-Host "📝 Database connection: postgresql://$DatabaseUser`:$DbPasswordText@/$DatabaseName`?host=/cloudsql/$ProjectId`:$Region`:$DatabaseInstance" -ForegroundColor Yellow
    } else {
        Write-Host "Cloud SQL instance already exists"
    }
} catch {
    Write-Host "Error creating database: $_" -ForegroundColor Red
}

# Create Redis instance
Write-Host "🔴 Setting up Redis cache..." -ForegroundColor Yellow

$RedisInstance = "evm-redis-cache"

try {
    $redisExists = gcloud redis instances describe $RedisInstance --region=$Region --project=$ProjectId 2>$null
    if (!$redisExists) {
        Write-Host "Creating Redis instance..."
        gcloud redis instances create $RedisInstance `
            --size=1 `
            --region=$Region `
            --redis-version=redis_6_x `
            --project=$ProjectId
            
        Write-Host "✅ Redis instance created" -ForegroundColor Green
    } else {
        Write-Host "Redis instance already exists"
    }
} catch {
    Write-Host "Error creating Redis instance: $_" -ForegroundColor Red
}

# Set up secrets
Write-Host "🔒 Setting up Secret Manager..." -ForegroundColor Yellow

# Generate secret key
$SecretKey = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Create secrets
try {
    echo $SecretKey | gcloud secrets create django-secret-key --data-file=- --project=$ProjectId 2>$null
    Write-Host "✅ Secrets configured" -ForegroundColor Green
} catch {
    Write-Host "Secret may already exist, continuing..."
}

# Prepare environment file
Write-Host "⚙️ Preparing environment configuration..." -ForegroundColor Yellow

if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "📝 Please edit .env file with your production values" -ForegroundColor Yellow
    Write-Host "Opening .env file for editing..."
    notepad.exe ".env"
    Write-Host "Press Enter when done editing .env file..."
    Read-Host
}

Write-Host "✅ Environment prepared" -ForegroundColor Green

# Deploy application
Write-Host "🚀 Deploying application..." -ForegroundColor Yellow

# Install dependencies
Write-Host "Installing dependencies..."
pip install -r requirements_production_fixed.txt

# Collect static files
Write-Host "Collecting static files..."
python manage.py collectstatic --noinput --settings=evm_backend.settings_production

# Run migrations
Write-Host "📊 Running database migrations..."
python manage.py migrate --settings=evm_backend.settings_production

# Deploy to App Engine
Write-Host "Deploying to App Engine..."
gcloud app deploy app.yaml --quiet --project=$ProjectId

Write-Host "✅ Application deployed successfully!" -ForegroundColor Green

# Create superuser
Write-Host "👤 Creating admin superuser..." -ForegroundColor Yellow
Write-Host "Please create an admin user for the Django admin interface:"
python manage.py createsuperuser --settings=evm_backend.settings_production

Write-Host "✅ Superuser created" -ForegroundColor Green

# Display deployment info
Write-Host ""
Write-Host "================================================" -ForegroundColor Green
Write-Host "🎉 DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green

$AppUrl = "https://$ProjectId.appspot.com"

Write-Host "📱 Application URL: $AppUrl" -ForegroundColor Blue
Write-Host "🔧 Admin Interface: $AppUrl/admin/" -ForegroundColor Blue
Write-Host "📡 API Endpoints:" -ForegroundColor Blue
Write-Host "   - Health Check: $AppUrl/api/health/"
Write-Host "   - ESP32 Auth: $AppUrl/api/auth/"
Write-Host "   - Active Elections: $AppUrl/api/elections/"
Write-Host "   - Cast Vote: $AppUrl/api/vote/"
Write-Host ""

Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Update your ESP32 config.h with the new backend URL:"
Write-Host "   #define BACKEND_URL `"$AppUrl`""
Write-Host "2. Test the API endpoints"
Write-Host "3. Configure your domain (optional)"
Write-Host "4. Set up monitoring and alerts"
Write-Host ""

Write-Host "🔍 View logs: gcloud app logs tail -s default" -ForegroundColor Blue
Write-Host "📊 Monitoring: https://console.cloud.google.com/appengine" -ForegroundColor Blue

Write-Host ""
Write-Host "🚀 Deployment completed successfully!" -ForegroundColor Green