# 🗳️ EVM Voting System Guide

## Overview
The ESP32 Electronic Voting Machine has been converted from a fingerprint verification system to a complete voting system with backend and blockchain integration.

## 🔧 Key Changes Made

### ✅ Removed Components
- ❌ Firebase/IFTTT integration
- ❌ Cloud verification system
- ❌ Complex backend template storage

### ✅ Added Components
- ✅ **Voting Interface** - 3 candidate options (USAR, USAP, USDI)
- ✅ **Backend API Integration** - Votes stored in Django backend
- ✅ **Blockchain Integration** - Votes recorded on blockchain
- ✅ **Serial Monitor Voting** - No hardware buttons needed

---

## 🔄 System Flow

```
1. Power On → WiFi Connect → System Ready
2. Press 'V' → Voting Mode Activated
3. Place Finger → Fingerprint Verification
4. If Verified → Show Voting Options
5. Enter Choice (1/2/3) in Serial Monitor
6. Vote Submitted → Backend API + Blockchain API
7. Success Confirmation → Return to Idle
```

---

## 📋 Serial Commands

| Command | Function | Description |
|---------|----------|-------------|
| `E` | **Enroll** | Register new voter fingerprint |
| `V` | **Vote** | Start voting process |
| `S` | **Status** | Show system information |

---

## 🎯 Voting Options

When fingerprint is verified, you'll see:

```
Select your candidate:
1. USAR
2. USAP  
3. USDI
Enter choice: 
```

**Enter `1`, `2`, or `3` in Serial Monitor**

---

## 🌐 API Integration

### 🏢 Backend API Call
```http
POST http://<BACKEND_URL>/vote
Content-Type: application/json

{
  "voterId": 5,
  "candidate": "USAR"
}
```

### 🔗 Blockchain API Call
```http
POST http://<BLOCKCHAIN_URL>/addVote
Content-Type: application/json

{
  "voterId": 5,
  "candidate": "USAR"
}
```

---

## ⚙️ Configuration

### Update `config.h`:

```cpp
// WiFi Credentials
#define WIFI_SSID "YourWiFi"
#define WIFI_PASSWORD "YourPassword"

// Backend Configuration
#define BACKEND_URL "https://your-backend-url.com"

// Blockchain Configuration  
#define BLOCKCHAIN_URL "https://your-blockchain-endpoint.com"
```

---

## 🖥️ LCD Display States

| State | Line 1 | Line 2 |
|-------|--------|--------|
| **Ready** | `Mode: IDLE` | `Ready...` |
| **Voting** | `Place finger` | `to vote...` |
| **Verified** | `VERIFIED!` | `Voter ID: #5` |
| **Selection** | `Select candidate:` | `1=USAR 2=USAP 3=USDI` |
| **Processing** | `Processing...` | `Please wait` |
| **Success** | `VOTE RECORDED!` | `ID:5 -> USAR` |
| **Error** | `NOT VERIFIED` | `Access Denied` |

---

## 🔊 Audio Feedback

- **Success Beep**: Long beep (500ms) - Vote recorded
- **Error Beep**: Double beep (300ms x2) - Verification failed/Error

---

## 📊 Serial Monitor Output

### ✅ Successful Vote:
```
╔══════════════════════════════╗
║      VOTE CONFIRMATION       ║
╠══════════════════════════════╣
║   Voter ID: #5               ║
║   Candidate: USAR            ║
║   Backend: ✓                 ║
║   Blockchain: ✓              ║
╚══════════════════════════════╝
```

### ❌ Failed Verification:
```
╔══════════════════════════════╗
║   VERIFICATION FAILED!       ║
╠══════════════════════════════╣
║   Status: UNAUTHORIZED       ║
║   Cannot Vote                ║
╚══════════════════════════════╝
```

---

## 🔍 Troubleshooting

### WiFi Issues
- **Problem**: `WiFi Failed!` on LCD
- **Solution**: Check SSID/Password in `config.h`

### Backend Issues  
- **Problem**: `Backend Error! Vote Failed`
- **Solution**: Verify `BACKEND_URL` is correct and server is running

### Blockchain Issues
- **Problem**: `Partial Success Backend OK`
- **Solution**: Check `BLOCKCHAIN_URL` and endpoint availability

### Fingerprint Issues
- **Problem**: `NOT VERIFIED Access Denied`
- **Solution**: Re-enroll fingerprint using 'E' command

---

## 📱 Backend Requirements

Your Django backend must handle:

### Vote Endpoint:
```python
@api_view(['POST'])
def vote(request):
    voter_id = request.data.get('voterId')
    candidate = request.data.get('candidate')
    
    # Process vote
    # Return success/failure
```

### Blockchain Endpoint:
```python
@api_view(['POST'])  
def add_vote(request):
    voter_id = request.data.get('voterId')
    candidate = request.data.get('candidate')
    
    # Record on blockchain
    # Return success/failure
```

---

## 🔒 Security Features

- ✅ **Fingerprint Authentication** - Only enrolled users can vote
- ✅ **Dual Storage** - Backend database + Blockchain
- ✅ **Local Verification** - Fast fingerprint matching
- ✅ **Audit Trail** - All votes tracked with voter ID
- ✅ **Tamper Resistant** - Blockchain immutability

---

## 🎮 Usage Example

1. **Power on ESP32**
2. **Open Serial Monitor** (115200 baud)
3. **Wait for "EVM System Ready"**
4. **Type 'V'** to start voting
5. **Place finger** on sensor
6. **Wait for verification**
7. **Type choice** (1, 2, or 3)
8. **Confirmation** displayed
9. **Return to idle**

---

## 📝 Notes

- **No Hardware Buttons**: All input via Serial Monitor
- **Local Storage**: Fingerprints stored on R307 sensor
- **Dual APIs**: Backend + Blockchain for redundancy
- **Real-time Feedback**: LCD + Serial Monitor updates
- **Error Handling**: Graceful failure with clear messages

---

## 🏆 Success Indicators

- ✅ WiFi connected
- ✅ Fingerprint verified  
- ✅ Backend API call successful (200/201)
- ✅ Blockchain API call successful (200/201)
- ✅ Vote recorded confirmation
- ✅ System returns to idle mode

Your EVM system is now ready for secure, authenticated voting! 🗳️✨