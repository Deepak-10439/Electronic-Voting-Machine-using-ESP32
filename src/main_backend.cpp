/**
 * ESP32 EVM Voting System - Main Controller
 * Uses Django REST API Backend for Secure Blockchain Voting
 * Replaces Firebase with enterprise-grade backend
 */

#include <LiquidCrystal_I2C.h>
#include <Adafruit_Fingerprint.h>
#include <WiFi.h>
#include "config.h"
#include "BackendManager.h"

#define buzzerPin 25
#define enrollButton 26
#define voteButton 27

enum SystemMode {
    MODE_IDLE,
    MODE_AUTH,
    MODE_VOTE,
    MODE_RESULTS
};

// Hardware components
LiquidCrystal_I2C lcd(0x27, 16, 2);
Adafruit_Fingerprint finger = Adafruit_Fingerprint(&Serial2);

// Backend manager for API communication
BackendManager backend(BACKEND_URL, ESP32_DEVICE_ID);

// System state
SystemMode currentMode = MODE_IDLE;
bool systemReady = false;
bool voterAuthenticated = false;
String currentVoterToken = "";
String currentVoterName = "";
String currentVoterId = "";

// Button state tracking
bool enrollButtonPressed = false;
bool voteButtonPressed = false;
unsigned long lastButtonPress = 0;

// Voting data
String activeElectionId = "";
String selectedCandidateId = "";

void setup() {
    Serial.begin(115200);
    Serial2.begin(57600);
    delay(100);
    
    // Initialize hardware
    initializeHardware();
    
    // Connect to backend
    initializeBackend();
    
    // Show ready status
    showReadyScreen();
}

void loop() {
    // Handle serial commands for testing
    handleSerialCommands();
    
    // Handle button presses
    handleButtons();
    
    // Handle current mode
    handleCurrentMode();
    
    delay(100);
}

void initializeHardware() {
    // Initialize LCD
    lcd.init();
    lcd.backlight();
    lcd.clear();
    showMessage("Starting EVM", "Blockchain System");
    delay(2000);
    
    // Initialize buzzer
    pinMode(buzzerPin, OUTPUT);
    pinMode(enrollButton, INPUT_PULLUP);
    pinMode(voteButton, INPUT_PULLUP);
    
    // Initialize fingerprint sensor
    showMessage("Init Sensor", "Please wait...");
    if (finger.verifyPassword()) {
        showMessage("Sensor Ready!", "");
        playSound("success");
        delay(1000);
    } else {
        showMessage("Sensor Error!", "Check connection");
        playSound("error");
        while (1) { delay(1); }
    }
}

void initializeBackend() {
    // Connect to WiFi
    showMessage("Connecting WiFi", WIFI_SSID);
    if (backend.connectWiFi(WIFI_SSID, WIFI_PASSWORD)) {
        showMessage("WiFi Connected!", WiFi.localIP().toString());
        delay(1500);
    } else {
        showMessage("WiFi Failed!", "Check credentials");
        playSound("error");
        delay(5000);
        ESP.restart();
    }
    
    // Initialize backend connection
    showMessage("Init Backend", "Connecting...");
    if (backend.begin()) {
        showMessage("Backend Ready!", "System Online");
        systemReady = true;
        playSound("success");
        
        // Sync system time
        backend.syncSystemTime();
        delay(1500);
    } else {
        showMessage("Backend Error!", "Check server");
        playSound("error");
        delay(5000);
        ESP.restart();
    }
}

void handleSerialCommands() {
    if (Serial.available() > 0) {
        String command = Serial.readString();
        command.trim();
        command.toUpperCase();
        
        if (command == "STATUS" || command == "S") {
            printSystemStatus();
        } else if (command == "AUTH" || command == "A") {
            currentMode = MODE_AUTH;
            showMessage("AUTH Mode", "Ready...");
        } else if (command == "VOTE" || command == "V") {
            if (voterAuthenticated) {
                currentMode = MODE_VOTE;
                showMessage("VOTE Mode", "Ready...");
            } else {
                showMessage("Not Authenticated", "Use AUTH first");
            }
        } else if (command == "RESULTS" || command == "R") {
            currentMode = MODE_RESULTS;
            showMessage("Results Mode", "Loading...");
        } else if (command == "LOGOUT" || command == "L") {
            logoutVoter();
        }
    }
}

