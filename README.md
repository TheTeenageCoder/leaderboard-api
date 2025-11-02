# 🏆 Leaderboard API

A lightweight REST API for managing users, per-level scores, and leaderboards.  
Built for easy integration with games (e.g. Godot).

---

## 🌐 Base URL
```
"Isesend k to sayo Jiro"
```

Replace with your actual Render deployment URL.

---

## 🔐 Authentication
No authentication required for now.  
All endpoints accept and return JSON.

---

## 📋 Endpoints

---

### **1️⃣ Register User**
**POST** `/register`

**Body:**
```json
{
  "username": "alice",
  "password": "1234"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Account created"
}
```

**Response (If user exists):**
```json
{
  "success": false,
  "message": "Username already exists"
}
```

---

### **2️⃣ Login**
**POST** `/login`

**Body:**
```json
{
  "username": "alice",
  "password": "1234"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Login successful"
}
```

**Response (Fail):**
```json
{
  "success": false,
  "message": "Invalid credentials"
}
```

---

### **3️⃣ Submit Score**
**POST** `/submit_score`

**Body:**
```json
{
  "username": "alice",
  "level": 1,
  "score": 300
}
```

**Behavior:**
- Updates score **only if it’s higher** than the existing one.
- Recalculates the user’s total score.

**Response (Improved):**
```json
{
  "success": true,
  "message": "Score updated: 0 → 300"
}
```

**Response (Lower score):**
```json
{
  "success": false,
  "message": "Score 200 not higher than current 300"
}
```

---

### **4️⃣ Get Total Leaderboard**
**GET** `/leaderboard`

**Response:**
```json
[
  { "username": "alice", "total_score": 800 },
  { "username": "bob", "total_score": 500 }
]
```

---

### **5️⃣ Get Leaderboard for a Level**
**GET** `/leaderboard/<level>`

Example:
```
/leaderboard/1
```

**Response:**
```json
[
  { "username": "alice", "score": 300 },
  { "username": "bob", "score": 200 }
]
```

---

### **6️⃣ Get User Data**
**GET** `/user/<username>`

Example:
```
/user/alice
```

**Response:**
```json
{
  "username": "alice",
  "levels": { "1": 300, "2": 500 },
  "total_score": 800
}
```

---

### **7️⃣ Remove User**
**DELETE** `/remove_user`

**Body:**
```json
{
  "username": "alice",
  "password": "1234"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User 'alice' removed successfully"
}
```

---

### **8️⃣ Reset All Data**
**POST** `/reset_data`

**Body:**
```json
{
  "secret": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Data reset successfully"
}
```

---

## 🧠 Data Structure

**data.json**
```json
{
  "alice": {
    "password": "1234",
    "levels": { "1": 300, "2": 500 },
    "total_score": 800
  },
  "bob": {
    "password": "abcd",
    "levels": { "1": 200 },
    "total_score": 200
  }
}
```

---

## ⚙️ Notes
- Scores can only increase per level (best score kept).  
- Total score = sum of all best scores.  
- `/reset_data` clears all users and scores (admin only).  
- No tokens or authentication yet — keep this private if possible.
