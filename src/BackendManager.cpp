/**
 * BackendManager Implementation
 * Secure Django REST API communication for ESP32 EVM
 * Replaces Firebase with blockchain-ready backend
 */

#include "BackendManager.h"

// Constructor
BackendManager::BackendManager(String serverUrl, String devId) {
    apiBaseUrl = serverUrl;
    deviceId = devId;
    authToken = "";
    isAuthenticated = false;
}

// Destructor
BackendManager::~BackendManager() {
    http.end();
}

// Initialize backend manager
bool BackendManager::begin() {
    Serial.println("🚀 Initializing Backend Manager");
    Serial.println("API Base URL: " + apiBaseUrl);
    Serial.println("Device ID: " + deviceId);
    
    // Test connectivity
    return healthCheck();
}

// Connect to WiFi
bool BackendManager::connectWiFi(const char* ssid, const char* password) {
    Serial.println("📡 Connecting to WiFi: " + String(ssid));
    
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\n✅ WiFi Connected!");
        Serial.println("IP Address: " + WiFi.localIP().toString());
        Serial.println("Signal Strength: " + String(WiFi.RSSI()) + " dBm");
        return true;
    } else {
        Serial.println("\n❌ WiFi Connection Failed");
        return false;
    }
}

// Authenticate voter with backend
bool BackendManager::authenticateVoter(String aadharNumber, uint8_t* fingerprintTemplate, uint16_t templateSize) {
    Serial.println("🔐 Authenticating Voter: " + aadharNumber);
    
    // Encode fingerprint template to hex
    String fingerprintHex = encodeFingerprint(fingerprintTemplate, templateSize);
    
    // Prepare authentication payload
    DynamicJsonDocument payload(2048);
    payload["device_id"] = deviceId;
    payload["aadhar_number"] = aadharNumber;
    payload["fingerprint_template"] = fingerprintHex;
    
    String payloadStr;
    serializeJson(payload, payloadStr);
    
    // Make authentication request
    String response = makeHttpRequest("/api/auth/", "POST", payloadStr);
    
    // Parse response
    DynamicJsonDocument responseDoc(1024);
    if (parseJsonResponse(response, responseDoc)) {
        if (responseDoc["success"] == true) {
            authToken = responseDoc["token"].as<String>();
            isAuthenticated = true;
            
            Serial.println("✅ Authentication Successful");
            Serial.println("Voter ID: " + responseDoc["voter_id"].as<String>());
            Serial.println("Voter Name: " + responseDoc["voter_name"].as<String>());
            Serial.println("Eligible: " + String(responseDoc["is_eligible"].as<bool>()));
            Serial.println("Fingerprint Similarity: " + String(responseDoc["fingerprint_similarity"].as<float>()));
            
            return true;
        } else {
            Serial.println("❌ Authentication Failed: " + responseDoc["error"].as<String>());
            return false;
        }
    }
    
    Serial.println("❌ Authentication Error: Invalid response");
    return false;
}

// Register new voter
bool BackendManager::registerVoter(String username, String email, String password,
                                  String firstName, String lastName, String aadharNumber,
                                  String phoneNumber, String address, String dateOfBirth,
                                  uint8_t* fingerprintTemplate, uint16_t templateSize) {
    
    Serial.println("📝 Registering New Voter: " + username);
    
    // Encode fingerprint template
    String fingerprintHex = encodeFingerprint(fingerprintTemplate, templateSize);
    
    // Prepare registration payload
    DynamicJsonDocument payload(3072);
    payload["username"] = username;
    payload["email"] = email;
    payload["password"] = password;
    payload["confirm_password"] = password;
    payload["first_name"] = firstName;
    payload["last_name"] = lastName;
    payload["aadhar_number"] = aadharNumber;
    payload["phone_number"] = phoneNumber;
    payload["address"] = address;
    payload["date_of_birth"] = dateOfBirth;
    payload["fingerprint_template"] = fingerprintHex;
    
    String payloadStr;
    serializeJson(payload, payloadStr);
    
    // Make registration request
    String response = makeHttpRequest("/api/register/", "POST", payloadStr);
    
    // Parse response
    DynamicJsonDocument responseDoc(1024);
    if (parseJsonResponse(response, responseDoc)) {
        if (responseDoc["success"] == true) {
            Serial.println("✅ Voter Registration Successful");
            Serial.println("Voter ID: " + responseDoc["voter_id"].as<String>());
            Serial.println("Blockchain Registered: " + String(responseDoc["blockchain_registered"].as<bool>()));
            return true;
        } else {
            Serial.println("❌ Registration Failed");
            JsonObject errors = responseDoc["errors"];
            for (JsonPair kv : errors) {
                Serial.println("Error in " + String(kv.key().c_str()) + ": " + kv.value().as<String>());
            }
            return false;
        }
    }
    
    Serial.println("❌ Registration Error: Invalid response");
    return false;
}

