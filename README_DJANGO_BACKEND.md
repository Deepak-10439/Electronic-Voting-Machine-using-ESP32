# ESP32 Blockchain Voting System with Django Backend

## 🚀 System Overview

This is a secure Electronic Voting Machine (EVM) system built on ESP32 with Django REST API backend and blockchain integration. The system provides:

- **Biometric Authentication**: R307/R503 fingerprint sensor verification
- **Secure Backend**: Django REST API with token-based authentication
- **Blockchain Integration**: Ethereum/blockchain vote recording for immutability
- **Real-time Verification**: Vote verification and audit trails
- **Enterprise Security**: Rate limiting, CORS, audit logging

## 📁 Project Structure

```
evm/
├── django_backend/              # Django REST API Backend
│   ├── evm_backend/            # Django project settings
│   ├── voting/                 # Voting app with models, views, APIs
│   │   ├── models.py          # Voter, Election, Vote, AuditLog models
│   │   ├── views.py           # REST API endpoints
│   │   ├── serializers.py     # Data serialization
│   │   ├── blockchain.py      # Blockchain manager (Web3.py)
│   │   └── urls.py            # API URL routing
│   ├── requirements.txt        # Python dependencies
│   └── manage.py              # Django management script
├── src/
│   ├── main_backend.cpp       # New ESP32 main code (Django backend)
│   ├── main.cpp              # Original Firebase implementation
│   └── BackendManager.cpp    # Django API communication class
├── include/
│   ├── BackendManager.h      # Backend manager header
│   ├── FirebaseManager.h     # Original Firebase manager
│   └── config.h              # WiFi and backend configuration
└── platformio.ini            # PlatformIO project configuration
```

## 🔧 Hardware Requirements

| Component | Connection | Purpose |
|-----------|------------|---------|
| ESP32-D0WD | Main controller | WiFi, processing |
| R307/R503 Fingerprint Sensor | TX→GPIO17, RX→GPIO16 | Biometric authentication |
| 16x2 I2C LCD (0x27) | SDA→GPIO21, SCL→GPIO22 | User interface display |
| Buzzer | Positive→GPIO25 | Audio feedback |
| AUTH Button | GPIO26→GND | Authentication trigger |
| VOTE Button | GPIO27→GND | Voting trigger |

### Power Requirements
- ESP32: 3.3V/5V, ~240mA
- Fingerprint Sensor: 3.3V/5V, ~120mA
- LCD Display: 5V, ~20mA
- Total: ~380mA (5V recommended)

## 🌐 Backend Architecture

### Django REST API Endpoints

| Endpoint | Method | Purpose | Authentication |
|----------|--------|---------|---------------|
| `/api/health/` | GET | Health check | None |
| `/api/time/` | GET | System time sync | None |
| `/api/auth/` | POST | Voter authentication | None |
| `/api/register/` | POST | Voter registration | None |
| `/api/elections/` | GET | Active elections | Token |
| `/api/vote/` | POST | Cast vote | Token |
| `/api/verify/<vote_id>/` | GET | Verify vote | Token |
| `/api/results/<election_id>/` | GET | Election results | None |
| `/api/blockchain/status/` | GET | Blockchain status | Token |

### Database Models

#### Voter Model
```python
class Voter(AbstractUser):
    voter_id = UUIDField()
    fingerprint_template = BinaryField(max_length=534)
    aadhar_number = CharField(max_length=12)
    phone_number = CharField(max_length=10)
    blockchain_address = CharField(max_length=42)
    # ... other fields
```

#### Vote Model
```python
class Vote(Model):
    vote_id = UUIDField()
    voter = ForeignKey(Voter)
    election = ForeignKey(Election)
    candidate = ForeignKey(Candidate)
    blockchain_tx_hash = CharField(max_length=66)
    vote_status = CharField()  # PENDING, CONFIRMED, FAILED
    # ... other fields
```

## ⚙️ Installation & Setup

### 1. Django Backend Setup

```bash
# Navigate to backend directory
cd django_backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# Install dependencies
pip install django djangorestframework web3 psycopg2-binary django-cors-headers requests

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver 0.0.0.0:8000
```

### 2. ESP32 Setup

```cpp
// Update config.h with your settings
#define WIFI_SSID "YourWiFiName"
#define WIFI_PASSWORD "YourWiFiPassword"
#define BACKEND_URL "http://192.168.1.100:8000"  // Your server IP
#define ESP32_DEVICE_ID "ESP32_EVM_001"
```

### 3. Blockchain Setup (Optional)

```bash
# Install Ganache CLI for local blockchain
npm install -g ganache-cli

# Start local blockchain
ganache-cli --deterministic --accounts 10 --host 0.0.0.0

# Update Django settings with blockchain config
```

## 🔐 Security Features

### Backend Security
- **Token Authentication**: Django REST framework token auth
- **Rate Limiting**: API throttling (100/hour anonymous, 1000/hour authenticated)
- **CORS Protection**: Configurable cross-origin policies
- **Audit Logging**: Comprehensive activity tracking
- **Input Validation**: Serializer-based data validation

### Blockchain Security
- **Immutable Records**: Votes stored on blockchain
- **Hash Verification**: SHA256 vote and template hashing
- **Transaction Tracking**: Full blockchain audit trail
- **Smart Contract**: Vote validation and storage

### Hardware Security
- **Biometric Authentication**: 80%+ fingerprint matching
- **Template Encryption**: Secure fingerprint data handling
- **Device ID Tracking**: Hardware-specific identification

## 📊 API Usage Examples

### Authentication
```bash
curl -X POST http://server:8000/api/auth/ \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": "ESP32_EVM_001",
    "aadhar_number": "123456789012",
    "fingerprint_template": "00112233...aabbcc"
  }'
```

