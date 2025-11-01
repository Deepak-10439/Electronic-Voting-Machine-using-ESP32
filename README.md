# Electronic Voting Machine (EVM) using ESP32

A modular fingerprint-based Electronic Voting Machine system built with ESP32, featuring separate modes for enrollment, deletion, and verification.

## 📁 Project Structure

```
Electronic-Voting-Machine-using-ESP32/
├── include/
│   ├── Config.h                 # ⚙️ MAIN CONFIGURATION FILE
│   ├── FingerPrintManager.h     # Fingerprint sensor management
│   ├── LCDManager.h             # LCD display management
│   └── BuzzerManager.h          # Buzzer/sound management
├── src/
│   ├── main.cpp                 # Main controller (DO NOT EDIT)
│   ├── FingerPrintManager.cpp   # Fingerprint implementation
│   ├── LCDManager.cpp           # LCD implementation
│   ├── BuzzerManager.cpp        # Buzzer implementation
│   ├── VerifyMode.cpp           # Verification/Voting mode
│   ├── EnrollMode.cpp           # Enrollment mode
│   └── DeleteMode.cpp           # Deletion mode
├── platformio.ini               # PlatformIO configuration
└── README.md                    # This file
```

## 🚀 Quick Start Guide

### Step 1: Select Operation Mode

Open `include/Config.h` and uncomment **ONLY ONE** mode:

```cpp
// For Voting/Verification
#define MODE_VERIFY

// For Enrolling new fingerprints
// #define MODE_ENROLL

// For Deleting fingerprints
// #define MODE_DELETE
```

### Step 2: Configure Settings (Optional)

In `Config.h`, adjust settings based on your selected mode:

#### For VERIFY Mode:
```cpp
#define VERIFY_CONFIDENCE_THRESHOLD 50  // Minimum confidence (0-255)
```

#### For ENROLL Mode:
```cpp
#define ENROLL_START_ID 1        // Starting ID
#define ENROLL_COUNT 10          // Number to enroll
#define ENROLL_MANUAL false      // true = manual ID entry
```

#### For DELETE Mode:
```cpp
#define DELETE_ID 1              // ID to delete
#define DELETE_MANUAL true       // true = manual ID entry
#define DELETE_ALL false         // true = delete all fingerprints
```

### Step 3: Upload to ESP32

```bash
# Using PlatformIO
pio run --target upload

# Or use the VS Code PlatformIO extension
```

## 📋 Operation Modes

### 🔍 VERIFY Mode (Voting/Authentication)
- **Purpose**: Verify registered fingerprints for voting or authentication
- **Features**:
  - Continuous fingerprint scanning
  - Displays matched ID and confidence score
  - Success/error feedback via buzzer and LCD
  - Confidence threshold filtering

**Usage**:
1. Set `#define MODE_VERIFY` in Config.h
2. Upload code
3. Place finger on sensor
4. System shows ID and confidence if match found

---

### ➕ ENROLL Mode (Registration)
- **Purpose**: Register new fingerprints
- **Features**:
  - Auto-enrollment: Sequentially enroll multiple IDs
  - Manual enrollment: Enter specific IDs via Serial Monitor
  - Two-scan verification for accuracy
  - Progress tracking on LCD

**Auto Enrollment**:
```cpp
#define ENROLL_MANUAL false
#define ENROLL_START_ID 1
#define ENROLL_COUNT 10    // Enrolls ID 1-10
```

**Manual Enrollment**:
```cpp
#define ENROLL_MANUAL true
// Enter ID via Serial Monitor when prompted
```

**Process**:
1. System prompts for finger
2. Place finger → Remove finger
3. Place same finger again
4. Fingerprint saved!

---

### 🗑️ DELETE Mode (Remove Fingerprints)
- **Purpose**: Delete registered fingerprints
- **Features**:
  - Delete specific ID
  - Delete all fingerprints
  - Manual ID entry via Serial Monitor

**Delete Specific ID**:
```cpp
#define DELETE_MANUAL false
#define DELETE_ID 5        // Deletes ID #5
```

**Delete via Serial Monitor**:
```cpp
#define DELETE_MANUAL true
// Enter ID when prompted
```

**Delete All Fingerprints**:
```cpp
#define DELETE_ALL true    // ⚠️ Erases all stored fingerprints
```

---

## 🔧 Hardware Configuration

### Pin Connections

| Component | ESP32 Pin | Configuration |
|-----------|-----------|---------------|
| LCD (I2C) | SDA/SCL | Address: 0x27 |
| Fingerprint Sensor | Serial2 (RX=16, TX=17) | 57600 baud |
| Buzzer | GPIO 25 | Active High |

