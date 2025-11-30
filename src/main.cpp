#include <LiquidCrystal_I2C.h>
#include <Adafruit_Fingerprint.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "config.h"

#define enrollButtonPin 25
#define voteButtonPin 26
#define statusButtonPin 27

enum Mode
{
  MODE_IDLE,
  MODE_ENROLL,
  MODE_VOTE
};

LiquidCrystal_I2C lcd(0x27, 16, 2);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&Serial2);

Mode currentMode = MODE_IDLE;
int nextEnrollID = 1;
bool wifiReady = false;
String backendUrl = BACKEND_URL;
String blockchainUrl = BLOCKCHAIN_URL;

void lcdPrint(uint8_t row, uint8_t position, String message)
{
  lcd.setCursor(position, row);
  lcd.print(message);
}

void lcdClear()
{
  lcd.clear();
}

void lcdSetup()
{
  lcd.init();
  lcd.clear();
  lcd.backlight();
}

bool submitVoteToBackend(int voterId, String candidate)
{
  Serial.println("\n=== Submitting Vote");
  Serial.print("Voter ID: ");
  Serial.println(voterId);
  Serial.print("Candidate: ");
  Serial.println(candidate);

  HTTPClient http;
  http.begin(backendUrl + "/api/vote/");
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(15000);

  // Create JSON payload
  JsonDocument doc;
  doc["voterId"] = voterId;
  doc["candidate"] = candidate;

  String jsonString;
  serializeJson(doc, jsonString);

  Serial.print("Sending: ");
  Serial.println(jsonString);

  int httpResponseCode = http.POST(jsonString);

  if (httpResponseCode == 200 || httpResponseCode == 201)
  {
    String response = http.getString();
    Serial.println("✓ Vote submitted successfully!");
    Serial.print("Response: ");
    Serial.println(response);
    http.end();
    return true;
  }
  else
  {
    String response = http.getString();
    Serial.println("✗ Failed to submit vote to backend");
    Serial.print("HTTP Code: ");
    Serial.println(httpResponseCode);
    Serial.print("Response: ");
    Serial.println(response);
    http.end();
    return false;
  }
}

bool submitVoteToBlockchain(int voterId, String candidate)
{
  Serial.print("Voter ID: ");
  Serial.println(voterId);
  Serial.print("Candidate: ");
  Serial.println(candidate);

  HTTPClient http;
  http.begin(backendUrl + "/api/blockchain/vote/");
  http.addHeader("Content-Type", "application/json");
  http.setTimeout(15000);

  // Create JSON payload for blockchain
  JsonDocument doc;
  doc["user_id"] = String(voterId);
  doc["vote_choice"] = candidate;
  doc["election_id"] = "evm_2024";

  String jsonString;
  serializeJson(doc, jsonString);

  Serial.print("Sending: ");
  Serial.println(jsonString);

  int httpResponseCode = http.POST(jsonString);

  if (httpResponseCode == 200 || httpResponseCode == 201)
  {
    String response = http.getString();
    http.end();
    return true;
  }
  else
  {
    String response = http.getString();
    Serial.println("✗ Failed to submit vote to blockchain");
    Serial.print("HTTP Code: ");
    Serial.println(httpResponseCode);
    Serial.print("Response: ");
    Serial.println(response);
    http.end();
    return false;
  }
}

String getCandidateName(int choice)
{
  switch (choice)
  {
  case 1:
    return "USAR";
  case 2:
    return "USAP";
  case 3:
    return "USDI";
  default:
    return "INVALID";
  }
}

