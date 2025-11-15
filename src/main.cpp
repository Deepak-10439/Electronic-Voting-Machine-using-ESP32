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
  Serial.println("\n=== HYBRID VERIFICATION MODE ===");
  Serial.println("1. Local verification (R307 cache)");
  Serial.println("2. Cloud verification (if local fails)");
  
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Place finger");
  lcd.setCursor(0, 1);
  lcd.print("to verify...");
  
  Serial.println("Waiting for finger placement...");
  int p = -1;
  unsigned long startTime = millis();
  
  // Clear any previous finger readings
  delay(500);
  
  while (p != FINGERPRINT_OK && (millis() - startTime) < 30000) {
    p = finger.getImage();
    if (p == FINGERPRINT_NOFINGER) {
      delay(100);  // Increased delay for stability
      continue;
    }
    if (p == FINGERPRINT_OK) {
      Serial.println("✓ Finger detected successfully!");
      break;
    }
    if (p != FINGERPRINT_NOFINGER) {
      Serial.print("⚠ Error getting image (Code: ");
      Serial.print(p);
      Serial.println("). Retrying...");
      delay(200);  // Wait before retry
      continue;    // Don't exit, keep trying
    }
  }
  
  if (p != FINGERPRINT_OK) {
    Serial.println("❌ Timeout waiting for finger");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Timeout!");
    buzzer("error");
    delay(2000);
    currentMode = MODE_IDLE;
    return;
  }
  
  // Step 1: Try local verification first (R307 cache)
  Serial.println("\n🔍 STEP 1: Local Verification (R307 Cache)");
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Local Check...");
  lcd.setCursor(0, 1);
  lcd.print("Searching...");
  
  // Convert to template
  p = finger.image2Tz();
  if (p == FINGERPRINT_OK) {
    Serial.println("✓ Template created successfully");
    
    // Search locally stored templates
    p = finger.fingerSearch();
    if (p == FINGERPRINT_OK) {
      // Local match found!
      Serial.println("✅ LOCAL MATCH FOUND!");
      Serial.print("   Local ID: ");
      Serial.println(finger.fingerID);
      Serial.print("   Confidence: ");
      Serial.println(finger.confidence);
      
      // Verify with cloud for blockchain audit trail
      Serial.println("\n📡 Recording verification in blockchain...");
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Local: MATCH!");
      lcd.setCursor(0, 1);
      lcd.print("Updating...");
      
      // Send to cloud for blockchain recording
      int cloudResult = firebaseManager.cloudVerify(&finger, 100);
      
      // Show success
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("VERIFIED!");
      lcd.setCursor(0, 1);
      lcd.print("ID: #");
      lcd.print(finger.fingerID);
      buzzer("success");
      
      Serial.println("\n╔══════════════════════════════╗");
      Serial.println("║   VERIFICATION SUCCESSFUL!   ║");
      Serial.println("╠══════════════════════════════╣");
      Serial.print("║   Local ID: #");
      Serial.print(finger.fingerID);
      if (finger.fingerID < 10) Serial.print(" ");
      Serial.println("              ║");
      Serial.print("║   Confidence: ");
      Serial.print(finger.confidence);
      if (finger.confidence < 100) Serial.print(" ");
      Serial.println("            ║");
      Serial.println("║   Method: LOCAL + BLOCKCHAIN ║");
      Serial.println("║   Status: AUTHORIZED         ║");
      Serial.println("╚══════════════════════════════╝");
      Serial.println();
      
      delay(3000);
      currentMode = MODE_IDLE;
      return;
    }
  }
  
  // Step 2: Local verification failed, try cloud verification
  Serial.println("\n🌐 STEP 2: Cloud Verification (No local match)");
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Cloud Verify");
  lcd.setCursor(0, 1);
  lcd.print("Checking...");
  
  int matchedID = firebaseManager.cloudVerify(&finger, 100);
  
  if (matchedID > 0) {
    Serial.println("✅ CLOUD MATCH FOUND!");
    
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("VERIFIED!");
    lcd.setCursor(0, 1);
    lcd.print("ID: #");
    lcd.print(matchedID);
    buzzer("success");
    
    Serial.println("\n╔══════════════════════════════╗");
    Serial.println("║   VERIFICATION SUCCESSFUL!   ║");
    Serial.println("╠══════════════════════════════╣");
    Serial.print("║   Cloud ID: #");
    Serial.print(matchedID);
    if (matchedID < 10) Serial.print(" ");
    Serial.println("             ║");
    Serial.println("║   Method: CLOUD ONLY         ║");
    Serial.println("║   Status: AUTHORIZED         ║");
    Serial.println("╚══════════════════════════════╝");
    Serial.println();
    
    delay(3000);
  } else {
    Serial.println("❌ NO MATCH FOUND (Local + Cloud)");
    
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("NOT VERIFIED");
    lcd.setCursor(0, 1);
    lcd.print("Access Denied");
    buzzer("error");
    
    Serial.println("\n╔══════════════════════════════╗");
    Serial.println("║   VERIFICATION FAILED!       ║");
    Serial.println("╠══════════════════════════════╣");
    Serial.println("║   Local: NO MATCH            ║");
    Serial.println("║   Cloud: NO MATCH            ║");
    Serial.println("║   Status: UNAUTHORIZED       ║");
    Serial.println("╚══════════════════════════════╝");
    Serial.println();
    
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
  
  // Get template count from Firebase and local sensor
  Serial.println("\n=== TEMPLATE COUNT SYNC ===");
  int fbCount = firebaseManager.getTemplateCount();
  finger.getTemplateCount();
  int localCount = finger.templateCount;
  
  Serial.print("Firebase templates: ");
  Serial.println(fbCount);
  Serial.print("Local templates (R307): ");
  Serial.println(localCount);
  
  nextEnrollID = max(fbCount, localCount) + 1;
  
  Serial.print("Next enrollment ID: ");
  Serial.println(nextEnrollID);
  Serial.println("============================\n");
  
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
      
      // Add stabilization delay before verification
      Serial.println("\n>>> VERIFY MODE ACTIVATED <<<");
      Serial.println("Preparing sensor for verification...");
      delay(1000);  // Sensor stabilization delay
      
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Mode: VERIFY");
      lcd.setCursor(0, 1);
      lcd.print("Ready...");
    }
    else if (command == 'S') {
      Serial.println("\n=== System Status ===");
      Serial.print("WiFi: ");
      Serial.println(WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected");
      Serial.print("Firebase: ");
      Serial.println(firebaseReady ? "Ready" : "Not Ready");
      
      // Get current template counts
      finger.getTemplateCount();
      int localCount = finger.templateCount;
      int fbCount = firebaseManager.getTemplateCount();
      
      Serial.println("\n--- Template Storage ---");
      Serial.print("Local (R307): ");
      Serial.print(localCount);
      Serial.println("/1000 templates");
      Serial.print("Firebase: ");
      Serial.print(fbCount);
      Serial.println(" templates");
      Serial.print("Next Enroll ID: ");
      Serial.println(nextEnrollID);
      
      Serial.println("\n--- Current Mode ---");
      Serial.print("Mode: ");
      if (currentMode == MODE_IDLE) Serial.println("IDLE");
      else if (currentMode == MODE_ENROLL) Serial.println("ENROLL");
      else if (currentMode == MODE_VERIFY) Serial.println("VERIFY");
      
      Serial.println("\n--- Verification Method ---");
      Serial.println("1. Local R307 search (fast)");
      Serial.println("2. Cloud verification (backup)");
      Serial.println("3. Blockchain audit trail");
      Serial.println("==========================\n");
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
          
          // Add delay for sensor stabilization after enrollment
          Serial.println("Sensor stabilizing after enrollment...");
          delay(2000);
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