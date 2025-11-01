# Configuration Examples for Different Scenarios

## Scenario 1: First Day - Enroll All Voters
```cpp
// #define MODE_VERIFY
#define MODE_ENROLL
// #define MODE_DELETE

#define ENROLL_START_ID 1
#define ENROLL_COUNT 50        // Enroll 50 voters
#define ENROLL_MANUAL false    // Auto-sequence
```

## Scenario 2: Voting Day - Normal Operation
```cpp
#define MODE_VERIFY            // Main voting mode
// #define MODE_ENROLL
// #define MODE_DELETE

#define VERIFY_CONFIDENCE_THRESHOLD 50
```

## Scenario 3: Add Single New Voter
```cpp
// #define MODE_VERIFY
#define MODE_ENROLL
// #define MODE_DELETE

#define ENROLL_MANUAL true     // Enter specific ID via Serial
```

## Scenario 4: Remove One Invalid Voter
```cpp
// #define MODE_VERIFY
// #define MODE_ENROLL
#define MODE_DELETE

#define DELETE_ID 23           // Remove voter #23
#define DELETE_MANUAL false
#define DELETE_ALL false
```

## Scenario 5: Testing - Enter IDs Interactively
```cpp
// #define MODE_VERIFY
#define MODE_ENROLL
// #define MODE_DELETE

#define ENROLL_MANUAL true     // Test with specific IDs
```

## Scenario 6: End of Election - Clear Database
```cpp
// #define MODE_VERIFY
// #define MODE_ENROLL
#define MODE_DELETE

#define DELETE_ALL true        // ⚠️ Deletes everything!
```

## Scenario 7: High Security Voting
```cpp
#define MODE_VERIFY
// #define MODE_ENROLL
// #define MODE_DELETE

#define VERIFY_CONFIDENCE_THRESHOLD 100  // Very strict matching
```

## Scenario 8: Quick Enrollment Demo
```cpp
// #define MODE_VERIFY
#define MODE_ENROLL
// #define MODE_DELETE

#define ENROLL_START_ID 1
#define ENROLL_COUNT 3         // Just 3 for testing
#define ENROLL_MANUAL false
```
