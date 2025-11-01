# 🔧 Troubleshooting Guide

## Common Issues and Solutions

---

## ❌ Issue: "No mode selected!" Error on LCD

**Problem**: No operation mode is defined in Config.h

**Solution**:
1. Open `include/Config.h`
2. Find the mode definitions section
3. Uncomment **exactly ONE** mode:
   ```cpp
   #define MODE_VERIFY     // ✓ Remove // from ONE line
   // #define MODE_ENROLL  // Keep // on the others
   // #define MODE_DELETE
   ```
4. Save and re-upload

---

## ❌ Issue: "Did not find fingerprint sensor"

**Problem**: ESP32 cannot communicate with fingerprint sensor

**Possible Causes**:

### 1. Incorrect Wiring
**Check**:
- Fingerprint sensor TX → ESP32 RX (GPIO 16)
- Fingerprint sensor RX → ESP32 TX (GPIO 17)
- VCC → 3.3V or 5V (check sensor specs)
- GND → GND

### 2. Wrong Serial Port
**Solution**: Edit `Config.h`
```cpp
#define FINGERPRINT_SERIAL Serial2  // Try Serial1 or Serial
```

### 3. Wrong Baud Rate
**Solution**: Edit `Config.h`
```cpp
#define FINGERPRINT_BAUDRATE 57600  // Try 9600 or 115200
```

### 4. Power Issues
**Check**:
- Sensor LED is on?
- Use external 5V power if needed
- Check voltage requirements

---

## ❌ Issue: LCD Shows Nothing / Blank Screen

**Problem**: LCD not communicating via I2C

### Solution 1: Check I2C Address
Most common addresses are `0x27` or `0x3F`

**Edit Config.h**:
```cpp
#define LCD_ADDRESS 0x3F  // Try different address
```

### Solution 2: Run I2C Scanner
Upload this code temporarily:
```cpp
#include <Wire.h>
void setup() {
  Wire.begin();
  Serial.begin(115200);
  Serial.println("Scanning I2C...");
  for(byte i = 0; i < 128; i++) {
    Wire.beginTransmission(i);
    if (Wire.endTransmission() == 0) {
      Serial.print("Found device at 0x");
      Serial.println(i, HEX);
    }
  }
}
void loop() {}
```

### Solution 3: Check Wiring
- SDA → GPIO 21 (default)
- SCL → GPIO 22 (default)
- VCC → 5V
- GND → GND

### Solution 4: Adjust Contrast
- Turn the blue potentiometer on LCD backpack

---

## ❌ Issue: Enrollment Fails / Can't Enroll

**Problem**: Sensor cannot create fingerprint template

### Solution 1: Finger Placement
- **Clean finger** - wash and dry
- **Press firmly** - good contact needed
- **Same position** - place finger same way both times
- **Don't move** - keep still during scan

### Solution 2: Sensor Quality
- Clean sensor surface with soft cloth
- Check for scratches or damage
- Ensure good lighting

### Solution 3: Check Settings
```cpp
#define ENROLL_MANUAL false  // Try manual mode for control
```

### Solution 4: ID Already Used
- Try different ID number
- Delete existing ID first

---

## ❌ Issue: Verification Always Fails

**Problem**: Enrolled fingerprint not matching

### Solution 1: Lower Confidence Threshold
**Edit Config.h**:
```cpp
#define VERIFY_CONFIDENCE_THRESHOLD 30  // Lower from 50
```

### Solution 2: Re-enroll
- Delete and re-enroll fingerprint
- Use consistent finger placement

### Solution 3: Check Sensor
- Clean sensor surface
- Ensure finger is pressed firmly

---

## ❌ Issue: Buzzer Not Working

**Problem**: No sound from buzzer

### Solution 1: Check Wiring
- Buzzer + → GPIO 25
- Buzzer - → GND

### Solution 2: Check Pin
**Edit Config.h**:
```cpp
#define BUZZER_PIN 26  // Try different GPIO
```

