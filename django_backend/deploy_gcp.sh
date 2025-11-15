#!/bin/bash

# ESP32 EVM Django Backend - GCP Deployment Script
# Automated deployment to Google Cloud Platform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="your-gcp-project-id"
APP_NAME="esp32-evm-backend"
REGION="us-central1"
DATABASE_INSTANCE="evm-postgres-instance"

echo -e "${BLUE}🚀 ESP32 EVM Django Backend - GCP Deployment${NC}"
echo "================================================"

# Check if required tools are installed
check_requirements() {
    echo -e "${YELLOW}📋 Checking requirements...${NC}"
    
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}❌ Google Cloud SDK not found. Please install it first.${NC}"
        echo "Visit: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    
    if ! command -v python &> /dev/null; then
        echo -e "${RED}❌ Python not found. Please install Python 3.9+${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Requirements check passed${NC}"
}

# Authenticate with GCP
authenticate_gcp() {
    echo -e "${YELLOW}🔐 Authenticating with Google Cloud...${NC}"
    
    # Check if already authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n1 &> /dev/null; then
        echo "Please authenticate with Google Cloud:"
        gcloud auth login
    fi
    
    # Set project
    gcloud config set project $PROJECT_ID
    echo -e "${GREEN}✅ Authenticated with project: $PROJECT_ID${NC}"
}

# Enable required APIs
enable_apis() {
    echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
    
    gcloud services enable appengine.googleapis.com
    gcloud services enable cloudsql.googleapis.com
    gcloud services enable cloudresourcemanager.googleapis.com
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable secretmanager.googleapis.com
    gcloud services enable redis.googleapis.com
    
    echo -e "${GREEN}✅ APIs enabled${NC}"
}

# Create App Engine application
create_app_engine() {
    echo -e "${YELLOW}🏗️  Setting up App Engine...${NC}"
    
    # Check if App Engine app already exists
    if ! gcloud app describe --project=$PROJECT_ID &> /dev/null; then
        echo "Creating App Engine application..."
        gcloud app create --region=$REGION --project=$PROJECT_ID
    else
        echo "App Engine application already exists"
    fi
    
    echo -e "${GREEN}✅ App Engine ready${NC}"
}

# Create Cloud SQL instance
create_database() {
    echo -e "${YELLOW}🗄️  Setting up PostgreSQL database...${NC}"
    
    # Check if instance already exists
    if ! gcloud sql instances describe $DATABASE_INSTANCE --project=$PROJECT_ID &> /dev/null; then
        echo "Creating Cloud SQL PostgreSQL instance..."
        gcloud sql instances create $DATABASE_INSTANCE \
            --database-version=POSTGRES_14 \
            --tier=db-f1-micro \
            --region=$REGION \
            --project=$PROJECT_ID
        
        echo "Creating database..."
        gcloud sql databases create evm_voting --instance=$DATABASE_INSTANCE --project=$PROJECT_ID
        
        echo "Creating database user..."
        read -p "Enter database username: " DB_USER
        read -s -p "Enter database password: " DB_PASSWORD
        echo
        
        gcloud sql users create $DB_USER \
            --instance=$DATABASE_INSTANCE \
            --password=$DB_PASSWORD \
            --project=$PROJECT_ID
            
        echo -e "${GREEN}✅ Database created${NC}"
        echo -e "${YELLOW}📝 Database connection: postgresql://$DB_USER:$DB_PASSWORD@/$DATABASE_INSTANCE?host=/cloudsql/$PROJECT_ID:$REGION:$DATABASE_INSTANCE${NC}"
    else
        echo "Cloud SQL instance already exists"
    fi
}

