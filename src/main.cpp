#include <LiquidCrystal_I2C.h>
#include <Adafruit_Fingerprint.h>
#include <WiFi.h>
#include "config.h"
#include "FirebaseManager.h"

#define buzzerPin 25

enum Mode {
  MODE_IDLE,
  MODE_ENROLL,
  MODE_VERIFY
};

LiquidCrystal_I2C lcd(0x27, 16, 2);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&Serial2);
FirebaseManager firebaseManager;

Mode currentMode = MODE_IDLE;
int nextEnrollID = 1;
bool firebaseReady = false;

void lcdPrint(uint8_t row, uint8_t position, String message) {
  lcd.setCursor(position, row);
  lcd.print(message);
}

void lcdClear() {
  lcd.clear();
}

void lcdSetup() {
  lcd.init();
  lcd.clear();
  lcd.backlight();
}

void buzzer(String type) {
  if (type == "error") {
    digitalWrite(buzzerPin, HIGH);
    delay(300);
    digitalWrite(buzzerPin, LOW);
    delay(200);
    digitalWrite(buzzerPin, HIGH);
    delay(300);
    digitalWrite(buzzerPin, LOW);
  } else if (type == "success") {
    digitalWrite(buzzerPin, HIGH);
    delay(500);
    digitalWrite(buzzerPin, LOW);
  }
}

uint8_t enrollFingerprint(uint16_t id) {
  int p = -1;
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Enroll ID #");
  lcd.print(id);
  lcd.setCursor(0, 1);
  lcd.print("Place finger...");
  Serial.print("Waiting for finger to enroll ID #");
  Serial.println(id);
  
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
    switch (p) {
      case FINGERPRINT_OK:
        Serial.println("Image taken");
        break;
      case FINGERPRINT_NOFINGER:
        break;
      default:
        Serial.println("Error getting image");
        return p;
    }
  }
  
  // Convert image
  p = finger.image2Tz(1);
  if (p != FINGERPRINT_OK) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Convert failed");
    buzzer("error");
    delay(2000);
    return p;
  }
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Remove finger");
  Serial.println("Remove finger");
  delay(2000);
  
  p = 0;
  while (p != FINGERPRINT_NOFINGER) {
    p = finger.getImage();
  }
  
  // Ask for same finger again
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Place same");
  lcd.setCursor(0, 1);
  lcd.print("finger again");
  Serial.println("Place same finger again");
  
  p = -1;
  while (p != FINGERPRINT_OK) {
    p = finger.getImage();
  }
  
  // Convert image
  p = finger.image2Tz(2);
  if (p != FINGERPRINT_OK) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Convert failed");
    buzzer("error");
    delay(2000);
    return p;
  }
  
  // Create model
  p = finger.createModel();
  if (p != FINGERPRINT_OK) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Match failed");
    buzzer("error");
    delay(2000);
    return p;
  }
  
  // Store model locally (optional, for backup)
  p = finger.storeModel(id);
  if (p == FINGERPRINT_OK) {
    Serial.println("Stored locally!");
  }
  
  // Upload to Firebase
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Uploading to");
  lcd.setCursor(0, 1);
  lcd.print("Firebase...");
  
  if (firebaseManager.uploadTemplate(id, &finger)) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Enrolled!");
    lcd.setCursor(0, 1);
    lcd.print("ID: ");
    lcd.print(id);
    buzzer("success");
    Serial.print("Successfully enrolled ID #");
    Serial.println(id);
    delay(2000);
    return FINGERPRINT_OK;
  } else {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Upload failed");
    buzzer("error");
    delay(2000);
    return FINGERPRINT_PACKETRECIEVEERR;
  }
}

void verifyFingerprint() {
  Serial.println("Starting fingerprint verification...");
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Place finger");
  lcd.setCursor(0, 1);
  lcd.print("to verify...");
  
  Serial.println("Waiting for finger...");
  int p = -1;
  unsigned long startTime = millis();
  while (p != FINGERPRINT_OK && (millis() - startTime) < 30000) {  // 30 second timeout
    p = finger.getImage();
    if (p == FINGERPRINT_NOFINGER) {
      delay(50);
      continue;
    }
    if (p == FINGERPRINT_OK) {
      Serial.println("Finger detected!");
      break;
    }
    if (p != FINGERPRINT_NOFINGER) {
      Serial.print("Error getting image: ");
      Serial.println(p);
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Error reading");
      buzzer("error");
      delay(2000);
      currentMode = MODE_IDLE;
      return;
    }
  }
  
  if (p != FINGERPRINT_OK) {
    Serial.println("Timeout waiting for finger");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Timeout!");
    delay(2000);
    currentMode = MODE_IDLE;
    return;
  }
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Verifying with");
  lcd.setCursor(0, 1);
  lcd.print("Firebase...");
  
  // Download templates from Firebase and verify (up to 100 templates)
  int matchedID = firebaseManager.downloadAndVerify(&finger, 100);
  
  if (matchedID > 0) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Match Found!");
    lcd.setCursor(0, 1);
    lcd.print("ID: ");
    lcd.print(matchedID);
    buzzer("success");
    Serial.print("Matched with ID #");
    Serial.println(matchedID);
    delay(3000);
  } else {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("No Match");
    lcd.setCursor(0, 1);
    lcd.print("Found!");
    buzzer("error");
    Serial.println("No match found");
    delay(2000);
  }
  
  currentMode = MODE_IDLE;
}

