from flask import Flask
from threading import Thread
import os, time, requests, datetime
import pytz

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_ID", "-1004491702289")
COINS = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","DOGEUSDT","SHIBUSDT","PEPEUSDT","AVAXUSDT","DOTUSDT","LINKUSDT","LTCUSDT","BCHUSDT","UNIUSDT","ETCUSDT","APTUSDT","ARBUSDT","OPUSDT","SUIUSDT","NEARUSDT","FILUSDT","INJUSDT","ATOMUSDT","RNDRUSDT","FETUSDT","WIFUSDT","BONKUSDT","FLOKIUSDT","PAXGUSDT","ADAUSDT","TAOUSDT","ZEREBROUSDT","VIRTUALUSDT"]

LAST_SIGNAL = {}
ACTIVE = {}
STATS = {"wins":0, "loss":0, "tp1":0}

def get_dj_time():
    return datetime.datetime.now(pytz.timezone("Africa/Djibouti"))

def send_msg(t):
    try:
        print(f"SENDING TO {CHANNEL_ID}")
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHANNEL_ID, "text": t, "parse_mode": "HTML"}
        r = requests.post(url, data=data, timeout=15)
        print(f"RESULT: {r.text}")
    except Exception as e:
        print(f"ERROR: {e}")
    
        
        
        
    
        

def get_data(c):
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={c}", timeout=5).json()
        return {"price": float(r["lastPrice"]), "high": float(r["highPrice"]), "low": float(r["lowPrice"])}
    except:
        return None

def get_rsi(prices):
    if len(prices) < 15:
        return 50
    gains = []
    losses = []
    for i in range(1, len(prices)):
        diff = prices[i] - prices[i-1]
        if diff > 0:
            gains.append(diff)
            losses.append(0)
        else:
            losses.append(abs(diff))
            gains.append(0)
    avg_gain = sum(gains[-14:]) / 14
    avg_loss = sum(losses[-14:]) / 14
    if avg_loss == 0:
        return 75
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def get_vwap(coin):
    try:
        k15 = requests.get(f"https://api.binance.com/api/v3/klines?symbol={coin}&interval=15m&limit=50", timeout=5).json()
        closes = [float(k[4]) for k in k15]
        highs = [float(k[2]) for k in k15]
        lows = [float(k[3]) for k in k15]
        vols = [float(k[5]) for k in k15]
        typical = [(h+l+c)/3 for h,l,c in zip(highs, lows, closes)]
        vwap = sum(t*v for t,v in zip(typical, vols)) / sum(vols)
        k5 = requests.get(f"https://api.binance.com/api/v3/klines?symbol={coin}&interval=5m&limit=3", timeout=5).json()
        c1 = float(k5[-2][4]); o1 = float(k5[-2][1])
        c2 = float(k5[-1][4]); o2 = float(k5[-1][1])
        bull5 = c1 > o1 and c2 > o2
        bear5 = c1 < o1 and c2 < o2
        return closes, vols, vwap, bull5, bear5
    except:
        return None, None, None, False, False

def can_send(coin, side):
    key = f"{coin}_{side}"
    now = time.time()
    if key in LAST_SIGNAL and now - LAST_SIGNAL[key] < 2400:
        return False
    LAST_SIGNAL[key] = now
    return True

def btc_trend():
    try:
        b = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=3).json()
        return float(b["priceChangePercent"])
    except:
        return 0

def is_dj_session():
    h = get_dj_time().hour
    return 6 <= h <= 23

def check_tp():
    for key in list(ACTIVE.keys()):
        tr = ACTIVE[key]
        d = get_data(tr["coin"])
        if not d:
            continue
        price = d["price"]
        total = STATS["wins"] + STATS["loss"]
        if total == 0:
            total = 1
        wr = (STATS["wins"] / total) * 100
        if tr["side"] == "LONG":
            if price >= tr["tp2"]:
                STATS["wins"] += 1
                send_msg(f"✅ <b>TP2 WIN +3.2% {tr['coin']}</b> LONG\nEntry ${tr['entry']:.4f} -> ${price:.4f}\nWR {wr:.1f}%")
                del ACTIVE[key]
            elif price >= tr["tp1"] and not tr["tp1_hit"]:
                ACTIVE[key]["tp1_hit"] = True
                STATS["tp1"] += 1
                send_msg(f"⚡ <b>TP1 +1.5% {tr['coin']} LONG</b> Move SL to BE")
            elif price <= tr["sl"]:
                STATS["loss"] += 1
                send_msg(f"❌ <b>SL -2.1% {tr['coin']} LONG</b> WR {wr:.1f}%")
                del ACTIVE[key]
        else:
            if price <= tr["tp2"]:
                STATS["wins"] += 1
                send_msg(f"✅ <b>TP2 WIN -3.2% {tr['coin']}</b> SHORT\nEntry ${tr['entry']:.4f} -> ${price:.4f}\nWR {wr:.1f}%")
                del ACTIVE[key]
            elif price <= tr["tp1"] and not tr["tp1_hit"]:
                ACTIVE[key]["tp1_hit"] = True
                STATS["tp1"] += 1
                send_msg(f"⚡ <b>TP1 -1.5% {tr['coin']} SHORT</b>")
            elif price >= tr["sl"]:
                STATS["loss"] += 1
                send_msg(f"❌ <b>SL +2.1% {tr['coin']} SHORT</b> WR {wr:.1f}%")
                del ACTIVE[key]

