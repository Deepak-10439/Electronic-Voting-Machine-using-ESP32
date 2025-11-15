# 🚀 ESP32 Setup Guide for Blockchain-Enhanced EVM

## Quick Start Instructions

### 1. Hardware Setup
```
ESP32 Connections:
├── Fingerprint Sensor (AS608/R307)
│   ├── VCC → 3.3V or 5V
│   ├── GND → GND  
│   ├── TX → GPIO 16 (RX2)
│   └── RX → GPIO 17 (TX2)
├── LCD Display (16x2 I2C)
│   ├── VCC → 3.3V
│   ├── GND → GND
│   ├── SDA → GPIO 21
│   └── SCL → GPIO 22
└── Buzzer
    ├── Positive → GPIO 25
    └── Negative → GND
```

### 2. Upload Process (Multiple Options)

#### Option A: Using PlatformIO IDE (Recommended)
1. Install PlatformIO extension in VS Code
2. Open this project folder
3. Connect ESP32 via USB
4. Click "Upload" button (→) in PlatformIO toolbar
5. Monitor Serial output (📺) for status

#### Option B: Using Arduino IDE
1. Copy files from src/main.cpp to Arduino IDE
2. Install required libraries:
   - Adafruit Fingerprint Sensor Library
   - LiquidCrystal I2C
   - ArduinoJson
3. Set board to "ESP32 Dev Module"
4. Upload

#### Option C: Manual Upload with PlatformIO CLI
```bash
# If PlatformIO is installed globally:
platformio run --target upload

# If using local installation:
~/.platformio/penv/bin/platformio run --target upload
```

### 3. Testing ESP32 with Blockchain Backend

#### Serial Monitor Commands:
- **E** - Enter enrollment mode
- **V** - Enter verification mode  
- **S** - Show system status

#### Expected Workflow:
1. **Power On**: ESP32 connects to WiFi and backend
2. **Enrollment**: 
   - Send 'E' command
   - Place finger on sensor (twice)
   - Template uploaded to Firebase + blockchain transaction
3. **Verification**:
   - Send 'V' command  
   - Place finger on sensor
   - Backend verifies + blockchain audit trail

### 4. Monitoring Blockchain Activity

The monitoring script shows real-time updates:
```bash
python monitor_blockchain.py
```

**Monitor Output Sections:**
- 📊 Blockchain Status (blocks, validity, size)
- 📋 Recent Transactions (enrollments, verifications)
- 👆 Fingerprint Database Statistics
- 🔒 Blockchain Integrity Check

### 5. Configuration Verification

Check `include/config.h`:
```cpp
#define WIFI_SSID "YourWiFiName"         // ✅ Update this
#define WIFI_PASSWORD "YourPassword"      // ✅ Update this  
#define BACKEND_URL "https://swift-habitat-475216-n3.uc.r.appspot.com"  // ✅ Already set
```

### 6. Troubleshooting

#### WiFi Connection Issues:
- Verify SSID and password in config.h
- Check 2.4GHz network (ESP32 doesn't support 5GHz)
- Monitor Serial output for connection status

#### Fingerprint Sensor Issues:
- Verify wiring connections
- Check power supply (3.3V or 5V depending on sensor)
- Serial2 baud rate should be 57600

#### Backend Communication Issues:
- Verify internet connectivity
- Check if backend URL is accessible
- Monitor Serial output for HTTP response codes

#### Blockchain Issues:
- Backend automatically handles blockchain operations
- Monitor script shows real-time blockchain status
- Each enrollment/verification creates blockchain transaction

### 7. Success Indicators

#### ESP32 LCD Display:
```
Welcome to
Fingerprint EVM
├── WiFi Connected!
├── Firebase Ready!
└── Mode: IDLE Ready...
```

#### Serial Monitor Output:
```
=== Fingerprint System Ready ===
Commands:
  E - Enroll new fingerprint
  V - Verify fingerprint  
  S - Show status
================================
```

#### Blockchain Monitor:
```
✅ Backend is online!
📊 BLOCKCHAIN STATUS: Total Blocks: X
🔗 NEW TRANSACTION DETECTED!
```

### 8. Manual Testing Without Hardware

If ESP32 hardware is not immediately available, test the backend directly:

```python
# Test enrollment
python test_blockchain_integration.py

# Monitor blockchain  
python monitor_blockchain.py
```

### 9. Expected Blockchain Flow

1. **ESP32 Enrollment** → **Firebase Storage** → **Blockchain Transaction**
2. **ESP32 Verification** → **Backend Matching** → **Blockchain Audit**
3. **Monitor Shows** → **Real-time Updates** → **Transaction History**

### 10. Production Considerations

- Set appropriate WiFi credentials
- Consider security for production deployment
- Monitor blockchain integrity regularly
- Implement proper error handling
- Set up persistent storage for blockchain data

---

**🎯 Goal**: Demonstrate that ESP32 fingerprint operations (enrollment/verification) are automatically recorded in the blockchain for immutable audit trails, making the EVM tamper-proof and suitable for secure voting applications.