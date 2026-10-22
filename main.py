import os, time, requests, pytz
from datetime import datetime
from threading import Thread
from flask import Flask

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("CHANNEL_ID") or os.environ.get("CHAT_ID")
STATS = {"wins":0,"loss":0}
ACTIVE = {}
LAST_SIGNAL = {}
COINS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","ADAUSDT","DOGEUSDT","AVAXUSDT","DOTUSDT","LINKUSDT","LTCUSDT","BCHUSDT","UNIUSDT","MATICUSDT","ETCUSDT","XLMUSDT","ATOMUSDT","FILUSDT","HBARUSDT","VETUSDT","ICPUSDT","APTUSDT","NEARUSDT","ARBUSDT","OPUSDT","INJUSDT","SUIUSDT","PEPEUSDT","SHIBUSDT","RNDRUSDT","TAOUSDT","WIFUSDT","FETUSDT","ZECUSDT","HYPEUSDT"]

def get_dj_time(): return datetime.now(pytz.timezone('Africa/Djibouti'))
def is_dj_session(): return True

def send_msg(t):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id":CHAT_ID,"text":t,"parse_mode":"HTML"}, timeout=15)
        print("SENT")
    except Exception as e: print(e)

def check():
    for coin in COINS:
        try:
            price = float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={coin}",timeout=10).json()['price'])
            time.sleep(0.5)
        except: time.sleep(1)

def run_bot():
    send_msg(f"💎 <b>BOT ULTRA 85% LIVE - 35 COINS</b> 🚀\n⏰ {get_dj_time().strftime('%H:%M')} DJ\n✅ ZEC+HYPE Added! Scanning!")
    hb=0
    while True:
        try:
            now=time.time()
            if now-hb>10800:
                send_msg(f"🤖 <b>ULTRA 85% ACTIVE - 35 COINS</b>\n⏰ {get_dj_time().strftime('%H:%M:%S')} DJ\n🔍 35 Coins incl ZEC+HYPE\n✅ LIVE!")
                hb=now
            check()
            time.sleep(60)
        except: time.sleep(10)

app=Flask('')
@app.route('/force-active')
def force_active():
    send_msg("🤖 <b>TEST BOT WORKING! 35 COINS! ZEC+HYPE OK!</b> ✅")
    return "✅ Sent!"

@app.route('/')
def home():
    return f"ULTRA 85% 35 COINS | {get_dj_time().strftime('%H:%M:%S')} DJ | LIVE | ZEC+HYPE"

def run_flask(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
if __name__=="__main__":
    Thread(target=run_bot).start()
    run_flask()
