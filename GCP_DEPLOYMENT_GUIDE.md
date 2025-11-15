# ESP32 EVM Django Backend - Google Cloud Platform Deployment Guide

## 🚀 **Complete GCP Deployment Guide**

This guide will walk you through deploying your ESP32 Electronic Voting Machine Django backend to Google Cloud Platform using App Engine, Cloud SQL, and other GCP services.

---

## 📋 **Prerequisites**

### 1. **Google Cloud Account Setup**
- Google Cloud account with billing enabled
- New GCP project created
- gcloud CLI installed and configured

### 2. **Local Environment**
- Python 3.9+
- Git
- Your ESP32 EVM Django project

### 3. **Required GCP Services**
- App Engine (Django hosting)
- Cloud SQL (PostgreSQL database)
- Cloud Storage (static files)
- Secret Manager (sensitive data)
- Cloud Build (CI/CD)
- Redis (caching)

---

## 🔧 **Quick Setup Commands**

### **Step 1: Install Google Cloud SDK**
```bash
# Windows (using Chocolatey)
choco install gcloudsdk

# Or download from: https://cloud.google.com/sdk/docs/install

# Authenticate and set project
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

### **Step 2: Clone and Navigate to Project**
```bash
cd C:\Users\sdeep\OneDrive\Documents\PlatformIO\Projects\evm\django_backend
```

### **Step 3: Run Automated Deployment**
```bash
# Make deployment script executable (Git Bash on Windows)
chmod +x deploy_gcp.sh

# Run deployment
./deploy_gcp.sh
```

---

## 📚 **Manual Deployment Steps**

### **Step 1: Enable Required APIs**
```bash
gcloud services enable appengine.googleapis.com
gcloud services enable cloudsql.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable secretmanager.googleapis.com
gcloud services enable redis.googleapis.com
```

### **Step 2: Create App Engine Application**
```bash
gcloud app create --region=us-central1
```

### **Step 3: Set Up PostgreSQL Database**
```bash
# Create Cloud SQL instance
gcloud sql instances create evm-postgres-instance \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=us-central1

# Create database
gcloud sql databases create evm_voting --instance=evm-postgres-instance

# Create database user
gcloud sql users create evm_user \
    --instance=evm-postgres-instance \
    --password=YOUR_SECURE_PASSWORD
```

### **Step 4: Set Up Redis Cache**
```bash
gcloud redis instances create evm-redis-cache \
    --size=1 \
    --region=us-central1 \
    --redis-version=redis_6_x
```

### **Step 5: Configure Secrets**
```bash
# Generate and store Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" | gcloud secrets create django-secret-key --data-file=-

# Store database password
echo "YOUR_DB_PASSWORD" | gcloud secrets create db-password --data-file=-
```

### **Step 6: Configure Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your values
notepad .env
```

**Required .env values:**
```bash
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-project-id.appspot.com
DATABASE_URL=postgresql://evm_user:password@/evm_voting?host=/cloudsql/your-project-id:us-central1:evm-postgres-instance
BLOCKCHAIN_NETWORK=mainnet
CORS_ALLOWED_ORIGINS=https://your-esp32-domain.com
```

### **Step 7: Deploy Application**
```bash
# Install dependencies
pip install -r requirements_production.txt

# Collect static files
python manage.py collectstatic --noinput --settings=evm_backend.settings_production

# Run migrations
python manage.py migrate --settings=evm_backend.settings_production

# Deploy to App Engine
gcloud app deploy app.yaml
```

### **Step 8: Create Admin User**
```bash
python manage.py createsuperuser --settings=evm_backend.settings_production
```

---

## 🔐 **Security Configuration**

### **1. Update app.yaml Environment Variables**
```yaml
env_variables:
  DJANGO_SETTINGS_MODULE: evm_backend.settings_production
  SECRET_KEY: "projects/YOUR_PROJECT_ID/secrets/django-secret-key/versions/latest"
  DEBUG: "False"
  ALLOWED_HOSTS: "your-project-id.appspot.com"
  DATABASE_URL: "postgresql://evm_user:password@/evm_voting?host=/cloudsql/your-project-id:us-central1:evm-postgres-instance"
```

### **2. Configure HTTPS and Domain**
```bash
# Map custom domain (optional)
gcloud app domain-mappings create your-domain.com

# SSL certificates are automatically provisioned
```

### **3. Set Up IAM Permissions**
```bash
# Create service account for ESP32 API access
gcloud iam service-accounts create esp32-api-service

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:esp32-api-service@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"
```

---

## 📱 **ESP32 Configuration**

### **Update config.h for GCP Backend**
```cpp
// config.h - Updated for GCP deployment
#ifndef CONFIG_H
#define CONFIG_H

// WiFi Configuration
#define WIFI_SSID "your-wifi-ssid"
#define WIFI_PASSWORD "your-wifi-password"

// Backend Configuration (Updated for GCP)
#define BACKEND_URL "https://your-project-id.appspot.com"
#define API_TIMEOUT 30000  // 30 seconds timeout for GCP
#define MAX_RETRY_ATTEMPTS 3

// Device Configuration
#define DEVICE_ID "ESP32_EVM_001"
#define FINGERPRINT_SENSOR_PIN 2
#define LCD_ADDRESS 0x27

// API Endpoints
#define AUTH_ENDPOINT "/api/auth/"
#define VOTE_ENDPOINT "/api/vote/"
#define ELECTIONS_ENDPOINT "/api/elections/"
#define HEALTH_ENDPOINT "/api/health/"

// Security
#define API_TOKEN_LENGTH 40
#define FINGERPRINT_TEMPLATE_SIZE 534

// Hardware Pins
#define BUTTON_SELECT 12
#define BUTTON_BACK 14
#define BUTTON_UP 26
#define BUTTON_DOWN 27
#define BUZZER_PIN 25
#define LED_STATUS_PIN 2

#endif
```