# Create Redis instance
create_redis() {
    echo -e "${YELLOW}🔴 Setting up Redis cache...${NC}"
    
    REDIS_INSTANCE="evm-redis-cache"
    
    # Check if Redis instance exists
    if ! gcloud redis instances describe $REDIS_INSTANCE --region=$REGION --project=$PROJECT_ID &> /dev/null; then
        echo "Creating Redis instance..."
        gcloud redis instances create $REDIS_INSTANCE \
            --size=1 \
            --region=$REGION \
            --redis-version=redis_6_x \
            --project=$PROJECT_ID
            
        echo -e "${GREEN}✅ Redis instance created${NC}"
    else
        echo "Redis instance already exists"
    fi
}

# Set up secrets
setup_secrets() {
    echo -e "${YELLOW}🔒 Setting up Secret Manager...${NC}"
    
    # Generate secret key
    SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    
    # Create secrets
    echo $SECRET_KEY | gcloud secrets create django-secret-key --data-file=- --project=$PROJECT_ID || true
    
    echo -e "${GREEN}✅ Secrets configured${NC}"
}

# Prepare environment file
prepare_environment() {
    echo -e "${YELLOW}⚙️  Preparing environment configuration...${NC}"
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        echo -e "${YELLOW}📝 Please edit .env file with your production values${NC}"
        echo "Press Enter when done..."
        read
    fi
    
    echo -e "${GREEN}✅ Environment prepared${NC}"
}

# Deploy application
deploy_app() {
    echo -e "${YELLOW}🚀 Deploying application...${NC}"
    
    # Install dependencies
    pip install -r requirements_production.txt
    
    # Collect static files
    python manage.py collectstatic --noinput --settings=evm_backend.settings_production
    
    # Run migrations
    echo -e "${YELLOW}📊 Running database migrations...${NC}"
    python manage.py migrate --settings=evm_backend.settings_production
    
    # Deploy to App Engine
    gcloud app deploy app.yaml --quiet --project=$PROJECT_ID
    
    echo -e "${GREEN}✅ Application deployed successfully!${NC}"
}

# Create superuser
create_superuser() {
    echo -e "${YELLOW}👤 Creating admin superuser...${NC}"
    
    echo "Please create an admin user for the Django admin interface:"
    python manage.py createsuperuser --settings=evm_backend.settings_production
    
    echo -e "${GREEN}✅ Superuser created${NC}"
}

# Display deployment info
show_deployment_info() {
    echo -e "${GREEN}"
    echo "================================================"
    echo "🎉 DEPLOYMENT SUCCESSFUL!"
    echo "================================================"
    echo -e "${NC}"
    
    APP_URL="https://$PROJECT_ID.appspot.com"
    
    echo -e "${BLUE}📱 Application URL:${NC} $APP_URL"
    echo -e "${BLUE}🔧 Admin Interface:${NC} $APP_URL/admin/"
    echo -e "${BLUE}📡 API Endpoints:${NC}"
    echo "   - Health Check: $APP_URL/api/health/"
    echo "   - ESP32 Auth: $APP_URL/api/auth/"
    echo "   - Active Elections: $APP_URL/api/elections/"
    echo "   - Cast Vote: $APP_URL/api/vote/"
    echo
    echo -e "${YELLOW}📝 Next Steps:${NC}"
    echo "1. Update your ESP32 config.h with the new backend URL:"
    echo "   #define BACKEND_URL \"$APP_URL\""
    echo "2. Test the API endpoints"
    echo "3. Configure your domain (optional)"
    echo "4. Set up monitoring and alerts"
    echo
    echo -e "${BLUE}🔍 View logs:${NC} gcloud app logs tail -s default"
    echo -e "${BLUE}📊 Monitoring:${NC} https://console.cloud.google.com/appengine"
}

# Main deployment function
main() {
    echo -e "${BLUE}Starting deployment process...${NC}"
    
    check_requirements
    authenticate_gcp
    enable_apis
    create_app_engine
    create_database
    create_redis
    setup_secrets
    prepare_environment
    deploy_app
    create_superuser
    show_deployment_info
    
    echo -e "${GREEN}🚀 Deployment completed successfully!${NC}"
}

# Run main function
main "$@"