void handleButtons() {
    // Debounce buttons
    if (millis() - lastButtonPress < 500) return;
    
    // Check enroll/auth button
    if (digitalRead(enrollButton) == LOW) {
        lastButtonPress = millis();
        enrollButtonPressed = true;
        
        if (currentMode == MODE_IDLE) {
            currentMode = MODE_AUTH;
            showMessage("AUTH Mode", "Place finger...");
            Serial.println(">>> AUTH MODE ACTIVATED <<<");
        }
    }
    
    // Check vote button
    if (digitalRead(voteButton) == LOW) {
        lastButtonPress = millis();
        voteButtonPressed = true;
        
        if (voterAuthenticated && currentMode == MODE_IDLE) {
            currentMode = MODE_VOTE;
            showMessage("VOTE Mode", "Loading elections");
            Serial.println(">>> VOTE MODE ACTIVATED <<<");
        } else if (!voterAuthenticated) {
            showMessage("Not Authenticated", "Use AUTH first");
            playSound("error");
            delay(2000);
        }
    }
}

void handleCurrentMode() {
    switch (currentMode) {
        case MODE_IDLE:
            if (!voterAuthenticated) {
                static unsigned long lastUpdate = 0;
                if (millis() - lastUpdate > 3000) {
                    showMessage("EVM Ready", "AUTH to start");
                    lastUpdate = millis();
                }
            } else {
                static unsigned long lastUpdate = 0;
                if (millis() - lastUpdate > 3000) {
                    showMessage("Hello " + currentVoterName, "Press VOTE");
                    lastUpdate = millis();
                }
            }
            break;
            
        case MODE_AUTH:
            handleAuthentication();
            break;
            
        case MODE_VOTE:
            handleVoting();
            break;
            
        case MODE_RESULTS:
            handleResults();
            break;
    }
}

void handleAuthentication() {
    static bool authInProgress = false;
    
    if (authInProgress) return;
    authInProgress = true;
    
    showMessage("Place finger", "for AUTH...");
    Serial.println("🔐 Starting Authentication");
    
    // Get fingerprint
    uint8_t fingerprintData[534];
    uint16_t templateSize = 0;
    
    if (captureFingerprint(fingerprintData, &templateSize)) {
        showMessage("Authenticating", "Please wait...");
        
        // Test with a demo Aadhar number (in production, get from user input)
        String aadharNumber = "123456789012";  // Demo Aadhar
        
        if (backend.authenticateVoter(aadharNumber, fingerprintData, templateSize)) {
            // Authentication successful
            currentVoterToken = backend.getAuthToken();
            voterAuthenticated = true;
            
            showMessage("AUTH Success!", "Welcome!");
            playSound("success");
            delay(2000);
            
            Serial.println("✅ Voter authenticated successfully!");
            
        } else {
            showMessage("AUTH Failed!", "Try again");
            playSound("error");
            delay(2000);
            Serial.println("❌ Authentication failed");
        }
    } else {
        showMessage("Fingerprint", "Error");
        playSound("error");
        delay(2000);
    }
    
    currentMode = MODE_IDLE;
    authInProgress = false;
}

void handleVoting() {
    static bool votingInProgress = false;
    
    if (votingInProgress) return;
    votingInProgress = true;
    
    // Get active elections
    showMessage("Loading", "Elections...");
    String electionsResponse = backend.getActiveElections();
    
    if (electionsResponse.length() > 10) {
        // Parse elections and show to user
        // For demo, we'll use a mock election ID
        activeElectionId = "demo-election-001";
        
        showMessage("Election Found", "Select candidate");
        delay(2000);
        
        // Show candidates (demo data)
        showCandidateSelection();
        
        // Get candidate selection from user
        if (getCandidateSelection()) {
            // Cast vote
            showMessage("Casting Vote", "Please wait...");
            
            if (backend.castVote(activeElectionId, selectedCandidateId, 0.95f)) {
                showMessage("Vote Cast!", "Thank you!");
                playSound("success");
                delay(3000);
                
                // Log out voter after voting
                logoutVoter();
                
                Serial.println("✅ Vote cast successfully!");
            } else {
                showMessage("Vote Failed!", "Try again");
                playSound("error");
                delay(2000);
                Serial.println("❌ Vote casting failed");
            }
        }
    } else {
        showMessage("No Elections", "Available");
        delay(2000);
    }
    
    currentMode = MODE_IDLE;
    votingInProgress = false;
}

void handleResults() {
    showMessage("Election", "Results");
    delay(1000);
    
    // For demo, show mock results
    showMessage("Candidate A: 45%", "Candidate B: 55%");
    delay(3000);
    
    showMessage("Results shown", "Press any key");
    
    // Wait for button press
    while (digitalRead(enrollButton) == HIGH && digitalRead(voteButton) == HIGH) {
        delay(100);
    }
    
    currentMode = MODE_IDLE;
}