// Get active elections
String BackendManager::getActiveElections() {
    Serial.println("🗳️ Fetching Active Elections");
    
    if (!isAuthenticated) {
        Serial.println("❌ Not authenticated");
        return "{}";
    }
    
    String response = makeHttpRequest("/api/elections/", "GET");
    
    DynamicJsonDocument responseDoc(4096);
    if (parseJsonResponse(response, responseDoc)) {
        if (responseDoc["success"] == true) {
            Serial.println("✅ Elections Retrieved");
            JsonArray elections = responseDoc["elections"];
            Serial.println("Active Elections: " + String(elections.size()));
            
            for (JsonObject election : elections) {
                Serial.println("- " + election["name"].as<String>() + 
                              " (Type: " + election["election_type"].as<String>() + ")");
            }
        }
    }
    
    return response;
}

// Cast vote
bool BackendManager::castVote(String electionId, String candidateId, float fingerprintMatchScore) {
    Serial.println("🗳️ Casting Vote");
    Serial.println("Election: " + electionId);
    Serial.println("Candidate: " + candidateId);
    Serial.println("Fingerprint Score: " + String(fingerprintMatchScore));
    
    if (!isAuthenticated) {
        Serial.println("❌ Not authenticated");
        return false;
    }
    
    // Prepare vote payload
    DynamicJsonDocument payload(1024);
    payload["election_id"] = electionId;
    payload["candidate_id"] = candidateId;
    payload["device_id"] = deviceId;
    payload["fingerprint_match_score"] = fingerprintMatchScore;
    
    String payloadStr;
    serializeJson(payload, payloadStr);
    
    // Make vote request
    String response = makeHttpRequest("/api/vote/", "POST", payloadStr);
    
    // Parse response
    DynamicJsonDocument responseDoc(1024);
    if (parseJsonResponse(response, responseDoc)) {
        if (responseDoc["success"] == true) {
            Serial.println("✅ Vote Cast Successfully");
            Serial.println("Vote ID: " + responseDoc["vote_id"].as<String>());
            Serial.println("Blockchain Recorded: " + String(responseDoc["blockchain_recorded"].as<bool>()));
            if (responseDoc["transaction_hash"]) {
                Serial.println("TX Hash: " + responseDoc["transaction_hash"].as<String>());
            }
            return true;
        } else {
            Serial.println("❌ Vote Failed: " + responseDoc["error"].as<String>());
            return false;
        }
    }
    
    Serial.println("❌ Vote Error: Invalid response");
    return false;
}

// Verify vote
String BackendManager::verifyVote(String voteId) {
    Serial.println("🔍 Verifying Vote: " + voteId);
    
    if (!isAuthenticated) {
        Serial.println("❌ Not authenticated");
        return "{}";
    }
    
    String response = makeHttpRequest("/api/verify/" + voteId + "/", "GET");
    
    DynamicJsonDocument responseDoc(2048);
    if (parseJsonResponse(response, responseDoc)) {
        if (responseDoc["success"] == true) {
            Serial.println("✅ Vote Verification Complete");
            JsonObject voteDetails = responseDoc["vote_details"];
            Serial.println("Status: " + voteDetails["vote_status"].as<String>());
            if (voteDetails["blockchain_tx_hash"]) {
                Serial.println("TX Hash: " + voteDetails["blockchain_tx_hash"].as<String>());
            }
        }
    }
    
    return response;
}

// Get election results
String BackendManager::getElectionResults(String electionId) {
    Serial.println("📊 Fetching Election Results: " + electionId);
    
    String response = makeHttpRequest("/api/results/" + electionId + "/", "GET");
    
    DynamicJsonDocument responseDoc(4096);
    if (parseJsonResponse(response, responseDoc)) {
        if (responseDoc["success"] == true) {
            Serial.println("✅ Results Retrieved");
            JsonObject election = responseDoc["election"];
            Serial.println("Election: " + election["name"].as<String>());
            Serial.println("Total Votes: " + String(election["total_votes"].as<int>()));
            
            JsonArray results = responseDoc["results"];
            for (JsonObject candidate : results) {
                Serial.println("- " + candidate["name"].as<String>() + 
                              ": " + String(candidate["local_votes"].as<int>()) + " votes (" +
                              String(candidate["percentage"].as<float>()) + "%)");
            }
        }
    }
    
    return response;
}

// Sync system time
bool BackendManager::syncSystemTime() {
    Serial.println("⏰ Syncing System Time");
    
    String response = makeHttpRequest("/api/time/", "GET");
    
    DynamicJsonDocument responseDoc(512);
    if (parseJsonResponse(response, responseDoc)) {
        if (responseDoc["success"] == true) {
            long timestamp = responseDoc["timestamp"];
            Serial.println("✅ Time Synced: " + responseDoc["iso_time"].as<String>());
            // TODO: Set ESP32 RTC with timestamp
            return true;
        }
    }
    
    Serial.println("❌ Time Sync Failed");
    return false;
}

