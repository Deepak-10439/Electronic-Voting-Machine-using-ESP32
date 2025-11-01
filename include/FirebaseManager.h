#ifndef FIREBASEMANAGER_H
#define FIREBASEMANAGER_H

#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

class FirebaseManager {
private:
    String firebaseHost;
    String firebaseApiKey;
    String cloudFunctionUrl;
    bool wifiConnected;
    
    bool connectWiFi(const char* ssid, const char* password);
    
public:
    FirebaseManager();
    
    // Initialize Firebase with credentials
    bool initialize(const char* ssid, const char* password, const char* functionUrl);
    
    // Check WiFi connection status
    bool isConnected();
    
    // Upload fingerprint template to Firestore
    bool uploadTemplate(String voterId, String templateB64, uint16_t sensorId);
    
    // Upload voter record without template
    bool uploadVoterRecord(String voterId, String name, uint16_t sensorId, String location);
    
    // Update vote status in Firestore
    bool updateVoteStatus(String voterId, bool hasVoted);
    
    // Check if voter has already voted
    bool hasVotedAlready(String voterId);
    
    // Get voter information
    bool getVoterInfo(String voterId, String& name, uint16_t& sensorId);
    
    // Download template from Firestore (if needed)
    bool downloadTemplate(String voterId, String& templateB64);
    
    // Get total vote count
    int getTotalVoteCount();
    
    // Send HTTP POST request
    bool sendPostRequest(String url, String payload, String& response);
    
    // Send HTTP GET request
    bool sendGetRequest(String url, String& response);
};

#endif
