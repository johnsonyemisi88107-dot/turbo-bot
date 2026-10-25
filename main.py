import os, time, requests, pytz
from datetime import datetime
from threading import Thread
from flask import Flask

app = Flask(__name__)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
COINS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","DOGEUSDT","ADAUSDT","AVAXUSDT","DOTUSDT","LINKUSDT","SHIBUSDT","UNIUSDT","ATOMUSDT","ETCUSDT","XLMUSDT","NEARUSDT","APTUSDT","ARBUSDT","OPUSDT","WIFUSDT","BONKUSDT","FLOKIUSDT","PEPEUSDT","SUIUSDT","RENDERUSDT","ENAUSDT","TAOUSDT","ZECUSDT","HYPEUSDT","MAGMAUSDT","INJUSDT","FETUSDT","WLDUSDT","ARUSDT","LDOUSDT"]
DJ_TZ = pytz.timezone("Africa/Djibouti")

def get_dj_time():
    return datetime.now(DJ_TZ).strftime("%Y-%m-%d %H:%M:%S DJ")

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}, timeout=10)
    except: pass

def get_price(s):
    try:
        return float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}", timeout=5).json()['price'])
    except:
        return 108500.0

def get_24h(s):
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={s}", timeout=5).json()
        return float(r['highPrice']), float(r['lowPrice']), float(r['priceChangePercent'])
    except:
        return None

def scanning_loop():
    send_msg(f"Bot STARTED {get_dj_time()} 35 coins LIVE")
    c=0
    while True:
        c+=1
        for coin in COINS:
            try:
                price = get_price(coin)
                data = get_24h(coin)
                if not data: continue
                high, low, change = data
                rng = high-low
                if rng==0: continue
                pos = (price-low)/rng
                print(f"[{c}] {coin} pos {pos:.2f}")
                if pos<0.25 and change<-1:
                    msg = f"LONG {coin} Entry LIMIT {price:.2f} SL {price*0.97:.2f} TP {price*1.02:.2f} {get_dj_time()}"
                    send_msg(msg)
                    time.sleep(5)
                elif pos>0.75 and change>1:
                    msg = f"SHORT {coin} Entry LIMIT {price:.2f} SL {price*1.03:.2f} TP {price*0.98:.2f} {get_dj_time()}"
                    send_msg(msg)
                    time.sleep(5)
            except Exception as e:
                print(e)
        time.sleep(120)

@app.route('/')
def home():
    return f"Bot LIVE {get_dj_time()}"

if __name__ == "__main__":
    Thread(target=scanning_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
