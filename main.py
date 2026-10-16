import os, time, requests, threading, datetime, pytz
from telegram.ext import ApplicationBuilder, CommandHandler
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL_ID = "@SunnyCryptoDJVIP"
COINS = ["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","DOGEUSDT","ADAUSDT","AVAXUSDT","LINKUSDT","DOTUSDT","TRXUSDT","MATICUSDT","LTCUSDT","SHIBUSDT","UNIUSDT","ATOMUSDT","ETCUSDT","FILUSDT","APTUSDT","ARBUSDT","OPUSDT"]
TF_SETTINGS = {"15m":{"dip_pct":0.001,"tp":0.02,"sl":0.01},"1h":{"dip_pct":0.002,"tp":0.025,"sl":0.012},"4h":{"dip_pct":0.004,"tp":0.035,"sl":0.015},"1d":{"dip_pct":0.008,"tp":0.05,"sl":0.02}}
SESSIONS = {"MORNING":{"hours":(8,12),"tfs":["4h","1d"]},"AFTERNOON":{"hours":(12,18),"tfs":["1h","4h"]},"NIGHT":{"hours":(18,24),"tfs":["15m","1h"]},"NIGHT2":{"hours":(0,2),"tfs":["15m","1h"]},"SLEEP":{"hours":(2,8),"tfs":[]}}
def get_dj_time(): return datetime.datetime.now(pytz.timezone("Africa/Djibouti"))
def get_session():
 h=get_dj_time().hour
 for name,s in SESSIONS.items():
  st,en=s["hours"]
  if st<en:
   if st<=h<en: return name,s
  else:
   if h>=st or h<en: return name,s
 return "SLEEP",SESSIONS["SLEEP"]
def send_channel_msg(text):
 try:
  url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
  requests.post(url,data={"chat_id":CHANNEL_ID,"text":text},timeout=10)
 except: pass
def get_klines(symbol,interval,limit=100):
 try:
  url=f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
  r=requests.get(url,timeout=10).json()
  return [float(x[4]) for x in r]
 except: return []
def calc_rsi(prices,period=14):
 if len(prices)<period+1: return 50
 gains=[];losses=[]
 for i in range(1,len(prices)):
  d=prices[i]-prices[i-1];gains.append(max(d,0));losses.append(max(-d,0))
 avg_gain=sum(gains[-period:])/period;avg_loss=sum(losses[-period:])/period
 if avg_loss==0: return 70
 return 100-(100/(1+avg_gain/avg_loss))
def check_dip(symbol,tf,turbo=False):
 prices=get_klines(symbol,tf,100)
 if len(prices)<30: return None
 setting=TF_SETTINGS[tf];last,prev=prices[-1],prices[-2]
 dip=(prev-last)/prev if prev!=0 else 0;rsi=calc_rsi(prices)
 if turbo or abs(dip)>=setting["dip_pct"]:
  side="LONG" if dip>=0 else "SHORT"
  return {"side":side,"entry":last,"tp":last*(1+setting["tp"]) if dip>=0 else last*(1-setting["tp"]),"sl":last*(1-setting["sl"]) if dip>=0 else last*(1+setting["sl"]),"rsi":rsi,"dip":dip*100,"tf":tf,"symbol":symbol,"turbo":turbo}
 return None
def format_signal(sig):
 emoji="🟢 LONG" if sig["side"]=="LONG" else "🔴 SHORT"
 turbo="⚡ TURBO" if sig.get("turbo") else "🔥"
 return f"{turbo} {emoji} {sig['symbol']} {sig['tf']}\nEntry: {sig['entry']:.4f}\nTP: {sig['tp']:.4f}\nSL: {sig['sl']:.4f}\nRSI:{sig['rsi']:.1f} Dip:{sig['dip']:.2f}%\nDJ:{get_dj_time().strftime('%H:%M')}"
def scan_and_post_sync():
 sess_name,sess=get_session()
 if sess_name=="SLEEP": return
 best=[]
 for sym in COINS:
  for tf in sess["tfs"]:
   sig=check_dip(sym,tf,turbo=False)
   if sig: best.append(sig)
 best.sort(key=lambda x: abs(x['dip']),reverse=True)
 posted=0
 for sig in best[:2]:
  send_channel_msg(format_signal(sig));posted+=1;time.sleep(1)
 if posted==0:
  allp=[]
  for sym in COINS:
   for tf in sess["tfs"]:
    s=check_dip(sym,tf,turbo=True)
    if s: allp.append(s)
  if allp:
   allp.sort(key=lambda x: abs(x['dip']),reverse=True)
   send_channel_msg(format_signal(allp[0])+"\nTURBO Best!")
async def start_cmd(u,c): await u.message.reply_text("24/7 TURBO LIVE! /scan")
async def scan_cmd(u,c):
 await u.message.reply_text("Scanning...");threading.Thread(target=scan_and_post_sync,daemon=True).start()
def auto_loop():
 while True:
  try:
   if get_session()[0]!="SLEEP": scan_and_post_sync()
   time.sleep(900)
  except: time.sleep(60)
flask_app = Flask('')
@flask_app.route('/')
def home():
    return "Bot is Alive!"

def run_flask():
    flask_app.run(host='0.0.0.0', port=8080)

def keep_alive():
    threading.Thread(target=run_flask).start()

app=ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start",start_cmd))
app.add_handler(CommandHandler("scan",scan_cmd))
threading.Thread(target=auto_loop,daemon=True).start()
keep_alive()
app.run_polling()