bool captureFingerprint(uint8_t* templateData, uint16_t* templateSize) {
    Serial.println("📷 Capturing fingerprint...");
    
    // Wait for finger
    int p = -1;
    unsigned long startTime = millis();
    while (p != FINGERPRINT_OK && (millis() - startTime) < 15000) {
        p = finger.getImage();
        if (p == FINGERPRINT_OK) break;
        delay(50);
    }
    
    if (p != FINGERPRINT_OK) {
        Serial.println("❌ Timeout waiting for finger");
        return false;
    }
    
    // Convert to template
    p = finger.image2Tz(1);
    if (p != FINGERPRINT_OK) {
        Serial.println("❌ Failed to convert image");
        return false;
    }
    
    // Get template data (mock implementation)
    // In real implementation, extract actual template data from sensor
    for (int i = 0; i < 534; i++) {
        templateData[i] = random(0, 256);  // Mock data for demo
    }
    *templateSize = 534;
    
    Serial.println("✅ Fingerprint captured successfully");
    return true;
}

void showCandidateSelection() {
    // Demo candidate selection
    showMessage("1. Candidate A", "2. Candidate B");
    delay(2000);
    showMessage("3. Candidate C", "Select by button");
    delay(2000);
}

bool getCandidateSelection() {
    showMessage("Select:", "Press VOTE=A");
    delay(1000);
    showMessage("or AUTH=B", "or both=C");
    
    unsigned long startTime = millis();
    while (millis() - startTime < 30000) {  // 30 second timeout
        if (digitalRead(voteButton) == LOW && digitalRead(enrollButton) == HIGH) {
            selectedCandidateId = "candidate-a";
            showMessage("Selected:", "Candidate A");
            delay(1500);
            return true;
        } else if (digitalRead(enrollButton) == LOW && digitalRead(voteButton) == HIGH) {
            selectedCandidateId = "candidate-b";
            showMessage("Selected:", "Candidate B");
            delay(1500);
            return true;
        } else if (digitalRead(enrollButton) == LOW && digitalRead(voteButton) == LOW) {
            selectedCandidateId = "candidate-c";
            showMessage("Selected:", "Candidate C");
            delay(1500);
            return true;
        }
        delay(100);
    }
    
    showMessage("Selection", "Timeout");
    delay(2000);
    return false;
}

void logoutVoter() {
    backend.logout();
    voterAuthenticated = false;
    currentVoterToken = "";
    currentVoterName = "";
    currentVoterId = "";
    
    showMessage("Logged Out", "Thank you!");
    playSound("success");
    delay(2000);
    
    Serial.println("🚪 Voter logged out");
}

void showMessage(String line1, String line2) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print(line1.substring(0, 16));
    if (line2.length() > 0) {
        lcd.setCursor(0, 1);
        lcd.print(line2.substring(0, 16));
    }
}

void playSound(String type) {
    if (type == "error") {
        digitalWrite(buzzerPin, HIGH);
        delay(200);
        digitalWrite(buzzerPin, LOW);
        delay(100);
        digitalWrite(buzzerPin, HIGH);
        delay(200);
        digitalWrite(buzzerPin, LOW);
    } else if (type == "success") {
        digitalWrite(buzzerPin, HIGH);
        delay(500);
        digitalWrite(buzzerPin, LOW);
    } else if (type == "beep") {
        digitalWrite(buzzerPin, HIGH);
        delay(100);
        digitalWrite(buzzerPin, LOW);
    }
}

void showReadyScreen() {
    if (systemReady) {
        showMessage("EVM System", "Ready for Use");
        Serial.println("🚀 EVM System Ready!");
        Serial.println("Commands: AUTH, VOTE, RESULTS, STATUS, LOGOUT");
        delay(2000);
    }
}

void printSystemStatus() {
    Serial.println("\n=== 📊 EVM SYSTEM STATUS ===");
    Serial.println("WiFi: " + String(WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected"));
    Serial.println("IP Address: " + WiFi.localIP().toString());
    Serial.println("Backend: " + String(backend.isConnected() ? "Connected" : "Disconnected"));
    Serial.println("Device ID: " + backend.getDeviceId());
    Serial.println("Voter Authenticated: " + String(voterAuthenticated ? "Yes" : "No"));
    if (voterAuthenticated) {
        Serial.println("Voter Name: " + currentVoterName);
        Serial.println("Token: " + currentVoterToken.substring(0, 10) + "...");
    }
    Serial.print("Current Mode: ");
    switch (currentMode) {
        case MODE_IDLE: Serial.println("IDLE"); break;
        case MODE_AUTH: Serial.println("AUTH"); break;
        case MODE_VOTE: Serial.println("VOTE"); break;
        case MODE_RESULTS: Serial.println("RESULTS"); break;
    }
    Serial.println("Free Heap: " + String(ESP.getFreeHeap()) + " bytes");
    Serial.println("========================\n");
}