// Get system time
String BackendManager::getSystemTime() {
    String response = makeHttpRequest("/api/time/", "GET");
    return response;
}

// Health check
bool BackendManager::healthCheck() {
    Serial.println("🔍 Health Check");
    
    String response = makeHttpRequest("/api/health/", "GET");
    
    DynamicJsonDocument responseDoc(512);
    if (parseJsonResponse(response, responseDoc)) {
        if (responseDoc["status"] == "healthy") {
            Serial.println("✅ Backend Healthy");
            Serial.println("Version: " + responseDoc["version"].as<String>());
            return true;
        }
    }
    
    Serial.println("❌ Backend Unhealthy");
    return false;
}

// Get blockchain status
String BackendManager::getBlockchainStatus() {
    Serial.println("⛓️ Getting Blockchain Status");
    
    if (!isAuthenticated) {
        Serial.println("❌ Not authenticated");
        return "{}";
    }
    
    String response = makeHttpRequest("/api/blockchain/status/", "GET");
    
    DynamicJsonDocument responseDoc(1024);
    if (parseJsonResponse(response, responseDoc)) {
        if (responseDoc["success"] == true) {
            Serial.println("✅ Blockchain Status Retrieved");
            JsonObject status = responseDoc["blockchain_status"];
            Serial.println("Connected: " + String(status["connected"].as<bool>()));
            if (status["connected"]) {
                Serial.println("Network: " + status["network_id"].as<String>());
                Serial.println("Latest Block: " + String(status["latest_block"].as<int>()));
                Serial.println("Account Balance: " + String(status["account_balance"].as<float>()) + " ETH");
            }
        }
    }
    
    return response;
}

// Make HTTP request helper
String BackendManager::makeHttpRequest(String endpoint, String method, String payload) {
    http.begin(apiBaseUrl + endpoint);
    
    // Set headers
    http.addHeader("Content-Type", "application/json");
    http.addHeader("User-Agent", "ESP32-EVM-Client/1.0");
    
    // Add authentication token if available
    if (isAuthenticated && authToken.length() > 0) {
        http.addHeader("Authorization", "Token " + authToken);
    }
    
    // Add device ID header
    http.addHeader("X-Device-ID", deviceId);
    
    int httpCode;
    String response;
    
    // Make request based on method
    if (method == "GET") {
        httpCode = http.GET();
    } else if (method == "POST") {
        httpCode = http.POST(payload);
    } else if (method == "PUT") {
        httpCode = http.PUT(payload);
    } else if (method == "DELETE") {
        httpCode = http.sendRequest("DELETE");
    } else {
        httpCode = -1;
    }
    
    if (httpCode > 0) {
        response = http.getString();
    } else {
        response = "{\"error\":\"HTTP request failed\",\"code\":" + String(httpCode) + "}";
    }
    
    logRequest(endpoint, method, httpCode);
    http.end();
    
    return response;
}

// Encode fingerprint template to hex string
String BackendManager::encodeFingerprint(uint8_t* templateBuffer, uint16_t templateSize) {
    String hexString = "";
    for (uint16_t i = 0; i < templateSize; i++) {
        if (templateBuffer[i] < 16) {
            hexString += "0";
        }
        hexString += String(templateBuffer[i], HEX);
    }
    return hexString;
}

// Parse JSON response
bool BackendManager::parseJsonResponse(String response, DynamicJsonDocument& doc) {
    DeserializationError error = deserializeJson(doc, response);
    if (error) {
        Serial.println("JSON Parse Error: " + String(error.c_str()));
        return false;
    }
    return true;
}

// Log HTTP request
void BackendManager::logRequest(String endpoint, String method, int statusCode) {
    Serial.println("📡 " + method + " " + endpoint + " → " + String(statusCode));
    
    if (statusCode >= 200 && statusCode < 300) {
        // Success
    } else if (statusCode >= 400 && statusCode < 500) {
        Serial.println("⚠️ Client Error: " + String(statusCode));
    } else if (statusCode >= 500) {
        Serial.println("💥 Server Error: " + String(statusCode));
    } else {
        Serial.println("🔌 Connection Error: " + String(statusCode));
    }
}

// Utility functions
void BackendManager::setAuthToken(String token) {
    authToken = token;
    isAuthenticated = (token.length() > 0);
}

String BackendManager::getAuthToken() {
    return authToken;
}

String BackendManager::getDeviceId() {
    return deviceId;
}

bool BackendManager::isConnected() {
    return WiFi.status() == WL_CONNECTED;
}

void BackendManager::logout() {
    authToken = "";
    isAuthenticated = false;
    Serial.println("🚪 Logged out");
}

String BackendManager::getLastError() {
    // TODO: Implement error tracking
    return "Not implemented";
}

int BackendManager::getLastHttpCode() {
    // TODO: Store last HTTP code
    return 0;
}