void setup() {
  Serial.begin(115200);
  Serial2.begin(57600);
  delay(100);
  
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Welcome to ");
  lcd.setCursor(0, 1);
  lcd.print("Fingerprint EVM");
  delay(2000);
  lcd.clear();
  
  pinMode(buzzerPin, OUTPUT);

  // Initialize fingerprint sensor
  if (finger.verifyPassword()) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Sensor OK!");
    delay(1000);
  } else {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Sensor Error!");
    buzzer("error");
    while (1) {
      delay(1);
    }
  }

  // Initialize WiFi
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Connecting WiFi");
  if (firebaseManager.initWiFi()) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi Connected!");
    delay(1000);
  } else {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi Failed!");
    buzzer("error");
    delay(2000);
  }
  
  // Initialize Firebase
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Init Firebase...");
  if (firebaseManager.initFirebase()) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Firebase Ready!");
    firebaseReady = true;
    delay(1000);
  } else {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Firebase Failed!");
    buzzer("error");
    delay(2000);
  }
  
  // Get template count from Firebase
  int fbCount = firebaseManager.getTemplateCount();
  finger.getTemplateCount();
  int localCount = finger.templateCount;
  
  nextEnrollID = max(fbCount, localCount) + 1;
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("FB:");
  lcd.print(fbCount);
  lcd.print(" Local:");
  lcd.print(localCount);
  lcd.setCursor(0, 1);
  lcd.print("Next ID: ");
  lcd.print(nextEnrollID);
  delay(3000);
  
  // Show mode selection
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Mode: IDLE");
  lcd.setCursor(0, 1);
  lcd.print("Ready...");
  
  Serial.println("\n=== Fingerprint System Ready ===");
  Serial.println("Commands:");
  Serial.println("  E - Enroll new fingerprint");
  Serial.println("  V - Verify fingerprint");
  Serial.println("  S - Show status");
  Serial.println("================================\n");
}

void loop() {
  // Check for Serial commands
  if (Serial.available() > 0) {
    char command = Serial.read();
    command = toupper(command);
    
    if (command == 'E') {
      currentMode = MODE_ENROLL;
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Mode: ENROLL");
      lcd.setCursor(0, 1);
      lcd.print("Ready...");
      Serial.println("\n>>> ENROLL MODE ACTIVATED <<<");
    }
    else if (command == 'V') {
      currentMode = MODE_VERIFY;
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Mode: VERIFY");
      lcd.setCursor(0, 1);
      lcd.print("Ready...");
      Serial.println("\n>>> VERIFY MODE ACTIVATED <<<");
    }
    else if (command == 'S') {
      Serial.println("\n=== System Status ===");
      Serial.print("WiFi: ");
      Serial.println(WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected");
      Serial.print("Firebase: ");
      Serial.println(firebaseReady ? "Ready" : "Not Ready");
      Serial.print("Next Enroll ID: ");
      Serial.println(nextEnrollID);
      Serial.print("Mode: ");
      if (currentMode == MODE_IDLE) Serial.println("IDLE");
      else if (currentMode == MODE_ENROLL) Serial.println("ENROLL");
      else if (currentMode == MODE_VERIFY) Serial.println("VERIFY");
      Serial.println("====================\n");
    }
  }
  
  // Handle different modes
  switch (currentMode) {
    case MODE_ENROLL:
      if (firebaseReady) {  // Check dynamically instead of static flag
        uint8_t result = enrollFingerprint(nextEnrollID);
        if (result == FINGERPRINT_OK) {
          firebaseManager.updateTemplateCount(nextEnrollID);
          nextEnrollID++;
        }
        currentMode = MODE_IDLE;
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Mode: IDLE");
        lcd.setCursor(0, 1);
        lcd.print("Ready...");
        Serial.println("\n>>> Returned to IDLE mode <<<");
        Serial.println("Enter 'E' to Enroll or 'V' to Verify\n");
      } else {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Firebase not");
        lcd.setCursor(0, 1);
        lcd.print("ready!");
        buzzer("error");
        Serial.println("ERROR: Firebase not ready!");
        delay(2000);
        currentMode = MODE_IDLE;
      }
      break;
      
    case MODE_VERIFY:
      Serial.println("DEBUG: In MODE_VERIFY case");
      if (firebaseReady) {  // Check dynamically instead of static flag
        Serial.println("DEBUG: Firebase ready, calling verifyFingerprint()");
        verifyFingerprint();
        Serial.println("DEBUG: Returned from verifyFingerprint()");
        currentMode = MODE_IDLE;  // Ensure mode is reset
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Mode: IDLE");
        lcd.setCursor(0, 1);
        lcd.print("Ready...");
        Serial.println("\n>>> Returned to IDLE mode <<<");
        Serial.println("Enter 'E' to Enroll or 'V' to Verify\n");
      } else {
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Firebase not");
        lcd.setCursor(0, 1);
        lcd.print("ready!");
        buzzer("error");
        Serial.println("ERROR: Firebase not ready!");
        delay(2000);
        currentMode = MODE_IDLE;
      }
      break;
      
    case MODE_IDLE:
      // Display status
      delay(100);
      break;
  }
  
  delay(100);
}