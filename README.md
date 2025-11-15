# Django Backend for Electronic Voting Machine

A Django-based backend that retrieves voting data from Firebase Realtime Database.

## Features

- 🔥 Firebase Realtime Database integration
- 📊 REST API endpoints for voting data
- 👥 Voter management
- 📈 Real-time voting statistics
- 🔒 Secure API with CORS support

## Prerequisites

- Python 3.8 or higher
- Firebase account with Realtime Database
- Firebase service account credentials

## Installation

### 1. Clone or navigate to the Backend folder

```bash
cd Backend
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**

```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to **Project Settings** → **Service Accounts**
4. Click **Generate New Private Key**
5. Save the downloaded JSON file as `firebase-credentials.json` in the Backend folder

### 6. Set up environment variables

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Firebase configuration:
   ```env
   FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com
   FIREBASE_CREDENTIALS_PATH=firebase-credentials.json
   ```

### 7. Run database migrations

```bash
python manage.py migrate
```

### 8. Start the development server

```bash
python manage.py runserver
```

The server will start at `http://127.0.0.1:8000/`

## API Endpoints

### Root

- `GET /` - API information and available endpoints

### Votes

- `GET /api/votes/` - Get all votes
- `GET /api/votes/<vote_id>/` - Get specific vote by ID
- `GET /api/votes/station/<station_id>/` - Get all votes from a specific station

### Voters

- `GET /api/voters/` - Get all enrolled voters
- `GET /api/voters/<fingerprint_id>/` - Get voter by fingerprint ID

### Statistics

- `GET /api/statistics/` - Get voting statistics

## API Response Format

### Success Response

```json
{
  "success": true,
  "count": 10,
  "data": [...]
}
```

### Error Response

```json
{
  "error": "Error message"
}
```

## Example API Calls

### Get all votes

```bash
curl http://127.0.0.1:8000/api/votes/
```

### Get voter status

```bash
curl http://127.0.0.1:8000/api/voters/1/
```

### Get statistics

```bash
curl http://127.0.0.1:8000/api/statistics/
```

## Firebase Database Structure

The backend expects the following structure in Firebase Realtime Database:

```
{
  "votes": {
    "vote_id_1": {
      "fingerprintId": 1,
      "stationId": "ESP32_001",
      "timestamp": "2024-01-15T10:30:00",
      "candidate": "Candidate A"
    }
  },
  "voters": {
    "voter_id_1": {
      "fingerprintId": 1,
      "name": "John Doe",
      "hasVoted": true,
      "enrolledAt": "2024-01-10T09:00:00"
    }
  }
}
```

## Configuration Files

- `settings.py` - Django settings and configuration
- `urls.py` - URL routing
- `views.py` - API endpoint handlers
- `firebase_service.py` - Firebase Realtime Database service
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (create from `.env.example`)

## Troubleshooting

### Firebase not initialized

- Ensure `firebase-credentials.json` exists in the Backend folder
- Check that `FIREBASE_DATABASE_URL` is set correctly in `.env`

### Import errors

- Make sure you've installed all dependencies: `pip install -r requirements.txt`
- Activate your virtual environment

### Port already in use

- Run on a different port: `python manage.py runserver 8080`

## Development

### Running with auto-reload

The Django development server automatically reloads when you make changes to the code.

### Creating a superuser (for admin panel)

```bash
python manage.py createsuperuser
```

Access admin panel at: `http://127.0.0.1:8000/admin/`

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Add your domain to `ALLOWED_HOSTS` in `.env`
3. Use a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn wsgi:application
   ```

## Project Structure

```
Backend/
├── manage.py              # Django management script
├── settings.py            # Django settings
├── urls.py                # URL configuration
├── views.py               # API views
├── wsgi.py                # WSGI configuration
├── firebase_service.py    # Firebase integration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .env                  # Your environment variables (create this)
├── firebase-credentials.json  # Firebase credentials (add this)
└── README.md             # This file
```

## License

MIT License
