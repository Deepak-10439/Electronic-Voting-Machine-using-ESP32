#ifndef BACKENDMANAGER_H
#define BACKENDMANAGER_H

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Adafruit_Fingerprint.h>
#include <Base64.h>

/**
 * BackendManager Class
 * Handles all communication with Django REST API backend
 * Replaces Firebase functionality for secure blockchain voting
 */
class BackendManager {
private:
    String apiBaseUrl;
    String authToken;
    String deviceId;
    bool isAuthenticated;
    
    // HTTP client for API requests
    HTTPClient http;
    
    // Helper functions
    String makeHttpRequest(String endpoint, String method = "GET", String payload = "");
    String encodeFingerprint(uint8_t* templateBuffer, uint16_t templateSize);
    bool parseJsonResponse(String response, DynamicJsonDocument& doc);
    void logRequest(String endpoint, String method, int statusCode);

public:
    BackendManager(String serverUrl, String devId);
    ~BackendManager();
    
    // Core functionality
    bool begin();
    bool connectWiFi(const char* ssid, const char* password);
    
    // Authentication
    bool authenticateVoter(String aadharNumber, uint8_t* fingerprintTemplate, uint16_t templateSize);
    bool registerVoter(String username, String email, String password, 
                      String firstName, String lastName, String aadharNumber,
                      String phoneNumber, String address, String dateOfBirth,
                      uint8_t* fingerprintTemplate, uint16_t templateSize);
    
    // Voting operations
    String getActiveElections();
    String getCandidates(String electionId);
    bool castVote(String electionId, String candidateId, float fingerprintMatchScore);
    String verifyVote(String voteId);
    String getElectionResults(String electionId);
    
    // System operations
    bool syncSystemTime();
    String getSystemTime();
    bool healthCheck();
    String getBlockchainStatus();
    
    // Utility functions
    void setAuthToken(String token);
    String getAuthToken();
    String getDeviceId();
    bool isConnected();
    void logout();
    
    // Error handling
    String getLastError();
    int getLastHttpCode();
};

#endif