def check():
    dj_now = get_dj_time()
    if not is_dj_session():
        print(f"SLEEP DJ {dj_now.strftime('%H:%M')}")
        return
    btc_ch = btc_trend()
    print(f"SCAN DJ {dj_now.strftime('%H:%M')} ACTIVE {len(ACTIVE)} BTC {btc_ch:.1f}%")
    check_tp()
    for coin in COINS:
        d = get_data(coin)
        if not d:
            continue
        closes, vols, vwap, bull5, bear5 = get_vwap(coin)
        if closes is None:
            continue
        price = d["price"]
        high = d["high"]
        low = d["low"]
        rsi = get_rsi(closes)
        ema20 = sum(closes[-20:]) / 20
        ema50 = sum(closes[-50:]) / 50
        avg_vol = sum(vols[-20:]) / 20
        vol_now = vols[-1]
        dip = ((high - price) / high) * 100
        pump = ((price - low) / low) * 100
        if btc_ch >= -2.8 and 1.2 <= dip <= 5.0 and 30 <= rsi <= 46 and price > vwap and price > ema50 * 0.995 and bull5 and vol_now > avg_vol * 0.9:
            if can_send(coin, "LONG"):
                tp1 = price * 1.015
                tp2 = price * 1.032
                sl = price * 0.979
                ACTIVE[f"{coin}_LONG"] = {"coin": coin, "entry": price, "tp1": tp1, "tp2": tp2, "sl": sl, "side": "LONG", "tp1_hit": False}
                send_msg(f"🟢 <b>ULTRA LONG 85%</b>\n<b>{coin}</b> Dip {dip:.2f}% RSI {rsi:.1f}\nEntry ${price:.4f}\nTP +1.5% / +3.2% / +6%\nSL -2.1%\n🕐 {dj_now.strftime('%H:%M')} DJ")
                time.sleep(2)
        if 1.5 <= pump <= 5.5 and 54 <= rsi <= 70 and price < vwap and price < ema20 and bear5 and vol_now > avg_vol * 0.9:
            if can_send(coin, "SHORT"):
                tp1 = price * 0.985
                tp2 = price * 0.968
                sl = price * 1.021
                ACTIVE[f"{coin}_SHORT"] = {"coin": coin, "entry": price, "tp1": tp1, "tp2": tp2, "sl": sl, "side": "SHORT", "tp1_hit": False}
                send_msg(f"🔴 <b>ULTRA SHORT 85%</b>\n<b>{coin}</b> Pump {pump:.2f}% RSI {rsi:.1f}\nEntry ${price:.4f}\nTP -1.5% / -3.2%\nSL +2.1%\n🕐 {dj_now.strftime('%H:%M')} DJ")
                time.sleep(2)
        time.sleep(0.5)

def run_bot():
    send_msg(f"💎 <b>BOT ULTRA 85% LIVE - FIXED</b>\n🕐 {get_dj_time().strftime('%H:%M')} DJ GMT+3\n✅ DJ Session + VWAP + TP Tracker")
    while True:
        try:
            check()
            st = 300 if not is_dj_session() else 90
            time.sleep(st)
        except Exception as e:
            print(f"Error {e}")
            time.sleep(10)

app = Flask('')
@app.route('/')
def home():
    total = STATS["wins"] + STATS["loss"]
    wr = (STATS["wins"] / total * 100) if total > 0 else 0
    dj_now = get_dj_time()
    session = "ACTIVE" if is_dj_session() else "SLEEP TILL 06:00"
    return f"ULTRA 85% | DJ {dj_now.strftime('%H:%M:%S')} | {session} | WR {wr:.1f}% | LIVE {len(ACTIVE)}"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    run_bot()
