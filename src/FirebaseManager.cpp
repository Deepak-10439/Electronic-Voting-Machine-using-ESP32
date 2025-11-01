#include "FirebaseManager.h"

FirebaseManager::FirebaseManager() {
    wifiConnected = false;
}

bool FirebaseManager::connectWiFi(const char* ssid, const char* password) {
    Serial.println("Connecting to WiFi...");
    WiFi.begin(ssid, password);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.println("\nWiFi Connected!");
        Serial.print("IP Address: ");
        Serial.println(WiFi.localIP());
        wifiConnected = true;
        return true;
    } else {
        Serial.println("\nWiFi Connection Failed!");
        wifiConnected = false;
        return false;
    }
}

bool FirebaseManager::initialize(const char* ssid, const char* password, const char* functionUrl) {
    cloudFunctionUrl = String(functionUrl);
    return connectWiFi(ssid, password);
}

bool FirebaseManager::isConnected() {
    return (WiFi.status() == WL_CONNECTED);
}

bool FirebaseManager::sendPostRequest(String url, String payload, String& response) {
    if (!isConnected()) {
        Serial.println("WiFi not connected!");
        return false;
    }
    
    HTTPClient http;
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    
    int httpCode = http.POST(payload);
    
    if (httpCode > 0) {
        response = http.getString();
        Serial.print("HTTP Response code: ");
        Serial.println(httpCode);
        http.end();
        return (httpCode == 200 || httpCode == 201);
    } else {
        Serial.print("HTTP POST Error: ");
        Serial.println(httpCode);
        http.end();
        return false;
    }
}

bool FirebaseManager::sendGetRequest(String url, String& response) {
    if (!isConnected()) {
        Serial.println("WiFi not connected!");
        return false;
    }
    
    HTTPClient http;
    http.begin(url);
    
    int httpCode = http.GET();
    
    if (httpCode > 0) {
        response = http.getString();
        Serial.print("HTTP Response code: ");
        Serial.println(httpCode);
        http.end();
        return (httpCode == 200);
    } else {
        Serial.print("HTTP GET Error: ");
        Serial.println(httpCode);
        http.end();
        return false;
    }
}

bool FirebaseManager::uploadTemplate(String voterId, String templateB64, uint16_t sensorId) {
    StaticJsonDocument<2048> doc;
    doc["voter_id"] = voterId;
    doc["template_b64"] = templateB64;
    doc["sensor_id"] = sensorId;
    doc["action"] = "upload_template";
    
    String payload;
    serializeJson(doc, payload);
    
    String response;
    String url = cloudFunctionUrl + "/uploadTemplate";
    
    bool success = sendPostRequest(url, payload, response);
    
    if (success) {
        Serial.println("✓ Template uploaded to Firestore");
    } else {
        Serial.println("✗ Template upload failed");
    }
    
    return success;
}

bool FirebaseManager::uploadVoterRecord(String voterId, String name, uint16_t sensorId, String location) {
    StaticJsonDocument<1024> doc;
    doc["voter_id"] = voterId;
    doc["name"] = name;
    doc["sensor_id"] = sensorId;
    doc["location"] = location;
    doc["has_voted"] = false;
    doc["action"] = "upload_voter";
    
    String payload;
    serializeJson(doc, payload);
    
    String response;
    String url = cloudFunctionUrl + "/uploadVoter";
    
    bool success = sendPostRequest(url, payload, response);
    
    if (success) {
        Serial.println("✓ Voter record uploaded to Firestore");
    } else {
        Serial.println("✗ Voter record upload failed");
    }
    
    return success;
}

bool FirebaseManager::updateVoteStatus(String voterId, bool hasVoted) {
    StaticJsonDocument<512> doc;
    doc["voter_id"] = voterId;
    doc["has_voted"] = hasVoted;
    doc["action"] = "update_vote";
    
    String payload;
    serializeJson(doc, payload);
    
    String response;
    String url = cloudFunctionUrl + "/updateVote";
    
    bool success = sendPostRequest(url, payload, response);
    
    if (success) {
        Serial.println("✓ Vote status updated in Firestore");
    } else {
        Serial.println("✗ Vote status update failed");
    }
    
    return success;
}

bool FirebaseManager::hasVotedAlready(String voterId) {
    String url = cloudFunctionUrl + "/checkVote?voter_id=" + voterId;
    String response;
    
    if (sendGetRequest(url, response)) {
        StaticJsonDocument<512> doc;
        DeserializationError error = deserializeJson(doc, response);
        
        if (!error) {
            return doc["has_voted"] | false;
        }
    }
    
    return false;
}

bool FirebaseManager::getVoterInfo(String voterId, String& name, uint16_t& sensorId) {
    String url = cloudFunctionUrl + "/getVoter?voter_id=" + voterId;
    String response;
    
    if (sendGetRequest(url, response)) {
        StaticJsonDocument<512> doc;
        DeserializationError error = deserializeJson(doc, response);
        
        if (!error) {
            name = doc["name"] | "";
            sensorId = doc["sensor_id"] | 0;
            return true;
        }
    }
    
    return false;
}

bool FirebaseManager::downloadTemplate(String voterId, String& templateB64) {
    String url = cloudFunctionUrl + "/getTemplate?voter_id=" + voterId;
    String response;
    
    if (sendGetRequest(url, response)) {
        StaticJsonDocument<2048> doc;
        DeserializationError error = deserializeJson(doc, response);
        
        if (!error) {
            templateB64 = doc["template_b64"] | "";
            return true;
        }
    }
    
    return false;
}

int FirebaseManager::getTotalVoteCount() {
    String url = cloudFunctionUrl + "/getVoteCount";
    String response;
    
    if (sendGetRequest(url, response)) {
        StaticJsonDocument<256> doc;
        DeserializationError error = deserializeJson(doc, response);
        
        if (!error) {
            return doc["count"] | 0;
        }
    }
    
    return -1;
}
