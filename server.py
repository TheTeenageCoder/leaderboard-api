from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = 'data.json'

# -------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------
def load_data():
    if not os.path.exists(DATA_FILE) or os.path.getsize(DATA_FILE) == 0:
        data = {"users": {}, "scores": {}}
        save_data(data)
        return data
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    if "users" not in data:
        data["users"] = {}
    if "scores" not in data:
        data["scores"] = {}
    return data

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# -------------------------------------------------------------------
# API Routes
# -------------------------------------------------------------------

@app.route('/register', methods=['POST'])
def register():
    data = load_data()
    info = request.get_json()
    username = info.get('username')
    password = info.get('password')

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    if username in data["users"]:
        return jsonify({"success": False, "message": "Username already exists"}), 400

    data["users"][username] = {
        "password": password,
        "levels": {},
        "total_score": 0
    }
    save_data(data)
    return jsonify({"success": True, "message": "Account created"}), 201


@app.route('/login', methods=['POST'])
def login():
    data = load_data()
    info = request.get_json()
    username = info.get('username')
    password = info.get('password')

    user = data["users"].get(username)
    if not user or user['password'] != password:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    return jsonify({"success": True, "message": "Login successful"}), 200


@app.route('/submit_score', methods=['POST'])
def submit_score():
    data = load_data()
    info = request.get_json()

    username = info.get('username')
    level = str(info.get('level'))  # always store as string
    score = info.get('score')

    if not username or level is None or score is None:
        return jsonify({"success": False, "message": "Missing data"}), 400

    if username not in data:
        return jsonify({"success": False, "message": "User not found"}), 404

    user = data[username]

    # ✅ Only accept the score if it's higher than the existing one
    prev_score = user['levels'].get(level, 0)
    if score > prev_score:
        user['levels'][level] = score
        # Recalculate total (sum of all levels)
        user['total_score'] = sum(user['levels'].values())
        data[username] = user
        save_data(data)
        return jsonify({"success": True, "message": f"Score updated: {prev_score} → {score}"}), 200
    else:
        return jsonify({"success": False, "message": f"Score {score} not higher than current {prev_score}"}), 400



@app.route('/leaderboard', methods=['GET'])
def leaderboard_total():
    data = load_data()
    leaderboard = [
        {"username": u, "total_score": info.get('total_score', 0)}
        for u, info in data["users"].items()
    ]
    leaderboard.sort(key=lambda x: x["total_score"], reverse=True)
    return jsonify(leaderboard), 200


@app.route('/leaderboard/<int:level>', methods=['GET'])
def leaderboard_level(level):
    data = load_data()
    level = str(level)
    leaderboard = []
    for u, info in data["users"].items():
        score = info["levels"].get(level)
        if score is not None:
            leaderboard.append({"username": u, "score": score})
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    return jsonify(leaderboard), 200


@app.route('/user/<username>', methods=['GET'])
def get_user(username):
    data = load_data()

    if username not in data["users"]:
        return jsonify({"success": False, "message": "User not found"}), 404

    user = data["users"][username]
    return jsonify({
        "username": username,
        "levels": user.get("levels", {}),
        "total_score": user.get("total_score", 0)
    }), 200


@app.route("/remove_user", methods=["DELETE"])
def remove_user():
    data = load_data()
    content = request.get_json()

    username = content.get("username")
    password = content.get("password")

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password required"}), 400

    if username not in data["users"]:
        return jsonify({"success": False, "message": "User not found"}), 404

    if data["users"][username]["password"] != password:
        return jsonify({"success": False, "message": "Incorrect password"}), 401

    del data["users"][username]
    save_data(data)
    return jsonify({"success": True, "message": f"User '{username}' removed successfully"})


@app.route("/reset_data", methods=["POST"])
def reset_data():
    content = request.get_json() or {}
    secret = content.get("secret")

    if secret != "admin123":
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    data = {"users": {}, "scores": {}}
    save_data(data)
    return jsonify({"success": True, "message": "Data reset successfully"})


if __name__ == '__main__':
    app.run(debug=True)
