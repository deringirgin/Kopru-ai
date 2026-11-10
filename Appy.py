from flask import Flask, request
import os, requests

app = Flask(__name__)

MODEL = "claude-haiku-5-5"

SISTEM = """Sen Değer Akademisi'nin WhatsApp asistanısın.
Değer Akademisi, Köprü Metodu üzerine kurulu eğitim ve seminerler düzenler.
Kurallar:
- Türkçe, kısa (en fazla 3-4 cümle), sıcak ve net cevap ver.
- Seminerleri ve Köprü Metodu'nu tanıt, kişiyi seminere yönlendir.
- Fiyat, tarih ve yer bilgisini bilmiyorsan uydurma. "Ekibimiz size en kısa sürede dönecek" de.
- [BURAYA seminer tarihi, fiyat, yer, iletişim bilgilerini yaz]
"""

gecmis = {}

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

def claude_cevap(numara, metin):
    liste = gecmis.setdefault(numara, [])
    liste.append({"role": "user", "content": metin})
    del liste[:-10]
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={"model": MODEL, "max_tokens": 400,
                  "system": SISTEM, "messages": liste},
            timeout=25,
        )
        cevap = r.json()["content"][0]["text"]
        liste.append({"role": "assistant", "content": cevap})
        return cevap
    except Exception as e:
        print("Claude hatasi:", e)
        liste.pop()
        return "Şu an cevap veremiyorum, ekibimiz size en kısa sürede dönecek."

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
                cevap = claude_cevap(msg["from"], msg["text"]["body"])
                send_whatsapp(msg["from"], cevap)
    except Exception as e:
        print("Hata:", e)
    return "EVENT_RECEIVED", 200
