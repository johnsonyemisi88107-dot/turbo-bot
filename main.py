import os, time, requests, pytz
from datetime import datetime
from threading import Thread
from flask import Flask

app = Flask(__name__)

# SUPPORT BOTH NAMES - FIXES YOUR ERROR!
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("CHANNEL_ID") or "-1004491702289"

COINS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","DOGEUSDT","ADAUSDT","AVAXUSDT","DOTUSDT","LINKUSDT","LTCUSDT","BCHUSDT","UNIUSDT","XLMUSDT","ETCUSDT","FILUSDT","TRXUSDT","APTUSDT","NEARUSDT","ATOMUSDT","ARBUSDT","OPUSDT","SUIUSDT","SEIUSDT","PEPEUSDT","SHIBUSDT","ZECUSDT","HYPEUSDT","WIFUSDT","BONKUSDT","TIAUSDT","PYTHUSDT","JUPUSDT","RENDERUSDT"]

def get_dj_time():
    dj = pytz.timezone("Africa/Djibouti")
    return datetime.now(dj).strftime("%H:%M:%S DJ")

def send_msg(t):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": t, "parse_mode": "HTML"}, timeout=15)
        print(f"SEND {r.status_code} {r.text}")
        return r.text
    except Exception as e:
        print(f"Error {e}")
        return str(e)

@app.route("/")
def home():
    return f"ULTRA 85% 35 COINS | {get_dj_time()} | LIVE | ZEC+HYPE | ID {CHAT_ID}"

@app.route("/debug")
def debug():
    result = send_msg(f"🔧 DEBUG TEST {get_dj_time()}\nBot working! ID {CHAT_ID}")
    return f"<h1>DEBUG</h1>TOKEN: {'YES' if BOT_TOKEN else 'NO'}<br>CHAT_ID: {CHAT_ID}<br>TIME: {get_dj_time()}<br><hr>Result: {result}<hr>Check Telegram NOW!"

@app.route("/force-active")
def force():
    result = send_msg(f"🚀 <b>FORCE ACTIVE</b>\nTime: {get_dj_time()}\n35 Coins including ZEC+HYPE\nBot is LIVE!")
    return f"Forced! {result} - Check Telegram!"

def loop():
    while True:
        try:
            print(f"Heartbeat {get_dj_time()}")
            time.sleep(60)
        except Exception as e:
            print(e)
            time.sleep(10)

Thread(target=loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