### Modify Hardware Settings

Edit `Config.h`:
```cpp
// LCD Configuration
#define LCD_ADDRESS 0x27       // Change I2C address if needed
#define LCD_COLS 16
#define LCD_ROWS 2

// Buzzer
#define BUZZER_PIN 25          // Change GPIO pin

// Fingerprint Sensor
#define FINGERPRINT_SERIAL Serial2
#define FINGERPRINT_BAUDRATE 57600
```

## 💡 Usage Examples

### Example 1: First-Time Setup (Enroll 5 Users)

1. Open `Config.h`:
```cpp
#define MODE_ENROLL
#define ENROLL_MANUAL false
#define ENROLL_START_ID 1
#define ENROLL_COUNT 5
```

2. Upload code
3. Follow LCD prompts to enroll 5 fingerprints (ID 1-5)

### Example 2: Run Voting System

1. Open `Config.h`:
```cpp
#define MODE_VERIFY
#define VERIFY_CONFIDENCE_THRESHOLD 50
```

2. Upload code
3. Place finger to vote/authenticate

### Example 3: Delete User ID 3

1. Open `Config.h`:
```cpp
#define MODE_DELETE
#define DELETE_MANUAL false
#define DELETE_ID 3
```

2. Upload code
3. ID #3 will be deleted automatically

### Example 4: Interactive Enrollment

1. Open `Config.h`:
```cpp
#define MODE_ENROLL
#define ENROLL_MANUAL true
```

2. Upload code
3. Open Serial Monitor (115200 baud)
4. Enter ID numbers when prompted

## 📊 Serial Monitor Commands

Set baud rate to **115200**.

### VERIFY Mode Output:
```
=== VERIFY MODE ===
Fingerprint Verification System Ready
Sensor contains 5 templates
Found ID #3 with confidence of 187
✓ Vote Registered!
```

### ENROLL Mode Output:
```
=== ENROLL MODE ===
Starting Enrollment for ID #1
Place finger...
Remove finger...
Place same finger again...
Successfully enrolled ID #1
```

### DELETE Mode Output:
```
=== DELETE MODE ===
Deleting ID #5
Successfully deleted!
```

## 🛠️ Troubleshooting

### "Did not find fingerprint sensor"
- Check Serial2 connections (RX/TX)
- Verify sensor power supply (3.3V or 5V)
- Check baud rate (57600)

### "No mode selected!" Error
- Open `Config.h`
- Uncomment exactly ONE mode definition
- Re-upload code

### LCD Not Displaying
- Verify I2C address (try 0x27 or 0x3F)
- Check SDA/SCL connections
- Run I2C scanner to find address

### Enrollment Fails
- Ensure finger is clean and dry
- Press firmly on sensor
- Use same finger position for both scans
- Avoid moving finger during scan

## 📝 Code Architecture

### Why This Structure?

✅ **No Code Commenting**: Switch modes in one file (Config.h)
✅ **Modular**: Each feature in separate files
✅ **Maintainable**: Easy to add new features
✅ **Clean**: No messy #ifdef in logic files
✅ **Safe**: Main.cpp doesn't need editing

### Class Responsibilities:

- **FingerPrintManager**: All fingerprint operations
- **LCDManager**: Display messages and UI
- **BuzzerManager**: Audio feedback
- **VerifyMode**: Verification logic
- **EnrollMode**: Enrollment logic
- **DeleteMode**: Deletion logic

## 🔐 Security Notes

- Store fingerprint IDs in database/EEPROM with voter info
- Implement one-vote-per-ID tracking
- Add timestamp logging
- Consider encryption for stored data

## 📚 Libraries Used

- **Adafruit Fingerprint Sensor Library** (v2.1.4+)
- **LiquidCrystal_I2C** (v1.1.4+)

## 🤝 Contributing

To add a new mode:
1. Create `NewMode.cpp` in `src/`
2. Define `newMode_setup()` and `newMode_loop()`
3. Add `#define MODE_NEW` in `Config.h`
4. Add mode handling in `main.cpp`

## 📄 License

BSD License - See Adafruit Fingerprint Sensor Library

## 🎯 Future Enhancements

- [ ] EEPROM storage for vote tracking
- [ ] WiFi connectivity for remote monitoring
- [ ] Multiple candidate selection
- [ ] Real-time results display
- [ ] Admin authentication mode
- [ ] Vote counting and reporting

---

**Made with ❤️ for secure and transparent voting systems**
