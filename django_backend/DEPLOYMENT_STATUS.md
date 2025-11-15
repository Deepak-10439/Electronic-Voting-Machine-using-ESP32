# ESP32 EVM Backend Deployment - Billing Setup Required

## 🚨 **Billing Required for GCP Deployment**

Your ESP32 EVM Django backend is ready to deploy, but Google Cloud Platform requires billing to be enabled for most services including App Engine and Cloud Run.

---

## 💳 **Enable Billing (Required)**

### **Step 1: Enable Billing in GCP Console**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **Billing** in the left menu
3. Click **Link a billing account** or **Create billing account**
4. Add a valid payment method (credit/debit card)
5. Select your project: `gen-lang-client-0176730707`

### **Step 2: Verify Billing Status**
```bash
gcloud billing accounts list
gcloud billing projects link gen-lang-client-0176730707 --billing-account=BILLING_ACCOUNT_ID
```

---

## 🚀 **Once Billing is Enabled - Quick Deploy**

### **Option 1: App Engine Deployment (Recommended)**
```bash
# Navigate to backend directory
cd C:\Users\sdeep\OneDrive\Documents\PlatformIO\Projects\evm\django_backend

# Enable required services
gcloud services enable appengine.googleapis.com

# Create App Engine app
gcloud app create --region=us-central1

# Deploy the application
gcloud app deploy app_simple.yaml
```

### **Option 2: Cloud Run Deployment**
```bash
# Enable Cloud Run services
gcloud services enable run.googleapis.com cloudbuild.googleapis.com

# Build and deploy container
gcloud run deploy esp32-evm-backend \
    --source . \
    --region=us-central1 \
    --allow-unauthenticated \
    --port=8000
```

---

## 💰 **Free Tier Information**

### **Google Cloud Free Tier Includes:**
- **App Engine:** 28 frontend instance hours per day
- **Cloud Run:** 2 million requests per month
- **Cloud Storage:** 5 GB per month
- **Computing:** 1 GB network egress per month

### **Estimated Costs for ESP32 EVM:**
- **Development/Testing:** $0-5/month (within free tier)
- **Light Production Use:** $5-20/month
- **Heavy Production Use:** $20-100/month

---

## 🎯 **Alternative Deployment Options (No Billing Required)**

### **Option 1: Railway (Free Tier Available)**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### **Option 2: Render (Free Tier Available)**
1. Go to [Render.com](https://render.com)
2. Connect your GitHub repository
3. Create a new Web Service
4. Use Python runtime with build command: `pip install -r requirements.txt`
5. Start command: `gunicorn evm_backend.wsgi:application`

### **Option 3: PythonAnywhere (Free Tier Available)**
1. Go to [PythonAnywhere.com](https://pythonanywhere.com)
2. Upload your Django project
3. Configure WSGI file
4. Set up static files

### **Option 4: Heroku (Paid but Simple)**
```bash
# Install Heroku CLI
# Login and create app
heroku login
heroku create esp32-evm-backend

# Configure buildpack
heroku buildpacks:set heroku/python

# Deploy
git push heroku main
```

---

## 📝 **Prepared Files for Deployment**

Your project now includes:

✅ **`app_simple.yaml`** - Basic App Engine configuration  
✅ **`app.yaml`** - Full production App Engine configuration  
✅ **`requirements_production_fixed.txt`** - Production dependencies  
✅ **`settings_production.py`** - Production Django settings  
✅ **`Deploy-GCP.ps1`** - Automated PowerShell deployment script  
✅ **Static files collected** - Ready for deployment  

---

## 🔄 **Current Status**

### **Ready for Deployment:**
- ✅ Django backend configured for production
- ✅ Static files collected
- ✅ Database migrations applied
- ✅ Google Cloud SDK installed and authenticated
- ✅ Deployment scripts created

### **Pending:**
- ⏳ **Billing account setup** (required for GCP)
- ⏳ **App Engine application creation**
- ⏳ **Application deployment**

---

## ⚡ **Quick Commands After Billing Setup**

```bash
# Quick deployment sequence
cd C:\Users\sdeep\OneDrive\Documents\PlatformIO\Projects\evm\django_backend

# Create App Engine app
gcloud app create --region=us-central1

# Deploy
gcloud app deploy app_simple.yaml

# Your app will be available at:
# https://gen-lang-client-0176730707.appspot.com
```

### **Update ESP32 Configuration:**
```cpp
// config.h - Update after deployment
#define BACKEND_URL "https://gen-lang-client-0176730707.appspot.com"
```

---

## 🆘 **Next Steps**

1. **Enable billing** in Google Cloud Console
2. **Run deployment command** (takes ~5 minutes)
3. **Update ESP32 config.h** with new URL
4. **Test the complete system**

Your ESP32 EVM Django backend is **100% ready for deployment** - just needs billing enabled! 🚀

---

*Deployment prepared on: November 15, 2025*  
*Status: Ready for deployment (billing required)*  
*Estimated deployment time: 5 minutes after billing setup*