### Solution 3: Check Buzzer Type
- **Active buzzer**: Has internal oscillator (works with our code)
- **Passive buzzer**: Needs frequency signal (won't work)
- Use **active buzzer**

### Solution 4: Test Manually
Add to setup():
```cpp
digitalWrite(BUZZER_PIN, HIGH);
delay(1000);
digitalWrite(BUZZER_PIN, LOW);
```

---

## ❌ Issue: Serial Monitor Shows Nothing

**Problem**: No output in Serial Monitor

### Solution:
1. Check baud rate is set to **115200**
2. Ensure USB cable supports data transfer
3. Check correct COM port selected
4. Try different USB port

---

## ❌ Issue: Code Won't Compile

**Problem**: Build errors

### Solution 1: Install Dependencies
```bash
# In PlatformIO terminal
pio lib install
```

### Solution 2: Clean Build
```bash
pio run --target clean
pio run
```

### Solution 3: Check platformio.ini
Ensure libraries are listed:
```ini
lib_deps =
    marcoschwartz/LiquidCrystal_I2C@^1.1.4
    adafruit/Adafruit Fingerprint Sensor Library@^2.1.4
```

---

## ❌ Issue: Multiple Modes Active

**Problem**: Uncommented more than one mode

### Solution:
Open `Config.h` and ensure **only ONE** mode is uncommented:

```cpp
#define MODE_VERIFY      // ✓ Active
// #define MODE_ENROLL   // ✗ Inactive
// #define MODE_DELETE   // ✗ Inactive
```

---

## ❌ Issue: Enrollment Hangs at "Remove Finger"

**Problem**: Sensor still detecting finger

### Solution:
- **Completely remove finger** from sensor
- Wait for prompt to place finger again
- Ensure nothing touching sensor surface

---

## ❌ Issue: Delete Mode Doesn't Work

**Problem**: Cannot delete fingerprint

### Solution 1: Verify ID Exists
- Check sensor template count
- Ensure ID was enrolled

### Solution 2: Check ID Range
- IDs must be 1-127
- ID 0 is not valid

### Solution 3: Try Manual Mode
```cpp
#define DELETE_MANUAL true  // Enter ID via Serial
```

---

## ❌ Issue: Upload Fails

**Problem**: Cannot upload code to ESP32

### Solution 1: Hold BOOT Button
- Hold BOOT button on ESP32
- Click Upload
- Release when "Connecting..." appears

### Solution 2: Check USB Connection
- Try different USB cable
- Try different USB port
- Some cables are charge-only

### Solution 3: Check Driver
- Install CH340 or CP2102 USB driver
- Restart computer after installation

---

## 🔍 Debugging Tips

### Enable Verbose Output
Add to your code:
```cpp
Serial.println("Debug: Reached this point");
```

### Check Variable Values
```cpp
Serial.print("Finger ID: ");
Serial.println(fingerID);
```

### Test Hardware Separately
Test each component individually:
1. LCD only
2. Fingerprint sensor only
3. Buzzer only

---

## 📞 Still Having Issues?

### Checklist:
- [ ] Config.h has exactly ONE mode uncommented
- [ ] All wiring connections verified
- [ ] Correct I2C address for LCD
- [ ] Fingerprint sensor power is adequate
- [ ] Serial monitor baud rate is 115200
- [ ] PlatformIO libraries installed
- [ ] ESP32 board properly selected
- [ ] Latest code uploaded

### Get More Help:
1. Check Serial Monitor output for error messages
2. Verify hardware with example sketches
3. Test each mode separately
4. Review documentation files

---

## 🧪 Test Procedure

### 1. Test VERIFY Mode
```cpp
#define MODE_VERIFY
```
Upload and verify LCD shows "Waiting for valid finger..."

### 2. Test ENROLL Mode
```cpp
#define MODE_ENROLL
#define ENROLL_START_ID 99
#define ENROLL_COUNT 1
```
Upload and enroll one test fingerprint

### 3. Test DELETE Mode
```cpp
#define MODE_DELETE
#define DELETE_ID 99
#define DELETE_MANUAL false
```
Upload and verify it deletes the test fingerprint

If all three work, system is functioning correctly!

---

## 📋 Hardware Checklist

| Component | Test | Expected Result |
|-----------|------|-----------------|
| ESP32 | Upload blink sketch | LED blinks |
| LCD | I2C scanner | Shows address 0x27 or 0x3F |
| Fingerprint | Adafruit example | Reads template count |
| Buzzer | digitalWrite test | Makes sound |

---

## ⚡ Quick Fixes Summary

| Problem | Quick Fix |
|---------|-----------|
| No mode selected | Uncomment ONE mode in Config.h |
| Sensor not found | Check wiring, try different baud |
| LCD blank | Try I2C address 0x3F |
| Can't enroll | Clean finger, press firmly |
| No match | Lower confidence threshold |
| No sound | Check buzzer type (use active) |
| Won't compile | Run `pio lib install` |
| Can't upload | Hold BOOT button during upload |

---

Remember: Most issues are wiring or configuration - double-check connections first!
