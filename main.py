import os, time, requests, pytz
from datetime import datetime
from threading import Thread
from flask import Flask

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("CHANNEL_ID") or os.environ.get("CHAT_ID")
COINS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","ADAUSDT","DOGEUSDT","AVAXUSDT","DOTUSDT","LINKUSDT","LTCUSDT","BCHUSDT","UNIUSDT","MATICUSDT","ETCUSDT","XLMUSDT","ATOMUSDT","FILUSDT","HBARUSDT","VETUSDT","ICPUSDT","APTUSDT","NEARUSDT","ARBUSDT","OPUSDT","INJUSDT","SUIUSDT","PEPEUSDT","SHIBUSDT","RNDRUSDT","TAOUSDT","WIFUSDT","FETUSDT","ZECUSDT","HYPEUSDT"]

def get_dj_time(): return datetime.now(pytz.timezone('Africa/Djibouti'))

def send_msg(t):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id":CHAT_ID,"text":t,"parse_mode":"HTML"}, timeout=15)
        print(f"SEND {r.status_code} {r.text}")
        return r.json()
    except Exception as e:
        print(f"Error {e}")
        return {"error": str(e)}

def check():
    for coin in COINS:
        try:
            requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={coin}", timeout=10)
            time.sleep(0.5)
        except: time.sleep(1)

def run_bot():
    send_msg(f"💎 <b>BOT ULTRA 85% LIVE - 35 COINS</b> 🚀\n⏰ {get_dj_time().strftime('%H:%M')} DJ\n✅ ZEC+HYPE Included!")
    hb=0
    while True:
        try:
            now=time.time()
            if now-hb>10800:
                send_msg(f"🤖 <b>HEARTBEAT 35 COINS LIVE</b> ⏰ {get_dj_time().strftime('%H:%M:%S')} DJ")
                hb=now
            check()
            time.sleep(60)
        except Exception as e:
            print(e)
            time.sleep(10)

app=Flask('')

@app.route('/debug')
def debug():
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
        bot_info = requests.get(url, timeout=10).json()
        url2 = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        send_res = requests.post(url2, data={"chat_id": CHAT_ID, "text": "DEBUG TEST"}, timeout=10).json()
        return f"Bot Info: {bot_info}<br><br>ChatID: {CHAT_ID}<br><br>Token Len: {len(BOT_TOKEN) if BOT_TOKEN else 0}<br><br>Send Result: {send_res}"
    except Exception as e:
        return f"ERROR: {e}<br>Chat: {CHAT_ID}<br>Token exists: {bool(BOT_TOKEN)}"

@app.route('/force-active')
def force_active():
    res = send_msg("🤖 <b>TEST: BOT WORKING! 35 COINS! ZEC+HYPE OK!</b> ✅")
    return f"Sent! Result: {res}"

@app.route('/')
def home():
    return f"ULTRA 85% 35 COINS | {get_dj_time().strftime('%H:%M:%S')} DJ | LIVE | ZEC+HYPE"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))

if __name__=="__main__":
    Thread(target=run_bot).start()
    run_flask()
