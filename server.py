from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

DATA_FILE = 'data.json'

# -------------------------------------------------------------------
# Helper Functions
# -------------------------------------------------------------------
def load_data():
    if not os.path.exists("data.json") or os.path.getsize("data.json") == 0:
        # Create an empty default structure
        data = {"users": {}, "scores": {}}
        with open("data.json", "w") as f:
            json.dump(data, f)
        return data
    with open("data.json", "r") as f:
        return json.load(f)

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

    if username in data:
        return jsonify({"success": False, "message": "Username already exists"}), 400

    data[username] = {
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

    user = data.get(username)
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
    user['levels'][level] = score

    # Recalculate total (sum of all levels)
    user['total_score'] = sum(user['levels'].values())

    data[username] = user
    save_data(data)

    return jsonify({"success": True, "message": "Score submitted"}), 200


@app.route('/leaderboard', methods=['GET'])
def leaderboard_total():
    data = load_data()

    leaderboard = [
        {"username": user, "total_score": info.get('total_score', 0)}
        for user, info in data.items()
    ]

    leaderboard.sort(key=lambda x: x['total_score'], reverse=True)
    return jsonify(leaderboard), 200


@app.route('/leaderboard/<int:level>', methods=['GET'])
def leaderboard_level(level):
    data = load_data()
    level = str(level)

    leaderboard = []
    for user, info in data.items():
        score = info['levels'].get(level)
        if score is not None:
            leaderboard.append({"username": user, "score": score})

    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    return jsonify(leaderboard), 200


@app.route('/user/<username>', methods=['GET'])
def get_user(username):
    data = load_data()

    if username not in data:
        return jsonify({"success": False, "message": "User not found"}), 404

    user = data[username]
    return jsonify({
        "username": username,
        "levels": user.get('levels', {}),
        "total_score": user.get('total_score', 0)
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