void handleVoting(int voterId)
{
  Serial.println("Select your candidate:");
  Serial.println("1. USAR (Serial: 1 or Button: Pin 25)");
  Serial.println("2. USAP (Serial: 2 or Button: Pin 26)");
  Serial.println("3. USDI (Serial: 3 or Button: Pin 27)");
  Serial.println("Enter choice via Serial or Press Button: ");

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Select candidate:");
  lcd.setCursor(0, 1);
  lcd.print("Btn25=USAR 26=USAP");
  delay(1500);
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("27=USDI or");
  lcd.setCursor(0, 1);
  lcd.print("Serial: 1,2,3");

  int choice = 0;
  unsigned long startTime = millis();
  unsigned long timeout = 30000; // 30 second timeout

  // Debug: Print initial button states
  Serial.print("Initial button states - Pin 25: ");
  Serial.print(digitalRead(enrollButtonPin));
  Serial.print(", Pin 26: ");
  Serial.print(digitalRead(voteButtonPin));
  Serial.print(", Pin 27: ");
  Serial.println(digitalRead(statusButtonPin));

  // Wait for either serial input or button press
  while (choice == 0 && (millis() - startTime) < timeout)
  {
    // Check for serial input
    if (Serial.available())
    {
      choice = Serial.parseInt();
      while (Serial.available())
        Serial.read(); // Clear buffer
      if (choice >= 1 && choice <= 3)
      {
        Serial.print("Choice selected via Serial: ");
        Serial.println(choice);
        break;
      }
      else
      {
        choice = 0; // Reset invalid choice
      }
    }

    // Read button states
    bool btn25 = digitalRead(enrollButtonPin);
    bool btn26 = digitalRead(voteButtonPin);
    bool btn27 = digitalRead(statusButtonPin);

    // Check for button presses with stable reading
    if (btn25 == LOW)
    {
      delay(50); // Wait for stable reading
      if (digitalRead(enrollButtonPin) == HIGH)
      { // Confirm button is still pressed
        choice = 1;
        Serial.println("Choice selected via Button (Pin 25): USAR");
        delay(300); // Debounce delay
        break;
      }
    }
    if (btn26 == LOW)
    {
      delay(50); // Wait for stable reading
      if (digitalRead(voteButtonPin) == HIGH)
      { // Confirm button is still pressed
        choice = 2;
        Serial.println("Choice selected via Button (Pin 26): USAP");
        delay(300); // Debounce delay
        break;
      }
    }
    if (btn27 == LOW)
    {
      delay(50); // Wait for stable reading
      if (digitalRead(statusButtonPin) == HIGH)
      { // Confirm button is still pressed
        choice = 3;
        Serial.println("Choice selected via Button (Pin 27): USDI");
        delay(300); // Debounce delay
        break;
      }
    }

    delay(10);
  }

  if (choice == 0)
  {
    Serial.println("\n❌ Timeout! No candidate selected.");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Timeout!");
    lcd.setCursor(0, 1);
    lcd.print("No selection");
    delay(2000);
    return;
  }

  if (choice < 1 || choice > 3)
  {
    Serial.println("\n❌ Invalid choice! Please select 1, 2, or 3.");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Invalid Choice!");
    lcd.setCursor(0, 1);
    lcd.print("Try Again");
    delay(2000);
    return;
  }

  String candidate = getCandidateName(choice);

  Serial.println("\n✓ Vote Selection:");
  Serial.print("Voter ID: ");
  Serial.println(voterId);
  Serial.print("Candidate: ");
  Serial.println(candidate);

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Voting for:");
  lcd.setCursor(0, 1);
  lcd.print(candidate);
  delay(2000);

  // Show processing
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Processing...");
  lcd.setCursor(0, 1);
  lcd.print("Please wait");

  // Submit vote to backend first
  bool backendSuccess = submitVoteToBackend(voterId, candidate);

  if (!backendSuccess)
  {
    Serial.println("\n❌ Backend vote submission failed!");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Backend Error!");
    lcd.setCursor(0, 1);
    lcd.print("Vote Failed");
    delay(3000);
    return;
  }

  // Submit vote to blockchain
  bool blockchainSuccess = submitVoteToBlockchain(voterId, candidate);

  if (!blockchainSuccess)
  {
    Serial.println("\n⚠ Blockchain submission failed, but backend vote recorded!");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Partial Success");
    lcd.setCursor(0, 1);
    lcd.print("Backend OK");
    delay(3000);
    return;
  }

  // Both successful
  Serial.println("\n✅ VOTE SUCCESSFULLY RECORDED!");
  Serial.print("Voter ID: #");
  Serial.print(voterId);
  if (voterId < 10)
    Serial.print(" ");
  Serial.println("");
  Serial.print("║   Candidate: ");
  Serial.print(candidate);
  Serial.println("             ║");

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("VOTE RECORDED!");
  lcd.setCursor(0, 1);
  lcd.print("ID:");
  lcd.print(voterId);
  lcd.print(" -> ");
  lcd.print(candidate);

  delay(5000);
}