### **Test ESP32 Connection**
```cpp
// Add to main_backend.cpp for GCP testing
void testGCPConnection() {
    Serial.println("Testing GCP Backend Connection...");
    
    HTTPClient http;
    http.begin(String(BACKEND_URL) + "/api/health/");
    http.addHeader("Content-Type", "application/json");
    http.setTimeout(API_TIMEOUT);
    
    int httpResponseCode = http.GET();
    
    if (httpResponseCode == 200) {
        String response = http.getString();
        Serial.println("✅ GCP Backend Connected:");
        Serial.println(response);
    } else {
        Serial.printf("❌ Connection Failed: %d\n", httpResponseCode);
    }
    
    http.end();
}
```

---

## 🔍 **Testing and Validation**

### **1. Test API Endpoints**
```bash
# Health check
curl https://your-project-id.appspot.com/api/health/

# ESP32 authentication test
curl -X POST https://your-project-id.appspot.com/api/auth/ \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "TEST_ESP32_001",
    "fingerprint_template": "00112233445566778899",
    "aadhar_number": "123456789012"
  }'
```

### **2. Load Testing**
```bash
# Install Apache Bench for load testing
# Test voting endpoint performance
ab -n 100 -c 10 -H "Content-Type: application/json" \
   -p test_vote.json \
   https://your-project-id.appspot.com/api/vote/
```

### **3. Monitor Application**
```bash
# View real-time logs
gcloud app logs tail -s default

# Check performance metrics
gcloud app browse
```

---

## 📊 **Monitoring and Maintenance**

### **1. Set Up Alerts**
```bash
# Create uptime check
gcloud alpha monitoring uptime create \
    --hostname=your-project-id.appspot.com \
    --path=/api/health/
```

### **2. Database Backup**
```bash
# Automated backup for Cloud SQL
gcloud sql backups create --instance=evm-postgres-instance
```

### **3. Update Deployment**
```bash
# Deploy updates
gcloud app deploy app.yaml --promote
```

---

## 💰 **Cost Optimization**

### **1. App Engine Scaling**
```yaml
# In app.yaml
automatic_scaling:
  min_instances: 0  # Scale to zero when not in use
  max_instances: 5
  target_cpu_utilization: 0.6
```

### **2. Database Optimization**
```bash
# Use smaller instance for development
gcloud sql instances patch evm-postgres-instance --tier=db-f1-micro
```

### **3. Monitoring Costs**
- Set up billing alerts
- Use GCP Cost Management tools
- Monitor usage with Cloud Monitoring

---

## 🚨 **Troubleshooting**

### **Common Issues and Solutions**

#### **1. Database Connection Issues**
```bash
# Check Cloud SQL proxy connection
gcloud sql connect evm-postgres-instance --user=evm_user --database=evm_voting
```

#### **2. Static Files Not Loading**
```bash
# Ensure whitenoise is configured
pip install whitenoise
python manage.py collectstatic --noinput
```

#### **3. ESP32 Connection Timeouts**
```cpp
// Increase timeout in ESP32 code
http.setTimeout(30000);  // 30 seconds for GCP
```

#### **4. Memory Issues**
```yaml
# Increase App Engine memory in app.yaml
resources:
  memory_gb: 1
```

---

## 🎉 **Post-Deployment Checklist**

- [ ] ✅ Application deployed and accessible
- [ ] ✅ Database migrations completed
- [ ] ✅ Admin user created
- [ ] ✅ API endpoints responding correctly
- [ ] ✅ ESP32 configuration updated
- [ ] ✅ HTTPS certificate active
- [ ] ✅ Monitoring and logging configured
- [ ] ✅ Backup strategy implemented
- [ ] ✅ Load testing completed
- [ ] ✅ Documentation updated

---

## 📞 **Support and Resources**

### **GCP Documentation**
- [App Engine Python](https://cloud.google.com/appengine/docs/standard/python3)
- [Cloud SQL for PostgreSQL](https://cloud.google.com/sql/docs/postgres)
- [Secret Manager](https://cloud.google.com/secret-manager/docs)

### **Application URLs**
```
🌐 Application: https://your-project-id.appspot.com
🔧 Admin: https://your-project-id.appspot.com/admin/
📊 Monitoring: https://console.cloud.google.com/appengine
💾 Database: https://console.cloud.google.com/sql/instances
```

### **Support Commands**
```bash
# View deployment status
gcloud app describe

# Check service status
gcloud app services list

# View instance details
gcloud app instances list

# Access Cloud Shell for debugging
gcloud cloud-shell ssh
```

---

**🎊 Your ESP32 EVM Django backend is now running on Google Cloud Platform!**

The system is now enterprise-ready with automatic scaling, managed database, secure authentication, and professional monitoring. Your ESP32 devices can now communicate with a production-grade backend infrastructure.

---

*Deployment Guide Version: 1.0*  
*Last Updated: November 15, 2025*  
*ESP32 Electronic Voting Machine - Django Backend on GCP*