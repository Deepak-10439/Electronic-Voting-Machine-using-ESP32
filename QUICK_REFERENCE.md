# 🚀 Quick Reference - EVM Django Backend

## Setup (First Time Only)
```powershell
cd "d:\Minor Project 7th sem\Backend"
.\setup.ps1
# OR manually:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

## Configuration
1. Add `firebase-credentials.json` to Backend folder
2. Edit `.env` and set `FIREBASE_DATABASE_URL`

## Run Server
```powershell
cd "d:\Minor Project 7th sem\Backend"
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

## Test Setup
```powershell
python test_setup.py
```

## API Endpoints (http://127.0.0.1:8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/api/votes/` | All votes |
| GET | `/api/votes/{id}/` | Specific vote |
| GET | `/api/votes/station/{id}/` | Votes by station |
| GET | `/api/voters/` | All voters |
| GET | `/api/voters/{id}/` | Voter by fingerprint ID |
| GET | `/api/statistics/` | Vote statistics |

## Test in Browser
- Visit: http://127.0.0.1:8000
- Try: http://127.0.0.1:8000/api/votes/

## Test with PowerShell
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/statistics/" -Method Get
```

## Common Issues

**Import errors?**
→ Activate venv: `.\venv\Scripts\Activate.ps1`

**Firebase not initialized?**
→ Check firebase-credentials.json exists
→ Verify FIREBASE_DATABASE_URL in .env

**Port 8000 in use?**
→ Run on different port: `python manage.py runserver 8080`

## Files You Need to Add
- ✓ `firebase-credentials.json` (from Firebase Console)
- ✓ `.env` (copy from .env.example)

## Files Already Created
- ✓ settings.py - Django config
- ✓ urls.py - URL routing
- ✓ views.py - API handlers
- ✓ firebase_service.py - Firebase integration
- ✓ requirements.txt - Dependencies
- ✓ manage.py - Django management
- ✓ README.md - Full documentation