uint8_t enrollFingerprint(uint16_t id)
{
  int p = -1;

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Enroll ID #");
  lcd.print(id);
  lcd.setCursor(0, 1);
  lcd.print("Place finger...");
  Serial.print("Waiting for finger to enroll ID #");
  Serial.println(id);

  while (p != FINGERPRINT_OK)
  {
    p = finger.getImage();
    switch (p)
    {
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
  if (p != FINGERPRINT_OK)
  {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Convert failed");
    delay(2000);
    return p;
  }

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Remove finger");
  Serial.println("Remove finger");
  delay(2000);

  p = 0;
  while (p != FINGERPRINT_NOFINGER)
  {
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
  while (p != FINGERPRINT_OK)
  {
    p = finger.getImage();
  }

  // Convert image
  p = finger.image2Tz(2);
  if (p != FINGERPRINT_OK)
  {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Convert failed");
    delay(2000);
    return p;
  }

  // Create model
  p = finger.createModel();
  if (p != FINGERPRINT_OK)
  {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Match failed");
    delay(2000);
    return p;
  }

  // Store model locally
  p = finger.storeModel(id);
  if (p == FINGERPRINT_OK)
  {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Enrolled!");
    lcd.setCursor(0, 1);
    lcd.print("ID: ");
    lcd.print(id);
    Serial.print("Successfully enrolled ID #");
    Serial.println(id);
    delay(2000);
    return FINGERPRINT_OK;
  }
  else
  {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Store failed");
    delay(2000);
    return p;
  }
}

void verifyForVoting()
{
  Serial.println("\n=== VOTER VERIFICATION ===");

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Place finger");
  lcd.setCursor(0, 1);
  lcd.print("to vote...");

  Serial.println("Waiting for finger placement...");
  int p = -1;
  unsigned long startTime = millis();

  // Clear any previous finger readings
  delay(500);

  while (p != FINGERPRINT_OK && (millis() - startTime) < 30000)
  {
    p = finger.getImage();
    if (p == FINGERPRINT_NOFINGER)
    {
      delay(100);
      continue;
    }
    if (p == FINGERPRINT_OK)
    {
      Serial.println("✓ Finger detected successfully!");
      break;
    }
    if (p != FINGERPRINT_NOFINGER)
    {
      Serial.print("⚠ Error getting image (Code: ");
      Serial.print(p);
      Serial.println("). Retrying...");
      delay(200);
      continue;
    }
  }

  if (p != FINGERPRINT_OK)
  {
    Serial.println("❌ Timeout waiting for finger");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Timeout!");
    delay(2000);
    currentMode = MODE_IDLE;
    return;
  }

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Verifying...");
  lcd.setCursor(0, 1);
  lcd.print("Please wait");

  // Convert to template
  p = finger.image2Tz();
  if (p == FINGERPRINT_OK)
  {
    Serial.println("✓ Template created successfully");

    // Search locally stored templates
    p = finger.fingerSearch();
    if (p == FINGERPRINT_OK)
    {
      // Local match found!
      Serial.println("✅ VOTER VERIFIED!");
      Serial.print("   Voter ID: ");
      Serial.println(finger.fingerID);
      Serial.print("   Confidence: ");
      Serial.println(finger.confidence);

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("VERIFIED!");
      lcd.setCursor(0, 1);
      lcd.print("Voter ID: #");
      lcd.print(finger.fingerID);

      delay(2000);
      // Debug: Print initial button states
      Serial.print("Initial button states - Pin 25: ");
      Serial.print(digitalRead(enrollButtonPin));
      Serial.print(", Pin 26: ");
      Serial.print(digitalRead(voteButtonPin));
      Serial.print(", Pin 27: ");
      Serial.println(digitalRead(statusButtonPin));
      // Proceed to voting
      handleVoting(finger.fingerID);

      currentMode = MODE_IDLE;
      return;
    }
  }

  // Verification failed
  Serial.println("❌ VOTER NOT VERIFIED");

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("NOT VERIFIED");
  lcd.setCursor(0, 1);
  lcd.print("Access Denied");

  Serial.println("\n╔══════════════════════════════╗");
  Serial.println("║   VERIFICATION FAILED!       ║");
  Serial.println("╠══════════════════════════════╣");
  Serial.println("║   Status: UNAUTHORIZED       ║");
  Serial.println("║   Cannot Vote                ║");
  Serial.println("╚══════════════════════════════╝");
  Serial.println();

  delay(2000);
  currentMode = MODE_IDLE;
}

void setup()
{
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

  // Initialize button pins
  pinMode(enrollButtonPin, INPUT_PULLUP);
  pinMode(voteButtonPin, INPUT_PULLUP);
  pinMode(statusButtonPin, INPUT_PULLUP);

  // Initialize fingerprint sensor
  if (finger.verifyPassword())
  {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Sensor OK!");
    delay(1000);
  }
  else
  {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Sensor Error!");
    while (1)
    {
      delay(1);
    }
  }

  // Initialize WiFi
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Connecting WiFi");

  Serial.print("Connecting to WiFi");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20)
  {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED)
  {
    Serial.println("\nWiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi Connected!");
    wifiReady = true;
    delay(1000);
  }
  else
  {
    Serial.println("\nWiFi Connection Failed!");
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("WiFi Failed!");
    delay(2000);
  }

  // Get template count from local sensor
  Serial.println("\n=== TEMPLATE COUNT ===");
  finger.getTemplateCount();
  int localCount = finger.templateCount;

  Serial.print("Local templates (R307): ");
  Serial.println(localCount);

  nextEnrollID = localCount + 1;

  Serial.print("Next enrollment ID: ");
  Serial.println(nextEnrollID);
  Serial.println("=========================\n");

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Local: ");
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

  Serial.println("\n=== EVM System Ready ===");
  Serial.println("Commands:");
  Serial.println("  E - Enroll new voter");
  Serial.println("  V - Start voting");
  Serial.println("  S - Show status");
  Serial.println("=============================\n");
}

void loop()
{
  // Check for enroll button
  static bool lastEnrollPressed = false;
  bool enrollPressed = (digitalRead(enrollButtonPin) == LOW);

  if (enrollPressed && !lastEnrollPressed && currentMode == MODE_IDLE)
  {
    currentMode = MODE_ENROLL;
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Mode: ENROLL");
    lcd.setCursor(0, 1);
    lcd.print("Ready...");
    Serial.println("\n>>> ENROLL MODE ACTIVATED (Button) <<<");
    delay(300); // Simple debounce
  }
  lastEnrollPressed = enrollPressed;

  // Check for vote button
  static bool lastVotePressed = false;
  bool votePressed = (digitalRead(voteButtonPin) == LOW);

  if (votePressed && !lastVotePressed && currentMode == MODE_IDLE)
  {
    currentMode = MODE_VOTE;
    Serial.println("\n>>> VOTING MODE ACTIVATED (Button) <<<");
    Serial.println("Preparing sensor for voting...");
    delay(1000); // Sensor stabilization delay

    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Mode: VOTE");
    lcd.setCursor(0, 1);
    lcd.print("Ready...");
  }
  lastVotePressed = votePressed;

  // Check for status button
  static bool lastStatusPressed = false;
  bool statusPressed = (digitalRead(statusButtonPin) == LOW);

  if (statusPressed && !lastStatusPressed)
  {
    Serial.println("\n=== EVM System Status (Button) ===");
    Serial.print("WiFi: ");
    Serial.println(WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected");
    Serial.print("Backend URL: ");
    Serial.println(backendUrl);
    Serial.print("Blockchain URL: ");
    Serial.println(blockchainUrl);

    // Get current template counts
    finger.getTemplateCount();
    int localCount = finger.templateCount;

    Serial.println("\n--- Voter Storage ---");
    Serial.print("Local (R307): ");
    Serial.print(localCount);
    Serial.println("/1000 voters");
    Serial.print("Next Enroll ID: ");
    Serial.println(nextEnrollID);

    Serial.println("\n--- Current Mode ---");
    Serial.print("Mode: ");
    if (currentMode == MODE_IDLE)
      Serial.println("IDLE");
    else if (currentMode == MODE_ENROLL)
      Serial.println("ENROLL");
    else if (currentMode == MODE_VOTE)
      Serial.println("VOTE");

    Serial.println("\n--- Voting Candidates ---");
    Serial.println("1. USAR");
    Serial.println("2. USAP");
    Serial.println("3. USDI");
    Serial.println("\n--- Button Controls ---");
    Serial.println("Pin 25: Enroll Button");
    Serial.println("Pin 26: Vote Button");
    Serial.println("Pin 27: Status Button");
    Serial.println("==============================\n");

    // Show brief status on LCD
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Status: ");
    lcd.print(localCount);
    lcd.print(" voters");
    lcd.setCursor(0, 1);
    lcd.print("WiFi: ");
    lcd.print(WiFi.status() == WL_CONNECTED ? "OK" : "FAIL");
    delay(3000);

    // Return to previous display
    lcd.clear();
    lcd.setCursor(0, 0);
    if (currentMode == MODE_IDLE)
    {
      lcd.print("Mode: IDLE");
      lcd.setCursor(0, 1);
      lcd.print("Ready...");
    }
    else if (currentMode == MODE_ENROLL)
    {
      lcd.print("Mode: ENROLL");
      lcd.setCursor(0, 1);
      lcd.print("Ready...");
    }
    else if (currentMode == MODE_VOTE)
    {
      lcd.print("Mode: VOTE");
      lcd.setCursor(0, 1);
      lcd.print("Ready...");
    }
    delay(300); // Simple debounce
  }
  lastStatusPressed = statusPressed;

  // Check for Serial commands
  if (Serial.available() > 0)
  {
    char command = Serial.read();
    command = toupper(command);

    if (command == 'E')
    {
      currentMode = MODE_ENROLL;
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Mode: ENROLL");
      lcd.setCursor(0, 1);
      lcd.print("Ready...");
      Serial.println("\n>>> ENROLL MODE ACTIVATED <<<");
    }
    else if (command == 'V')
    {
      currentMode = MODE_VOTE;

      // Add stabilization delay before voting
      Serial.println("\n>>> VOTING MODE ACTIVATED <<<");
      Serial.println("Preparing sensor for voting...");
      delay(1000); // Sensor stabilization delay

      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Mode: VOTE");
      lcd.setCursor(0, 1);
      lcd.print("Ready...");
    }
    else if (command == 'S')
    {
      Serial.println("\n=== EVM System Status ===");
      Serial.print("WiFi: ");
      Serial.println(WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected");
      Serial.print("Backend URL: ");
      Serial.println(backendUrl);
      Serial.print("Blockchain URL: ");
      Serial.println(blockchainUrl);

      // Get current template counts
      finger.getTemplateCount();
      int localCount = finger.templateCount;

      Serial.println("\n--- Voter Storage ---");
      Serial.print("Local (R307): ");
      Serial.print(localCount);
      Serial.println("/1000 voters");
      Serial.print("Next Enroll ID: ");
      Serial.println(nextEnrollID);

      Serial.println("\n--- Current Mode ---");
      Serial.print("Mode: ");
      if (currentMode == MODE_IDLE)
        Serial.println("IDLE");
      else if (currentMode == MODE_ENROLL)
        Serial.println("ENROLL");
      else if (currentMode == MODE_VOTE)
        Serial.println("VOTE");

      Serial.println("\n--- Voting Candidates ---");
      Serial.println("1. USAR");
      Serial.println("2. USAP");
      Serial.println("3. USDI");
      Serial.println("==============================\n");
    }
  }

  // Handle different modes
  switch (currentMode)
  {
  case MODE_ENROLL:
  {
    uint8_t result = enrollFingerprint(nextEnrollID);
    if (result == FINGERPRINT_OK)
    {
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
    Serial.println("Enter 'E' to Enroll or 'V' to Vote\n");
    break;
  }

  case MODE_VOTE:
  {
    Serial.println("DEBUG: In MODE_VOTE case");
    if (wifiReady)
    {
      Serial.println("DEBUG: WiFi ready, calling verifyForVoting()");
      verifyForVoting();
      Serial.println("DEBUG: Returned from verifyForVoting()");
      currentMode = MODE_IDLE; // Ensure mode is reset
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Mode: IDLE");
      lcd.setCursor(0, 1);
      lcd.print("Ready...");
      Serial.println("\n>>> Returned to IDLE mode <<<");
      Serial.println("Enter 'E' to Enroll or 'V' to Vote\n");
    }
    else
    {
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("WiFi not ready!");
      lcd.setCursor(0, 1);
      lcd.print("Cannot vote");
      Serial.println("ERROR: WiFi not ready! Cannot submit votes.");
      delay(2000);
      currentMode = MODE_IDLE;
    }
    break;
  }

  case MODE_IDLE:
    // Display status
    delay(100);
    break;
  }

  delay(100);
}