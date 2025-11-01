// Firebase Cloud Functions for EVM System
// Deploy this to Firebase Cloud Functions to handle ESP32 requests

const functions = require("firebase-functions");
const admin = require("firebase-admin");
admin.initializeApp();

const db = admin.firestore();

// Main handler for all EVM requests
exports.evmHandler = functions.https.onRequest(async (req, res) => {
  // Enable CORS
  res.set("Access-Control-Allow-Origin", "*");
  res.set("Access-Control-Allow-Methods", "GET, POST");
  res.set("Access-Control-Allow-Headers", "Content-Type");

  if (req.method === "OPTIONS") {
    res.status(204).send("");
    return;
  }

  const path = req.path || "/";

  try {
    // Route requests based on path
    if (path.includes("/uploadTemplate")) {
      await uploadTemplate(req, res);
    } else if (path.includes("/uploadVoter")) {
      await uploadVoter(req, res);
    } else if (path.includes("/updateVote")) {
      await updateVote(req, res);
    } else if (path.includes("/checkVote")) {
      await checkVote(req, res);
    } else if (path.includes("/getVoter")) {
      await getVoter(req, res);
    } else if (path.includes("/getTemplate")) {
      await getTemplate(req, res);
    } else if (path.includes("/getVoteCount")) {
      await getVoteCount(req, res);
    } else {
      res.status(404).send("Endpoint not found");
    }
  } catch (error) {
    console.error("Error:", error);
    res.status(500).send("Internal Server Error");
  }
});

// Upload fingerprint template to Firestore
async function uploadTemplate(req, res) {
  try {
    const { voter_id, template_b64, sensor_id } = req.body;

    if (!voter_id || !template_b64) {
      res.status(400).send("Missing parameters");
      return;
    }

    const docRef = db.collection("fingerprint_templates").doc(voter_id);

    await docRef.set({
      voter_id: voter_id,
      template_b64: template_b64,
      sensor_id: sensor_id || 0,
      uploaded_at: admin.firestore.FieldValue.serverTimestamp(),
    });

    res.status(200).json({
      success: true,
      message: "Template stored securely",
    });
  } catch (error) {
    console.error("uploadTemplate error:", error);
    res.status(500).send("Error uploading template");
  }
}

// Upload voter record
async function uploadVoter(req, res) {
  try {
    const { voter_id, name, sensor_id, location } = req.body;

    if (!voter_id || !name) {
      res.status(400).send("Missing parameters");
      return;
    }

    const docRef = db.collection("voters").doc(voter_id);

    await docRef.set({
      voter_id: voter_id,
      name: name,
      sensor_id: sensor_id || 0,
      location: location || "Unknown",
      has_voted: false,
      enrolled_at: admin.firestore.FieldValue.serverTimestamp(),
      voted_at: null,
    });

    res.status(200).json({
      success: true,
      message: "Voter record created",
    });
  } catch (error) {
    console.error("uploadVoter error:", error);
    res.status(500).send("Error uploading voter record");
  }
}

// Update vote status
async function updateVote(req, res) {
  try {
    const { voter_id, has_voted } = req.body;

    if (!voter_id) {
      res.status(400).send("Missing voter_id");
      return;
    }

    const docRef = db.collection("voters").doc(voter_id);
    const doc = await docRef.get();

    if (!doc.exists) {
      res.status(404).send("Voter not found");
      return;
    }

    await docRef.update({
      has_voted: has_voted,
      voted_at: has_voted ? admin.firestore.FieldValue.serverTimestamp() : null,
    });

    // Increment vote count
    if (has_voted) {
      const countRef = db.collection("vote_counts").doc("total");
      await countRef.set(
        {
          count: admin.firestore.FieldValue.increment(1),
          last_updated: admin.firestore.FieldValue.serverTimestamp(),
        },
        { merge: true }
      );
    }

    res.status(200).json({
      success: true,
      message: "Vote status updated",
    });
  } catch (error) {
    console.error("updateVote error:", error);
    res.status(500).send("Error updating vote status");
  }
}

// Check if voter has already voted
async function checkVote(req, res) {
  try {
    const voter_id = req.query.voter_id;

    if (!voter_id) {
      res.status(400).send("Missing voter_id");
      return;
    }

    const docRef = db.collection("voters").doc(voter_id);
    const doc = await docRef.get();

    if (!doc.exists) {
      res.status(404).json({
        found: false,
        has_voted: false,
      });
      return;
    }

    const data = doc.data();
    res.status(200).json({
      found: true,
      has_voted: data.has_voted || false,
      voted_at: data.voted_at,
    });
  } catch (error) {
    console.error("checkVote error:", error);
    res.status(500).send("Error checking vote status");
  }
}

// Get voter information
async function getVoter(req, res) {
  try {
    const voter_id = req.query.voter_id;

    if (!voter_id) {
      res.status(400).send("Missing voter_id");
      return;
    }

    const docRef = db.collection("voters").doc(voter_id);
    const doc = await docRef.get();

    if (!doc.exists) {
      res.status(404).send("Voter not found");
      return;
    }

    const data = doc.data();
    res.status(200).json({
      voter_id: data.voter_id,
      name: data.name,
      sensor_id: data.sensor_id,
      location: data.location,
      has_voted: data.has_voted,
    });
  } catch (error) {
    console.error("getVoter error:", error);
    res.status(500).send("Error getting voter info");
  }
}

// Get fingerprint template
async function getTemplate(req, res) {
  try {
    const voter_id = req.query.voter_id;

    if (!voter_id) {
      res.status(400).send("Missing voter_id");
      return;
    }

    const docRef = db.collection("fingerprint_templates").doc(voter_id);
    const doc = await docRef.get();

    if (!doc.exists) {
      res.status(404).send("Template not found");
      return;
    }

    const data = doc.data();
    res.status(200).json({
      voter_id: data.voter_id,
      template_b64: data.template_b64,
      sensor_id: data.sensor_id,
    });
  } catch (error) {
    console.error("getTemplate error:", error);
    res.status(500).send("Error getting template");
  }
}

// Get total vote count
async function getVoteCount(req, res) {
  try {
    const countRef = db.collection("vote_counts").doc("total");
    const doc = await countRef.get();

    if (!doc.exists) {
      res.status(200).json({
        count: 0,
      });
      return;
    }

    const data = doc.data();
    res.status(200).json({
      count: data.count || 0,
      last_updated: data.last_updated,
    });
  } catch (error) {
    console.error("getVoteCount error:", error);
    res.status(500).send("Error getting vote count");
  }
}

// Security Rules for Firestore (place in firebase rules)
/*
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Fingerprint templates - admin only
    match /fingerprint_templates/{voter_id} {
      allow read, write: if request.auth != null && request.auth.token.admin == true;
    }
    
    // Voter records - admin only
    match /voters/{voter_id} {
      allow read, write: if request.auth != null && request.auth.token.admin == true;
    }
    
    // Vote counts - read only for authenticated users
    match /vote_counts/{docId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && request.auth.token.admin == true;
    }
  }
}
*/
