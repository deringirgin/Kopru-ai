from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Kopru AI Server Aktif!"

@app.route("/health")
def health():
    return {"status": "online"}

@app.route("/webhook", methods=["GET"])
def verify():
    token = os.getenv("VERIFY_TOKEN")

    if request.args.get("hub.verify_token") == token:
        return request.args.get("hub.challenge")

    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Yeni mesaj:", data)
    return "EVENT_RECEIVED", 200
