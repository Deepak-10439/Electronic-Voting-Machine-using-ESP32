# Fingerprint Authentication System with Firebase

This system provides fingerprint enrollment and verification using Firebase Realtime Database for template storage.

## Features

- **Enrollment Mode**: Captures fingerprints and uploads templates to Firebase
- **Verification Mode**: Downloads templates from Firebase and verifies locally
- **Supports up to 100 fingerprints** for verification
- **LCD display** for user feedback
- **Audio feedback** via buzzer
- **WiFi connectivity** for Firebase communication

## Hardware Requirements

- ESP32 Development Board
- R307/R503 Fingerprint Sensor
- 16x2 I2C LCD Display (0x27 address)
- Buzzer (GPIO 25)
- 2x Push Buttons:
  - Enroll Button (GPIO 26)
  - Verify Button (GPIO 27)

## Wiring Connections

### Fingerprint Sensor (R307/R503)
- VCC → 3.3V/5V
- GND → GND
- TX → GPIO 17 (RX2)
- RX → GPIO 16 (TX2)

### LCD Display (I2C)
- VCC → 5V
- GND → GND
- SDA → GPIO 21
- SCL → GPIO 22

### Buttons
- Enroll Button → GPIO 26 to GND (with internal pull-up)
- Verify Button → GPIO 27 to GND (with internal pull-up)

### Buzzer
- Positive → GPIO 25
- Negative → GND

## Firebase Setup

### 1. Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select existing one
3. Enable **Realtime Database**

### 2. Get Database URL
1. In Firebase Console, go to **Realtime Database**
2. Copy your database URL (e.g., `https://your-project.firebaseio.com` or `https://your-project.asia-southeast1.firebasedatabase.app`)

### 3. Get Authentication Secret (Optional but recommended)
1. Go to **Project Settings** → **Service Accounts**
2. Click on **Database Secrets** tab
3. Copy the secret (or leave `FIREBASE_AUTH` empty for testing without authentication)

### 4. Configure Database Rules
Set your Firebase Realtime Database rules:

```json
{
  "rules": {
    "fingerprints": {
      ".read": true,
      ".write": true
    }
  }
}
```

**Note**: For production, implement proper authentication rules.

## Configuration

Edit `include/config.h`:

```cpp
// WiFi Credentials
#define WIFI_SSID "Your_WiFi_SSID"
#define WIFI_PASSWORD "Your_WiFi_Password"

// Firebase Configuration
#define FIREBASE_AUTH ""  // Your Database Secret or leave empty
#define DATABASE_URL "https://your-project-id.firebaseio.com"
```

## How to Use

### Initial Setup
1. Upload the code to your ESP32
2. Open Serial Monitor (115200 baud)
3. Wait for WiFi and Firebase connection
4. System will display the number of templates in Firebase and local storage

### Enrolling a Fingerprint

1. **Press the Enroll Button** (GPIO 26)
2. LCD will display "Mode: ENROLL"
3. **Place your finger** on the sensor when prompted
4. **Remove finger** when instructed
5. **Place the same finger again** to confirm
6. System will:
   - Create the fingerprint template
   - Store it locally (backup)
   - Upload to Firebase
7. LCD shows "Enrolled! ID: X" on success
8. System returns to IDLE mode

### Verifying a Fingerprint

1. **Press the Verify Button** (GPIO 27)
2. LCD will display "Mode: VERIFY"
3. **Place your finger** on the sensor
4. System will:
   - Capture the fingerprint
   - Download up to 100 templates from Firebase
   - Compare with each template
5. LCD shows:
   - "Match Found! ID: X" if fingerprint matches
   - "No Match Found!" if no match
6. System returns to IDLE mode

## Firebase Data Structure

Templates are stored in Firebase as:

```
/fingerprints/
  ├── template_1/
  │   ├── data: "hex,string,data..."
  │   ├── id: 1
  │   └── size: 534
  ├── template_2/
  │   ├── data: "hex,string,data..."
  │   ├── id: 2
  │   └── size: 534
  └── count: 2
```

## Troubleshooting

### WiFi Connection Issues
- Verify SSID and password in `config.h`
- Check WiFi signal strength
- Ensure 2.4GHz WiFi (ESP32 doesn't support 5GHz)

### Firebase Connection Issues
- Verify DATABASE_URL is correct
- Check Firebase database rules allow read/write
- Ensure device has internet access

### Fingerprint Sensor Issues
- Verify wiring connections
- Check sensor power (3.3V or 5V depending on model)
- Ensure Serial2 is properly initialized

### No Match During Verification
- Ensure fingerprints are enrolled properly
- Try enrolling the same finger multiple times
- Clean the fingerprint sensor
- Press finger firmly but not too hard

## System Behavior

### Buzzer Patterns
- **Success** (1 long beep): Enrollment/verification successful
- **Error** (2 short beeps): Operation failed

### LED Display Messages
- "Mode: IDLE" - Waiting for button press
- "Mode: ENROLL" - Ready to enroll fingerprint
- "Mode: VERIFY" - Ready to verify fingerprint
- "WiFi Connected!" - Successfully connected to WiFi
- "Firebase Ready!" - Firebase initialized
- "Uploading to Firebase..." - Uploading template
- "Verifying with Firebase..." - Downloading and verifying

## Performance

- **Enrollment time**: ~5-8 seconds (including Firebase upload)
- **Verification time**: ~10-30 seconds (depends on number of templates)
- **Maximum templates**: 100 (configurable in code)
- **Template size**: ~534 bytes per fingerprint

## Security Considerations

1. **Use Firebase Authentication**: Don't leave FIREBASE_AUTH empty in production
2. **Implement proper database rules**: Restrict read/write access
3. **Encrypt sensitive data**: Consider encrypting fingerprint templates
4. **Use HTTPS**: Firebase automatically uses HTTPS
5. **Regular backups**: Keep local copies of templates

## Code Structure

- `main.cpp` - Main program logic with button handling and mode control
- `FirebaseManager.h` - Firebase operations (upload/download/verify)
- `config.h` - WiFi and Firebase configuration

## Future Enhancements

- Add user authentication before enrollment
- Implement template encryption
- Add cloud backup/restore functionality
- Support for more than 100 templates
- Web interface for management
- Add fingerprint deletion capability

## License

This project is provided as-is for educational and personal use.

## Support

For issues or questions, please check:
1. Serial Monitor output for debugging information
2. Firebase Console for data verification
3. Ensure all hardware connections are correct
