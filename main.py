import os,time,requests,pytz
from datetime import datetime
from threading import Thread
from flask import Flask

app=Flask(__name__)
BOT=os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT=os.environ.get("TELEGRAM_CHAT_ID")

COINS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","DOGEUSDT","ADAUSDT","AVAXUSDT","DOTUSDT","LINKUSDT","SHIBUSDT","UNIUSDT","ATOMUSDT","ETCUSDT","XLMUSDT","NEARUSDT","APTUSDT","ARBUSDT","OPUSDT","WIFUSDT","BONKUSDT","FLOKIUSDT","PEPEUSDT","SUIUSDT","RENDERUSDT","ENAUSDT","TAOUSDT","ZECUSDT","HYPEUSDT","MAGMAUSDT","INJUSDT","FETUSDT","WLDUSDT","ARUSDT","LDOUSDT"]

TZ=pytz.timezone("Africa/Djibouti")

def dj():
    return datetime.now(TZ).strftime("%H:%M DJ %d/%m")

def send(t):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage",data={"chat_id":CHAT,"text":t},timeout=10)
    except: pass

def price(s):
    try:
        return float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}",timeout=5).json()['price'])
    except: return 0

def r24(s):
    try:
        r=requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={s}",timeout=5).json()
        return float(r['highPrice']),float(r['lowPrice'])
    except: return None

def loop():
    send(f"✅ SUNNY VIP V3 BREAKOUT STARTED\n⏰ {dj()}\n📊 35 Coins LIVE\n🎯 Entry -2% Below LOW / +2% Above HIGH\n💓 Heartbeat Every 1 Hour\n💎 PREMIUM MODE")
    c=0
    while True:
        c+=1
        if c % 20 == 0:
            send(f"💓 V3 ALIVE {dj()}\n📊 Scanned {c*35} coins\n🎯 Waiting for -2% / +2% Breakout\n💎 SUNNY VIP V3")

        for coin in COINS:
            try:
                p=price(coin)
                d=r24(coin)
                if not d: continue
                hi,lo=d
                rng=hi-lo
                if rng==0: continue
                pos=(p-lo)/rng
                filled=int(pos*10)
                b="█"*filled+"░"*(10-filled)
                print(f"[{c}] {coin} {pos*100:.0f}% {b}",flush=True)

                # === YOUR REQUEST: LONG FROM -2% BELOW LOW ===
                if pos < 0.25:
                    entry = lo * 0.98      # -2% BELOW LOW
                    sl = entry * 0.97      # -3% SL
                    tp1 = hi * 1.02        # +2% ABOVE HIGH (YOUR REQUEST!)
                    tp2 = hi * 1.04        # +4% ABOVE HIGH
                    tp3 = hi * 1.07        # +7% Runner

                    msg=f"🟢 LONG BREAKOUT #{coin}\n\n📍 Entry: {entry:.4f}\n   ↳ -2% Below 24h LOW ({lo:.4f})\n🛑 SL: {sl:.4f} (-3%)\n\n🎯 TP1: {tp1:.4f} (+2% Above HIGH)\n🎯 TP2: {tp2:.4f} (+4% Above HIGH)\n🎯 TP3: {tp3:.4f} (+7% Runner)\n\n📊 Context:\nLOW: {lo:.4f} | HIGH: {hi:.4f}\nNow: {p:.4f} [{b}] {pos*100:.0f}% BOTTOM\n💡 Liquidity Grab Setup!\n\n⏰ {dj()}\n💎 SUNNY VIP V3"
                    send(msg)
                    time.sleep(20)

                # === YOUR REQUEST: SHORT FROM +2% ABOVE HIGH ===
                elif pos > 0.75:
                    entry = hi * 1.02      # +2% ABOVE HIGH
                    sl = entry * 1.03      # +3% SL
                    tp1 = lo * 0.98        # -2% BELOW LOW (YOUR REQUEST!)
                    tp2 = lo * 0.96        # -4% BELOW LOW
                    tp3 = lo * 0.93        # -7% Runner

                    msg=f"🔴 SHORT BREAKOUT #{coin}\n\n📍 Entry: {entry:.4f}\n   ↳ +2% Above 24h HIGH ({hi:.4f})\n🛑 SL: {sl:.4f} (+3%)\n\n🎯 TP1: {tp1:.4f} (-2% Below LOW)\n🎯 TP2: {tp2:.4f} (-4% Below LOW)\n🎯 TP3: {tp3:.4f} (-7% Runner)\n\n📊 Context:\nLOW: {lo:.4f} | HIGH: {hi:.4f}\nNow: {p:.4f} [{b}] {pos*100:.0f}% TOP\n💡 Fakeout Short Setup!\n\n⏰ {dj()}\n💎 SUNNY VIP V3"
                    send(msg)
                    time.sleep(20)

            except Exception as e:
                print(e,flush=True)
        time.sleep(180)

@app.route('/')
def home():
    return f"SUNNY VIP V3 BREAKOUT LIVE {dj()} - Entry -2% / +2% Mode"

Thread(target=loop,daemon=True).start()

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
