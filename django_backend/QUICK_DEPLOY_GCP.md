# ESP32 EVM Django Backend - GCP Quick Deploy

## 🚀 **Quick Deployment (5 Minutes)**

### **Prerequisites**
1. Google Cloud account with billing enabled
2. Google Cloud SDK installed
3. Python 3.9+ installed

### **Step 1: Setup**
```powershell
# Navigate to project
cd C:\Users\sdeep\OneDrive\Documents\PlatformIO\Projects\evm\django_backend

# Authenticate with Google Cloud
gcloud auth login
```

### **Step 2: Deploy (Choose One)**

#### **Option A: Automated PowerShell Script (Recommended)**
```powershell
# Run automated deployment
.\Deploy-GCP.ps1 -ProjectId "your-gcp-project-id"
```

#### **Option B: Bash Script (Git Bash/Linux)**
```bash
# Make executable and run
chmod +x deploy_gcp.sh
./deploy_gcp.sh
```

#### **Option C: Manual Commands**
```powershell
# Enable APIs
gcloud services enable appengine.googleapis.com cloudsql.googleapis.com

# Create App Engine app
gcloud app create --region=us-central1

# Deploy
gcloud app deploy app.yaml
```

### **Step 3: Update ESP32**
```cpp
// Update config.h with your new backend URL
#define BACKEND_URL "https://your-project-id.appspot.com"
```

## 🎯 **Result**
- ✅ Django backend running on Google App Engine
- ✅ PostgreSQL database on Cloud SQL
- ✅ Automatic scaling and HTTPS
- ✅ Production-ready with monitoring

## 🔗 **Your URLs**
- **App:** https://your-project-id.appspot.com
- **Admin:** https://your-project-id.appspot.com/admin/
- **API:** https://your-project-id.appspot.com/api/

## 📊 **Estimated Costs**
- **App Engine:** $0-50/month (scales to zero)
- **Cloud SQL:** $7-30/month (db-f1-micro)
- **Total:** ~$10-80/month depending on usage

## 🆘 **Need Help?**
See full guide: `GCP_DEPLOYMENT_GUIDE.md`

---
**Time to deploy: ~5 minutes | Your ESP32 EVM is now enterprise-ready! 🎉**