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
 return datetime.now(TZ).strftime("%H:%M DJ")

def send(t):
 try:
  u=f"https://api.telegram.org/bot{BOT}/sendMessage"
  requests.post(u,data={"chat_id":CHAT,"text":t},timeout=10)
 except: pass

def price(s):
 try:
  r=requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={s}",timeout=5).json()
  return float(r['price'])
 except: return 108500.0

def r24(s):
 try:
  r=requests.get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={s}",timeout=5).json()
  return float(r['highPrice']),float(r['lowPrice']),float(r['priceChangePercent'])
 except: return None

def loop():
 send(f"Bot STARTED {dj()} 35 LIVE")
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
    print(f"{coin} {pos:.2f}")
    if pos<0.25 and ch<-1:
     send(f"LONG {coin} {p:.2f} SL {p*0.97:.2f} TP {p*1.02:.2f} {dj()}")
     time.sleep(5)
    elif pos>0.75 and ch>1:
     send(f"SHORT {coin} {p:.2f} SL {p*1.03:.2f} TP {p*0.98:.2f} {dj()}")
     time.sleep(5)
   except Exception as e: print(e)
  time.sleep(120)

@app.route('/')
def home():
 return f"LIVE {dj()}"

Thread(target=loop,daemon=True).start()

if __name__=="__main__":
 app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
