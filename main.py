from flask import Flask
from threading import Thread
import os, time, requests, datetime
import pytz

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@SunnyCryptoDJVIP"
COINS = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ZECUSDT","BCHUSDT","ALGOUSDT","NEARUSDT","SUIUSDT","STRKUSDT","ARBUSDT","DOGEUSDT","1000PEPEUSDT","BATUSDT","LINKUSDT","UNIUSDT","AAVEUSDT","INJUSDT","ONDOUSDT","ENAUSDT","HYPEUSDT","FILUSDT","WALUSDT","CRVUSDT","ZROUSDT","NXPCUSDT","ZKUSDT","OPUSDT","PAXGUSDT","ADAUSDT","TAOUSDT","ZEREBROUSDT"]

# Anti-spam - 1 signal per coin per 30 min
LAST_SIGNAL = {}

def get_dj_time():
    return datetime.datetime.now(pytz.timezone("Africa/Djibouti"))

def send_msg(t):
    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHANNEL_ID, "text": t, "parse_mode": "HTML"}, timeout=10)
    except: pass

def get_data(c):
    try:
        r=requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={c}",timeout=5).json()
        return {"price":float(r["lastPrice"]),"high":float(r["highPrice"]),"low":float(r["lowPrice"]),"change":float(r["priceChangePercent"])}
    except: return None

def can_send(coin, side):
    key = f"{coin}_{side}"
    now = time.time()
    if key in LAST_SIGNAL and now - LAST_SIGNAL[key] < 1800: # 30 min cooldown
        return False
    LAST_SIGNAL[key] = now
    return True

def check():
    print(f"SCAN PROFITABLE {get_dj_time().strftime('%H:%M DJ')}")
    for coin in COINS:
        d=get_data(coin)
        if not d: continue
        price=d["price"]; high=d["high"]; low=d["low"]
        dip = ((high-price)/high)*100
        pump = ((price-low)/low)*100

        # === BEAT CLASSIC PROFITABLE LONG 0.8% ===
        if 0.8 <= dip <= 7.0:
            if can_send(coin, "LONG"):
                tp1=price*1.025; tp2=price*1.05; sl=price*0.97
                send_msg(f"""🟢 <b>PROFITABLE LONG DIP</b> 🟢

💰 <b>{coin}</b> - LONG
📉 Dip: {dip:.2f}% from High
💵 Entry: ${price:.5f}
🎯 TP1: ${tp1:.5f} (+2.5%)
🎯 TP2: ${tp2:.5f} (+5% - MAIN)
🛑 SL: ${sl:.5f} (-3%)

✅ Beat Classic Setup
🕐 {get_dj_time().strftime('%H:%M DJ')} GMT+3
#LONG #{coin} #PROFITABLE""")
                time.sleep(2)

        # === BEAT CLASSIC PROFITABLE SHORT 1.5% ===
        if 1.5 <= pump <= 10.0 and d["change"]>1.0:
            if can_send(coin, "SHORT"):
                tp1=price*0.975; tp2=price*0.95; sl=price*1.03
                send_msg(f"""🔴 <b>PROFITABLE SHORT PUMP</b> 🔴

💰 <b>{coin}</b> - SHORT
📈 Pump: {pump:.2f}% from Low
💵 Entry: ${price:.5f}
🎯 TP1: ${tp1:.5f} (-2.5%)
🎯 TP2: ${tp2:.5f} (-5% - MAIN)
🛑 SL: ${sl:.5f} (+3%)

✅ Beat Classic Setup
🕐 {get_dj_time().strftime('%H:%M DJ')} GMT+3
#SHORT #{coin} #PROFITABLE""")
                time.sleep(2)
        time.sleep(0.4)

def run_bot():
    send_msg(f"💎 <b>BOT UPGRADED - BEAT CLASSIC PROFITABLE!</b>\n📊 {len(COINS)} coins\n🟢 LONG: 0.8%+ dip (High Win)\n🔴 SHORT: 1.5%+ pump (High Win)\n⏱️ 30min cooldown - No Spam\n🕐 {get_dj_time().strftime('%H:%M DJ')} GMT+3\nWIN RATE 70%+ TARGET")
    while True:
        try: check(); time.sleep(180)
        except: time.sleep(10)

app=Flask('')
@app.route('/')
def home(): return f"PROFITABLE BOT 70% - DJ {get_dj_time().strftime('%H:%M')}"
def run_flask(): app.run(host='0.0.0.0',port=8080)
if __name__=="__main__":
    Thread(target=run_flask).start()
    run_bot()
