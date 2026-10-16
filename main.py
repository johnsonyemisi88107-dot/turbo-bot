from flask import Flask
from threading import Thread
import os, time, requests, datetime
import pytz

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@SunnyCryptoDJVIP"
COINS = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","ZECUSDT","BCHUSDT","ALGOUSDT","NEARUSDT","SUIUSDT","STRKUSDT","ARBUSDT","DOGEUSDT","1000PEPEUSDT","BATUSDT","LINKUSDT","UNIUSDT","AAVEUSDT","INJUSDT","ONDOUSDT","ENAUSDT","HYPEUSDT","FILUSDT","WALUSDT","CRVUSDT","ZROUSDT","NXPCUSDT","ZKUSDT","OPUSDT","PAXGUSDT","ADAUSDT","TAOUSDT","ZEREBROUSDT"]

def get_dj_time():
    tz = pytz.timezone("Africa/Djibouti")
    return datetime.datetime.now(tz)

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHANNEL_ID, "text": text, "parse_mode": "HTML"}, timeout=10)
    except: pass

def get_data(coin):
    try:
        r = requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={coin}", timeout=5).json()
        return {"price": float(r["lastPrice"]), "high": float(r["highPrice"]), "low": float(r["lowPrice"]), "change": float(r["priceChangePercent"])}
    except: return None

def check_coins():
    for coin in COINS:
        d = get_data(coin)
        if not d: continue
        price=d["price"]; high=d["high"]; low=d["low"]
        dip = ((high-price)/high)*100
        pump = ((price-low)/low)*100

        if 0.5 <= dip <= 10:
            tp1=price*1.02; tp2=price*1.045; sl=price*0.97
            send_msg(f"🟢 <b>LONG DIP {dip:.2f}%</b>\n\n💰 <b>{coin}</b>\n📉 Dip: {dip:.2f}% from High\n💵 Entry: ${price:.5f}\n🎯 TP1: ${tp1:.5f} (+2%)\n🎯 TP2: ${tp2:.5f} (+4.5%)\n🛑 SL: ${sl:.5f}\n🕐 {get_dj_time().strftime('%H:%M DJ')}")
            time.sleep(1.5)

        if 0.5 <= pump <= 15 and d["change"]>0:
            tp1=price*0.98; tp2=price*0.955; sl=price*1.03
            send_msg(f"🔴 <b>SHORT PUMP {pump:.2f}%</b>\n\n💰 <b>{coin}</b>\n📈 Pump: {pump:.2f}% from Low\n💵 Entry: ${price:.5f}\n🎯 TP1: ${tp1:.5f} (-2%)\n🎯 TP2: ${tp2:.5f} (-4.5%)\n🛑 SL: ${sl:.5f}\n🕐 {get_dj_time().strftime('%H:%M DJ')}")
            time.sleep(1.5)
        time.sleep(0.3)

def run_bot():
    send_msg(f"🚀 <b>BOT LIVE 0.5% DIP PERFECT!</b>\n📊 {len(COINS)} coins\n🟢 LONG 0.5%+ dip\n🔴 SHORT 0.5%+ pump\n🕐 {get_dj_time().strftime('%H:%M DJ')} GMT+3\nSENSITIVE CLASSIC")
    while True:
        try: check_coins(); time.sleep(120)
        except: time.sleep(10)

app = Flask('')
@app.route('/')
def home(): return f"BOT LIVE 33 coins DJ {get_dj_time().strftime('%H:%M')}"
def run_flask(): app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    run_bot()
