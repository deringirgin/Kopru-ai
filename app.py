from flask import Flask, request
import os, requests

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

def send_whatsapp(to, text):
    url = f"https://graph.facebook.com/v25.0/{os.getenv('PHONE_NUMBER_ID')}/messages"
    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_TOKEN')}",
        "Content-Type": "application/json",
    }
    body = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    r = requests.post(url, headers=headers, json=body, timeout=10)
    print("Gonderim:", r.status_code, r.text)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Yeni mesaj:", data)
    try:
        value = data["entry"][0]["changes"][0]["value"]
        for msg in value.get("messages", []):
            if msg.get("type") == "text":
                gelen = msg["text"]["body"]
                send_whatsapp(msg["from"], "Merhaba! Ben Köprü AI. Mesajın bana ulaştı: " + gelen)
    except Exception as e:
        print("Hata:", e)
    return "EVENT_RECEIVED", 200 import Flask,

