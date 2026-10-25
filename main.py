import os,time,requests,pytz
from datetime import datetime
from threading import Thread
from flask import Flask
app=Flask(__name__)
BOT=os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT=os.environ.get("TELEGRAM_CHAT_ID")
COINS=["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","DOGEUSDT","ADAUSDT","AVAXUSDT","DOTUSDT","LINKUSDT","SHIBUSDT","UNIUSDT","ATOMUSDT","ETCUSDT","XLMUSDT","NEARUSDT","APTUSDT","ARBUSDT","OPUSDT","WIFUSDT","BONKUSDT","FLOKIUSDT","PEPEUSDT","SUIUSDT","RENDERUSDT","ENAUSDT","TAOUSDT","ZECUSDT","HYPEUSDT","MAGMAUSDT","INJUSDT","FETUSDT","WLDUSDT","ARUSDT","LDOUSDT"]
TZ=pytz.timezone("Africa/Djibouti")
def dj(): return datetime.now(TZ).strftime("%H:%M DJ %d/%m")
def send(t):
 try:
  requests.post(f"https://api.telegram.org/bot{BOT}/sendMessage",data={"chat_id":CHAT,"text":t},timeout=10)
 except: pass
def price(s):
 try: return float(requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}",timeout=5).json()['price'])
 except: return 0
def r24(s):
 try:
  r=requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={s}",timeout=5).json()
  return float(r['highPrice']),float(r['lowPrice']),float(r['priceChangePercent'])
 except: return None
def loop():
 send(f"✅ SUNNY VIP PREMIUM STARTED\n⏰ {dj()}\n📊 35 Coins LIVE Scanning\n🔍 Looking for LONG/SHORT Setups...")
 c=0
 while True:
  c+=1
  for coin in COINS:
   try:
    p=price(coin)
    d=r24(coin)
    if not d: continue
    hi,lo,ch=d
    rng=hi-lo
    if rng==0: continue
    pos=(p-lo)/rng
    print(f"[{c}] {coin} pos={pos:.2f} ch={ch:.1f}",flush=True)
    if pos<0.30 and ch<-0.5:
     sl=p*0.97
     tp1=p*1.02
     tp2=p*1.035
     msg=f"🟢 LONG #{coin}\n\n📍 Entry: {p:.4f}\n🛑 SL: {sl:.4f} (-3%)\n🎯 TP1: {tp1:.4f} (+2%)\n🎯 TP2: {tp2:.4f} (+3.5%)\n\n📊 24h Range Position: {pos*100:.0f}% (BOTTOM)\n⏰ {dj()}\n\n💎 SUNNY VIP PREMIUM"
     send(msg)
     time.sleep(10)
    elif pos>0.70 and ch>0.5:
     sl=p*1.03
     tp1=p*0.98
     tp2=p*0.965
     msg=f"🔴 SHORT #{coin}\n\n📍 Entry: {p:.4f}\n🛑 SL: {sl:.4f} (+3%)\n🎯 TP1: {tp1:.4f} (-2%)\n🎯 TP2: {tp2:.4f} (-3.5%)\n\n📊 24h Range Position: {pos*100:.0f}% (TOP)\n⏰ {dj()}\n\n💎 SUNNY VIP PREMIUM"
     send(msg)
     time.sleep(10)
   except Exception as e: print(e,flush=True)
  time.sleep(180)
@app.route('/')
def home(): return f"SUNNY VIP LIVE {dj()} 35 COINS"
Thread(target=loop,daemon=True).start()
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
