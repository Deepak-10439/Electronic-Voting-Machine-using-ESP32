/*
 * Electronic Voting Machine (EVM) using ESP32
 * Main Controller File
 * 
 * INSTRUCTIONS:
 * 1. Open Config.h file
 * 2. Uncomment ONLY ONE mode:
 *    - MODE_VERIFY  : For fingerprint verification/voting
 *    - MODE_ENROLL  : For enrolling new fingerprints
 *    - MODE_DELETE  : For deleting fingerprints
 * 3. Configure settings in Config.h as needed
 * 4. Upload code to ESP32
 * 
 * NO NEED TO EDIT THIS FILE!
 */

#include <Arduino.h>
#include <Adafruit_Fingerprint.h>
#include "Config.h"
#include "FingerPrintManager.h"
#include "LCDManager.h"
#include "BuzzerManager.h"

// Hardware instances
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&FINGERPRINT_SERIAL);
LCDManager lcdManager(LCD_ADDRESS, LCD_COLS, LCD_ROWS);
BuzzerManager buzzerManager(BUZZER_PIN);
FingerPrintManager fpManager(&finger);

// Mode-specific function declarations
#ifdef MODE_VERIFY
  void verifyMode_setup();
  void verifyMode_loop();
#endif

#ifdef MODE_ENROLL
  void enrollMode_setup();
  void enrollMode_loop();
#endif

#ifdef MODE_DELETE
  void deleteMode_setup();
  void deleteMode_loop();
#endif

#ifdef MODE_CLOUD
  void cloudMode_setup();
  void cloudMode_loop();
#endif

void setup() {
  Serial.begin(115200);
  FINGERPRINT_SERIAL.begin(FINGERPRINT_BAUDRATE);
  delay(100);
  
  // Initialize hardware
  lcdManager.initialize();
  buzzerManager.initialize();
  
  // Check which mode is active
  #if !defined(MODE_VERIFY) && !defined(MODE_ENROLL) && !defined(MODE_DELETE) && !defined(MODE_CLOUD)
    Serial.println("\n*** ERROR: No mode selected! ***");
    Serial.println("Please open Config.h and uncomment ONE mode:");
    Serial.println("  - MODE_VERIFY");
    Serial.println("  - MODE_ENROLL");
    Serial.println("  - MODE_DELETE");
    Serial.println("  - MODE_CLOUD");
    lcdManager.clear();
    lcdManager.print(0, 0, "ERROR!");
    lcdManager.print(1, 0, "No mode set");
    buzzerManager.playError();
    while(1) { delay(1000); }
  #endif
  
  // Initialize fingerprint sensor
  if (!fpManager.initialize()) {
    Serial.println("Fingerprint sensor initialization failed!");
    lcdManager.showSensorNotFound();
    buzzerManager.playError();
    while (1) { delay(1); }
  }
  
  // Call mode-specific setup
  #ifdef MODE_VERIFY
    verifyMode_setup();
  #elif defined(MODE_ENROLL)
    enrollMode_setup();
  #elif defined(MODE_DELETE)
    deleteMode_setup();
  #elif defined(MODE_CLOUD)
    cloudMode_setup();
  #endif
}

void loop() {
  // Call mode-specific loop
  #ifdef MODE_VERIFY
    verifyMode_loop();
  #elif defined(MODE_ENROLL)
    enrollMode_loop();
  #elif defined(MODE_DELETE)
    deleteMode_loop();
  #elif defined(MODE_CLOUD)
    cloudMode_loop();
  #endif
}