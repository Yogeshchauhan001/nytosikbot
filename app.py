# app.py (For Render.com hosting)
from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "AAHZTxXTKrKAyOxNsJXJjM9uOPOF6g8ErJ0")
ADMIN_ID = os.environ.get("ADMIN_ID", "@Nytosik")
USERS_FILE = "users.json"

def get_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_user(user_id, username=""):
    users = get_users()
    if user_id not in [u['id'] for u in users]:
        users.append({"id": user_id, "username": username})
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)
        return True
    return False

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{AAHZTxXTKrKAyOxNsJXJjM9uOPOF6g8ErJ0}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    try:
        return requests.post(url, json=payload, timeout=10).json()
    except:
        return None

@app.route('/')
def home():
    users = get_users()
    return f"""
    <h1>📢 Bulk Messaging Bot</h1>
    <p>Total Subscribers: <b>{len(users)}</b></p>
    <p>Status: ✅ Active</p>
    """

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    
    if "message" not in update:
        return jsonify({"ok": True})
    
    message = update["message"]
    chat_id = str(message["chat"]["id"])
    user = message.get("from", {})
    username = user.get("username", "")
    first_name = user.get("first_name", "User")
    text = message.get("text", "")
    
    # /start
    if text == "/start":
        save_user(chat_id, username)
        welcome = f"👋 <b>Welcome {first_name}!</b>\n\n✅ Aap ab subscribed ho!\n📢 Latest updates yahan milenge."
        send_message(chat_id, welcome)
        return jsonify({"ok": True})
    
    # Admin broadcast
    if text.startswith("/broadcast") and chat_id == ADMIN_ID:
        msg = text.replace("/broadcast", "").strip()
        if msg:
            users = get_users()
            sent = 0
            for u in users:
                if send_message(u['id'], msg):
                    sent += 1
            send_message(chat_id, f"📢 Broadcast: {sent}/{len(users)} sent!")
        return jsonify({"ok": True})
    
    # Status
    if text == "/status" and chat_id == ADMIN_ID:
        users = get_users()
        send_message(chat_id, f"👥 Total Users: {len(users)}")
        return jsonify({"ok": True})
    
    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
