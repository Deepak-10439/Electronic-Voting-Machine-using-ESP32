# EVM Backend Integration - Updated System

## 🔄 System Architecture

The system now uses a **3-tier architecture**:

```
ESP32 Fingerprint System ➜ Django Backend ➜ Firebase Realtime DB
```

### Benefits:
- ✅ **Centralized Logic**: All fingerprint processing in Django backend
- ✅ **Better Security**: ESP32 doesn't need direct Firebase credentials
- ✅ **Scalability**: Multiple ESP32 devices can use same backend
- ✅ **Monitoring**: Backend logs all enrollment and verification attempts
- ✅ **API Access**: Web/mobile apps can use the same backend

## 🚀 Quick Start

### 1. Start the Django Backend

```bash
# Install dependencies (first time only)
python setup.py

# Start the backend server
python start_backend.py
```

The backend will be available at `http://YOUR_IP:8000`

### 2. Update ESP32 Configuration

Edit `include/config.h` and set your backend URL:

```cpp
#define BACKEND_URL "http://192.168.1.100:8000"  // Your computer's IP
```

### 3. Upload and Run ESP32 Code

```bash
pio run --target upload
pio device monitor --port COM7 --baud 115200
```

## 📡 How It Works

### Enrollment Process:
1. **ESP32** captures fingerprint and converts to template
2. **ESP32** sends template data to Django backend via HTTP POST
3. **Django Backend** receives data and stores in Firebase
4. **ESP32** receives confirmation

### Verification Process:
1. **ESP32** captures fingerprint and converts to template  
2. **ESP32** sends template to Django backend for verification
3. **Django Backend** compares with all stored templates in Firebase
4. **Django Backend** sends match result (ID) back to ESP32
5. **ESP32** displays result on LCD and Serial Monitor

## 🔧 API Endpoints

### For ESP32:
- `POST /api/fingerprints/enroll/` - Enroll new fingerprint
- `POST /api/verification/verify/` - Verify fingerprint

### For Monitoring:
- `GET /api/fingerprints/` - Get all enrolled fingerprints
- `GET /api/fingerprints/count/` - Get count of enrolled fingerprints
- `GET /api/statistics/` - Get system statistics

## 🌐 Network Setup

### Find Your Computer's IP Address:

**Windows:**
```cmd
ipconfig
```

**macOS/Linux:**
```bash
ifconfig
```

### Update ESP32 Config:
Replace `192.168.1.100` in `config.h` with your actual IP address.

### Firewall:
Make sure port 8000 is open on your computer's firewall.

## 📱 Testing the System

### 1. Test Backend Connectivity:
```bash
curl http://YOUR_IP:8000/
```

### 2. Test Enrollment API:
```bash
curl -X POST http://YOUR_IP:8000/api/fingerprints/enroll/ \
  -H "Content-Type: application/json" \
  -d '{"id": 999, "data": "test,data", "size": 100}'
```

### 3. Monitor ESP32 Serial Output:
The ESP32 will show detailed logs of backend communication.

## 🔍 Troubleshooting

### ESP32 Can't Connect to Backend:
1. Check if backend is running: `http://YOUR_IP:8000`
2. Verify IP address in `config.h`
3. Check WiFi connectivity
4. Verify firewall settings

### Backend Can't Connect to Firebase:
1. Check `firebase-credentials.json` file exists
2. Verify Firebase configuration in `settings.py`
3. Check Firebase rules allow read/write access

### Slow Response Times:
1. Use local network (same WiFi)
2. Reduce verification threshold if needed
3. Check network latency

## 📊 Monitoring

### View Real-time Logs:
- **Django Backend**: Shows all API requests and Firebase operations
- **ESP32 Serial**: Shows enrollment/verification status
- **Firebase Console**: Shows data being stored

### API Statistics:
Visit `http://YOUR_IP:8000/api/statistics/` for system stats.

## 🔐 Security Notes

- Backend validates all input data
- Firebase credentials are secured on backend only
- ESP32 uses simple HTTP API calls
- Templates are encrypted during transmission

## 🆕 What Changed

### ESP32 Code Changes:
- New `FirebaseManager.h` with HTTP client integration
- Added ArduinoJson library for JSON handling
- Removed direct Firebase SDK dependency
- Added backend URL configuration

### Backend Features:
- New enrollment endpoint for ESP32
- New verification endpoint for ESP32  
- Enhanced error handling and validation
- Detailed logging and monitoring

### Benefits of New Architecture:
- **Easier Setup**: No Firebase SDK complexity on ESP32
- **Better Debugging**: Centralized logs in Django
- **More Flexible**: Easy to add new features
- **Production Ready**: Scalable backend architecture

## 🎯 Next Steps

1. **Web Interface**: Add a web dashboard for enrollment management
2. **Mobile App**: Create mobile app using the same backend APIs
3. **Multi-Device**: Connect multiple ESP32 devices to same backend
4. **Analytics**: Add detailed usage analytics and reporting
5. **Security**: Add authentication and authorization to backend APIs