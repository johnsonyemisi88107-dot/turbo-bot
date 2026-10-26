import os, time, requests, datetime, pytz
from binance.client import Client

# CONFIG
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
DJ_TZ = pytz.timezone('Africa/Djibouti')

COINS = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","DOGEUSDT","ADAUSDT","AVAXUSDT","SHIBUSDT","DOTUSDT","LINKUSDT","TRXUSDT","MATICUSDT","LTCUSDT","BCHUSDT","NEARUSDT","UNIUSDT","PEPEUSDT","ETCUSDT","XLMUSDT","HBARUSDT","APTUSDT","ARBUSDT","FILUSDT","OPUSDT","ATOMUSDT","INJUSDT","STXUSDT","RNDRUSDT","SUIUSDT","TIAUSDT","SEIUSDT","JUPUSDT","WIFUSDT","BONKUSDT"]

scanned = 0
sent_today = set()

def send_msg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML"}
    try:
        requests.post(url, json=data, timeout=10)
    except: pass

def get_data(symbol):
    try:
        client = Client()
        klines = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1DAY, limit=1)
        hi = float(klines[0][2])
        lo = float(klines[0][3])
        price = float(klines[0][4])
        rng = hi - lo
        if rng == 0: return None
        pos = (price - lo) / rng
        return price, hi, lo, pos
    except:
        return None

# START MESSAGE
now = datetime.datetime.now(DJ_TZ).strftime("%H:%M DJ %d/%m")
send_msg(f"🚀 <b>SUNNY VIP V3.1 BREAKOUT STARTED</b>\n⏰ {now}\n💎 35 Coins LIVE\n🎯 Filter 40/60 + Entry -2%/+2% + SL 3%\n🔥 PREMIUM MODE")

print(f"V3.1 40/60 STARTED {now}")

while True:
    try:
        now_dj = datetime.datetime.now(DJ_TZ)
        time_str = now_dj.strftime("%H:%M DJ %d/%m")
        
        for coin in COINS:
            data = get_data(coin)
            if not data: continue
            price, hi, lo, pos = data
            scanned += 1
            
            # VISUAL
            bar = "█" * int(pos*10) + "░" * (10-int(pos*10))
            print(f"[{scanned}] {coin} {pos*100:.0f}% {bar}")

            # V3.1 40/60 LOGIC
            signal = None
            if pos < 0.40 and f"{coin}_LONG" not in sent_today:
                entry = lo * 0.98
                sl = entry * 0.97
                tp1 = hi * 1.02
                tp2 = hi * 1.04
                tp3 = hi * 1.07
                signal = f"🟢 <b>LONG BREAKOUT #{coin}</b>\n\n📊 Position: {pos*100:.0f}% Bottom 40%\n📍 Entry: {entry:.4f} (-2% Below LOW)\n🛑 SL: {sl:.4f} (-3%)\n\n🎯 TP1: {tp1:.4f} (+2% Above HIGH)\n🎯 TP2: {tp2:.4f} (+4%)\n🎯 TP3: {tp3:.4f} (+7%)\n\n💎 SUNNY VIP V3.1"
                sent_today.add(f"{coin}_LONG")

            elif pos > 0.60 and f"{coin}_SHORT" not in sent_today:
                entry = hi * 1.02
                sl = entry * 1.03
                tp1 = lo * 0.98
                tp2 = lo * 0.96
                tp3 = lo * 0.93
                signal = f"🔴 <b>SHORT BREAKOUT #{coin}</b>\n\n📊 Position: {pos*100:.0f}% Top 60%\n📍 Entry: {entry:.4f} (+2% Above HIGH)\n🛑 SL: {sl:.4f} (+3%)\n\n🎯 TP1: {tp1:.4f} (-2% Below LOW)\n🎯 TP2: {tp2:.4f} (-4%)\n🎯 TP3: {tp3:.4f} (-7%)\n\n💎 SUNNY VIP V3.1"
                sent_today.add(f"{coin}_SHORT")

            if signal:
                send_msg(signal)
                print(f"SIGNAL SENT {coin}")
                time.sleep(2)

        # HEARTBEAT EVERY 1 HOUR
        if scanned % 35 == 0:
            loops = scanned // 35
            if loops % 20 == 0: # every ~60 min
                send_msg(f"💓 <b>V3.1 ALIVE {time_str}</b>\n📊 Scanned {scanned} coins\n🎯 Filter 40/60 Waiting -2% / +2%\n💎 SUNNY VIP V3.1")
                # reset daily
                if now_dj.hour == 0:
                    sent_today.clear()
                    scanned = 0

        time.sleep(180) # scan every 3 min

    except Exception as e:
        print(f"Error {e}")
        time.sleep(60)
