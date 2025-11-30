# Deploy Django Backend to Google Cloud Platform (GCP)

This guide will help you deploy the EVM Django backend to Google Cloud Platform for stable, always-available access from your ESP32.

## Prerequisites

1. **Google Cloud Account**: Sign up at [cloud.google.com](https://cloud.google.com)
2. **Google Cloud SDK**: Install from [cloud.google.com/sdk](https://cloud.google.com/sdk)
3. **Firebase Project**: Make sure your Firebase project is active

## Quick Deployment

### Option 1: Automated Script (Recommended)
```powershell
# Run the automated deployment script
.\deploy_to_gcp.ps1
```

### Option 2: Manual Deployment

1. **Install Google Cloud SDK**
   ```bash
   # After installation, authenticate
   gcloud auth login
   ```

2. **Create and Set Project**
   ```bash
   # Create new project (choose unique ID)
   gcloud projects create fingerprint-evm-backend-YOUR-ID
   
   # Set active project
   gcloud config set project fingerprint-evm-backend-YOUR-ID
   ```

3. **Enable Required APIs**
   ```bash
   gcloud services enable appengine.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

4. **Create App Engine Application**
   ```bash
   gcloud app create
   # Choose region (us-central recommended)
   ```

5. **Prepare Django for Production**
   ```bash
   # Collect static files
   python manage.py collectstatic --noinput
   ```

6. **Deploy to App Engine**
   ```bash
   gcloud app deploy
   ```

## Files Created for Deployment

- `app.yaml`: App Engine configuration
- `main.py`: WSGI entry point for App Engine
- `.gcloudignore`: Files to exclude from deployment
- `deploy_to_gcp.ps1`: Automated deployment script

## After Deployment

1. **Get Your App URL**
   ```bash
   gcloud app browse
   ```

2. **Update ESP32 Configuration**
   Update `include/config.h`:
   ```cpp
   #define BACKEND_URL "https://YOUR-PROJECT-ID.appspot.com"
   ```

3. **Upload New Firmware**
   ```bash
   platformio run --target upload
   ```

## Monitoring and Management

- **View Logs**: `gcloud app logs tail -s default`
- **Open App**: `gcloud app browse`
- **App Engine Console**: [console.cloud.google.com/appengine](https://console.cloud.google.com/appengine)

## API Endpoints

Once deployed, your ESP32 can access:
- `GET https://YOUR-PROJECT-ID.appspot.com/` - API info
- `POST https://YOUR-PROJECT-ID.appspot.com/api/fingerprints/enroll/` - Enroll fingerprint
- `POST https://YOUR-PROJECT-ID.appspot.com/api/verification/verify/` - Verify fingerprint

## Troubleshooting

### Common Issues:

1. **Project ID already exists**: Use a unique project ID
2. **Billing not enabled**: Enable billing in GCP Console
3. **API not enabled**: Run the enable services commands
4. **Authentication failed**: Run `gcloud auth login`

### Check Deployment Status:
```bash
gcloud app versions list
gcloud app logs tail -s default
```

## Cost Estimation

Google App Engine Standard has a free tier that includes:
- 28 frontend instance hours per day
- 1GB outbound data per day

This should be sufficient for ESP32 testing. Monitor usage in the GCP Console.

## Security Notes

- Firebase credentials are securely stored in App Engine
- HTTPS is automatically enabled
- CORS is configured for API access
- Debug mode is disabled in production

## Need Help?

1. Check GCP Console for error details
2. View application logs: `gcloud app logs tail`
3. Verify Firebase configuration
4. Test endpoints with curl or Postman

Your Django backend will be accessible 24/7 from anywhere with a stable HTTPS URL!