### Cast Vote
```bash
curl -X POST http://server:8000/api/vote/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token your_auth_token" \
  -d '{
    "election_id": "election-uuid",
    "candidate_id": "candidate-uuid",
    "device_id": "ESP32_EVM_001",
    "fingerprint_match_score": 0.95
  }'
```

### Verify Vote
```bash
curl -X GET http://server:8000/api/verify/vote-uuid/ \
  -H "Authorization: Token your_auth_token"
```

## 🎯 ESP32 Operation Modes

### 1. IDLE Mode
- System ready, waiting for user input
- Display shows current status
- LED shows "EVM Ready" or voter name if authenticated

### 2. AUTH Mode (Authentication)
- Triggered by AUTH button or 'A' command
- Captures fingerprint and sends to backend
- Displays authentication result
- Returns to IDLE on completion

### 3. VOTE Mode (Voting)
- Triggered by VOTE button or 'V' command (requires authentication)
- Downloads active elections from backend
- Shows candidate selection interface
- Casts vote and shows confirmation
- Logs out voter automatically

### 4. RESULTS Mode
- Triggered by 'R' command
- Downloads and displays election results
- Shows vote counts and percentages

## 📺 LCD Display Messages

| Message | Context | Duration |
|---------|---------|----------|
| "Starting EVM" | Boot sequence | 2s |
| "WiFi Connected!" | Network setup | 1.5s |
| "Backend Ready!" | API connection | 1.5s |
| "EVM Ready" | Idle mode | Continuous |
| "Place finger" | Authentication | Until finger detected |
| "AUTH Success!" | Successful auth | 2s |
| "Loading Elections" | Vote mode | 1s |
| "Vote Cast!" | Successful vote | 3s |

## 🔊 Audio Feedback

- **Success Sound**: Single long beep (500ms)
- **Error Sound**: Two short beeps (200ms + 100ms gap + 200ms)
- **Button Beep**: Short beep (100ms)

## 🚨 Error Handling

### Hardware Errors
- **Sensor Error**: "Sensor Error! Check connection"
- **WiFi Failed**: "WiFi Failed! Check credentials"
- **Backend Error**: "Backend Error! Check server"

### API Errors
- **Authentication Failed**: "AUTH Failed! Try again"
- **Vote Failed**: "Vote Failed! Try again"
- **Network Timeout**: "Network Error! Check connection"

## 📈 Performance Metrics

| Operation | Time | Memory |
|-----------|------|---------|
| Boot & Connect | ~15-20s | 45KB |
| Authentication | ~3-5s | 12KB |
| Vote Casting | ~5-8s | 15KB |
| Result Display | ~2-3s | 8KB |
| Blockchain Sync | ~10-15s | 20KB |

## 🔧 Configuration Options

### Backend URL Configuration
```cpp
// config.h
#define BACKEND_URL "http://192.168.1.100:8000"  // Development
// #define BACKEND_URL "https://evm-api.yourcompany.com"  // Production
```

### Fingerprint Matching Threshold
```cpp
// BackendManager.cpp
float MATCH_THRESHOLD = 0.8f;  // 80% similarity required
```

### API Timeout Settings
```cpp
// BackendManager.cpp
http.setTimeout(10000);  // 10 second timeout
```

## 🐛 Troubleshooting

### Common Issues

1. **WiFi Connection Failed**
   - Check SSID and password in config.h
   - Verify WiFi signal strength
   - Reset ESP32 and retry

2. **Backend Connection Error**
   - Verify backend server is running
   - Check IP address in BACKEND_URL
   - Test with curl or browser

3. **Authentication Failed**
   - Ensure voter is registered in database
   - Check fingerprint sensor connections
   - Verify Aadhar number matches

4. **Vote Casting Failed**
   - Ensure voter is authenticated
   - Check active elections exist
   - Verify candidate selection

### Debug Commands

```
Serial Monitor Commands:
- STATUS or S: Show system status
- AUTH or A: Enter authentication mode
- VOTE or V: Enter voting mode (requires auth)
- RESULTS or R: Show election results
- LOGOUT or L: Logout current voter
```

### Log Analysis

```bash
# Django backend logs
tail -f evm_backend.log

# Monitor API requests
python manage.py runserver --verbosity=2

# Database inspection
python manage.py shell
>>> from voting.models import *
>>> Vote.objects.count()
>>> AuditLog.objects.filter(log_type='VOTE_CAST')
```

## 🚀 Production Deployment

### Backend Deployment
1. **Use PostgreSQL**: Replace SQLite with PostgreSQL
2. **Configure HTTPS**: Use SSL certificates
3. **Set Secret Key**: Generate secure Django SECRET_KEY
4. **Configure CORS**: Restrict to specific ESP32 IPs
5. **Enable Logging**: Configure production logging
6. **Backup Strategy**: Regular database backups

### Blockchain Deployment
1. **Mainnet Setup**: Deploy to Ethereum mainnet or testnet
2. **Smart Contract**: Deploy voting smart contract
3. **Gas Optimization**: Configure gas prices
4. **Private Key**: Secure storage of blockchain keys

### Hardware Deployment
1. **Secure Enclosure**: Tamper-proof housing
2. **Power Backup**: UPS for continuous operation
3. **Network Security**: VPN or secure WiFi
4. **Physical Security**: Anti-tampering measures

## 📄 License

This project is provided for educational and personal use. For commercial use, please ensure compliance with local election laws and regulations.

## 👥 Support

For issues or questions:
1. Check the troubleshooting section
2. Review ESP32 serial output at 115200 baud
3. Verify Django backend logs
4. Test API endpoints manually with curl

---

**⚠️ Important Security Note**: This is a demonstration system. For actual election use, additional security measures, certifications, and compliance with election commission requirements are necessary.