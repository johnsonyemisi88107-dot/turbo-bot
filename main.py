from flask import Flask
from threading import Thread
import os, time, requests, threading, datetime
from telegram.ext import ApplicationBuilder

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@SunnyCryptoDJVIP"
COINS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT"]
TF_SETTINGS = {"15m":{"dip_pct":0.001,"tp":0.02,"sl":0.01},"1h":{"dip_pct":0.005,"tp":0.04,"sl":0.02},"4h":{"dip_pct":0.01,"tp":0.08,"sl":0.04}}
SESSIONS = {"MORNING":{"hours":(8,12),"tfs":["15m","1h"]},"AFTERNOON":{"hours":(12,17),"tfs":["1h","4h"]},"EVENING":{"hours":(17,22),"tfs":["15m","1h"]},"NIGHT":{"hours":(22,8),"tfs":["1h"]},"SLEEP":{"hours":(0,0),"tfs":[]}}

def get_dj_time():
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=3)

def get_session():
    h=get_dj_time().hour
    for name,s in SESSIONS.items():
        st,en=s["hours"]
        if st<en:
            if st<=h<en: return name,s
        else:
            if h>=st or h<en: return name,s
    return "SLEEP",SESSIONS["SLEEP"]

def send_channel_msg(text):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id":CHANNEL_ID,"text":text,"parse_mode":"HTML"})
    except: pass

def check_coins():
    session_name, session_data = get_session()
    tfs = session_data["tfs"]
    for coin in COINS:
        for tf in tfs:
            time.sleep(1)
    print(f"Checked {session_name}")

def run_bot():
    while True:
        try:
            check_coins()
            time.sleep(60)
        except Exception as e:
            print(e)
            time.sleep(10)

app = Flask('')
@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    run_bot()
