# ⚠️ IMPORTANT: Wrong Firebase Credentials Format

## Current Issue:

You've added the **Firebase Web Config** (for frontend JavaScript), but Django backend needs the **Firebase Admin SDK Service Account** credentials.

## How to Get the Correct Credentials:

### Step 1: Go to Firebase Console

1. Visit: https://console.firebase.google.com/
2. Select your project: **fingerprint-evm**

### Step 2: Navigate to Service Accounts

1. Click the ⚙️ **Settings** (gear icon)
2. Click **Project Settings**
3. Go to the **Service Accounts** tab

### Step 3: Generate Private Key

1. Look for "**Firebase Admin SDK**" section
2. Click **"Generate New Private Key"** button
3. Confirm by clicking **"Generate Key"**
4. A JSON file will be downloaded

### Step 4: Replace the File

1. The downloaded file will be named something like:
   `fingerprint-evm-firebase-adminsdk-xxxxx-xxxxxxxxxx.json`
2. Rename it to: `firebase-credentials.json`
3. Replace the existing file in: `d:\Minor Project 7th sem\Backend\`

## What the Correct File Should Look Like:

```json
{
  "type": "service_account",
  "project_id": "fingerprint-evm",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@fingerprint-evm.iam.gserviceaccount.com",
  "client_id": "123456789...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/..."
}
```

## Quick Test After Replacing:

```powershell
cd "d:\Minor Project 7th sem\Backend"
.\venv\Scripts\Activate.ps1
python check_firebase.py
```

If successful, you'll see:
✅ Valid JSON file
✅ Project ID: fingerprint-evm
✅ All required fields present

Then run: `python test_setup.py` to verify full setup!
