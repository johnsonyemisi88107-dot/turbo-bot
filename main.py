import os, time, requests, pytz, random
from datetime import datetime
from threading import Thread
from flask import Flask
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

app = Flask(__name__)

# --- CONFIG FROM RENDER ENV ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# 35 COINS INCLUDING ZEC + HYPE + MAGMA
COINS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT",
    "DOGEUSDT","ADAUSDT","AVAXUSDT","DOTUSDT","LINKUSDT",
    "SHIBUSDT","UNIUSDT","ATOMUSDT","ETCUSDT","XLMUSDT",
    "NEARUSDT","APTUSDT","ARBUSDT","OPUSDT","WIFUSDT",
    "BONKUSDT","FLOKIUSDT","PEPEUSDT","SUIUSDT","RENDERUSDT",
    "ENAUSDT","TAOUSDT","ZECUSDT","HYPEUSDT","MAGMAUSDT",
    "INJUSDT","FETUSDT","WLDUSDT","ARUSDT","LDOUSDT"
]

last_signal_time = {}
DJ_TZ = pytz.timezone("Africa/Djibouti")

def get_dj_time():
    return datetime.now(DJ_TZ).strftime("%Y-%m-%d %H:%M:%S DJ")

def send_msg(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("Missing TOKEN/CHAT_ID")
        return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Send error {e}")

def get_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        r = requests.get(url, timeout=5).json()
        return float(r['price'])
    except:
        return None

def get_24h_stats(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
        r = requests.get(url, timeout=5).json()
        return {
            'high': float(r['highPrice']),
            'low': float(r['lowPrice']),
            'change': float(r['priceChangePercent'])
        }
    except:
        return None

# --- FAST SCANNING ALL 35 COINS ---
def scanning_loop():
    print("Scanning loop started - 35 coins")
    send_msg(f"✅ SUNNY VIP BOT STARTED - LIVE {get_dj_time()}\n📡 UptimeRobot: Active\n💰 Scanning 35 coins with LIMIT strategy!\nCoins: BTC, ETH, BNB, SOL, ZEC, HYPE, MAGMA + 28 more!")
    count = 0
    while True:
        count += 1
        found_signals = 0
        for coin in COINS:
            try:
                price = get_price(coin)
                stats = get_24h_stats(coin)
                if not price or not stats:
                    print(f"Skip {coin} no data")
                    continue
                support = stats['low']
                resistance = stats['high']
                range_size = resistance - support
                if range_size == 0:
                    continue
                position = (price - support) / range_size
                change = stats['change']
                print(f"[{count}] Scanning {coin} Pos {position:.2f} Change {change:.2f}%")
                signal = None
                cooldown_ok = coin not in last_signal_time or time.time() - last_signal_time[coin] > 1800
                if position < 0.25 and change < -1 and cooldown_ok:
                    entry = price
                    sl = entry * 0.97
                    tp1 = entry * 1.02
                    tp2 = entry * 1.04
                    tp3 = entry * 1.06
                    signal = f"""🚀 <b>{coin} LONG SIGNAL 🔥</b>

📊 <b>Order Type: LIMIT ✅ BEST FOR TRADING</b>
💰 <b>Entry:</b> LIMIT at {entry:.5f}
🛡️ <b>Stop Loss:</b> {sl:.5f} (Conditional Market)
🎯 <b>TP1:</b> {tp1:.5f} (+2%)
🎯 <b>TP2:</b> {tp2:.5f} (+4%)
🎯 <b>TP3:</b> {tp3:.5f} (+6%)

⏰ {get_dj_time()}
📈 Reason: At SUPPORT {position*100:.0f}% of range + Dip {change:.1f}% -> Bounce expected
⚡ Leverage: 10x Cross | Scanning: 35 coins LIVE
💡 How: Futures -> Order Type LIMIT -> {entry:.5f} + Set SL/TP as Conditional
"""
                elif position > 0.75 and change > 1 and cooldown_ok:
                    entry = price
                    sl = entry * 1.03
                    tp1 = entry * 0.98
                    tp2 = entry * 0.96
                    tp3 = entry * 0.94
                    signal = f"""📉 <b>{coin} SHORT SIGNAL 🔥</b>

📊 <b>Order Type: LIMIT ✅ BEST FOR TRADING</b>
💰 <b>Entry:</b> LIMIT at {entry:.5f}
🛡️ <b>Stop Loss:</b> {sl:.5f} (Conditional Market)
🎯 <b>TP1:</b> {tp1:.5f} (-2%)
🎯 <b>TP2:</b> {tp2:.5f} (-4%)
🎯 <b>TP3:</b> {tp3:.5f} (-6%)

⏰ {get_dj_time()}
📉 Reason: At RESISTANCE {position*100:.0f}% of range + Pump {change:.1f}% -> Drop expected
⚡ Leverage: 10x Cross | Scanning: 35 coins LIVE
💡 How: Futures -> Order Type LIMIT -> {entry:.5f} + Set SL/TP as Conditional
"""
                if signal:
                    send_msg(signal)
                    last_signal_time[coin] = time.time()
                    found_signals += 1
                    print(f"*** SIGNAL SENT {coin} ***")
                    time.sleep(5)
                time.sleep(0.5)
            except Exception as e:
                print(f"Error {coin}: {e}")
                time.sleep(0.5)
        print(f"--- Full scan #{count} done {get_dj_time()} Found {found_signals} signals --- Sleeping 120 sec")
        time.sleep(120)

# --- TELEGRAM COMMANDS ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"✅ Bot LIVE - {get_dj_time()}\n📡 Scanning 35 coins 24/7\nCommands: /start /trade /status /help\nOrder Type: Always use LIMIT for entry!")

async def trade_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🔍 Scanning {len(COINS)} coins for LIMIT setup... {get_dj_time()}")
    try:
        price = get_price("BTCUSDT")
        if not price:
            price = 108500.0
        msg = f"""🚀 <b>FORCE ACTIVE - Manual Trade Request</b>

💰 BTCUSDT Example LIMIT Trade:
Entry: LIMIT at {price:.2f}

📊 Order Type: LIMIT ✅ (Lowest fees)
🛡️ SL: Conditional Market at {price*0.97:.2f} (-3%)
🎯 TP: Conditional Limit at {price*1.03:.2f} (+3%)

⏰ {get_dj_time()}
✅ Bot is LIVE and scanning 35 coins! Real signals post automatically when setup found!

💡 How to place:
1. Futures -> Order Type LIMIT -> {price:.2f}
2. Set SL {price*0.97:.2f} TP {price*1.03:.2f} as Conditional
"""
        send_msg(msg)
        await update.message.reply_text("✅ Test LIMIT signal sent to channel! Check SUNNY VIP channel! 🚀")
    except Exception as e:
        await update.message.reply_text(f"Bot busy scanning, try again! {e}")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"📊 STATUS LIVE\n⏰ {get_dj_time()}\n💰 Coins: {len(COINS)}\n📡 Scanning every 2 min\n✅ UptimeRobot: Active\nLast signals: {len(last_signal_time)} sent today")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📚 HOW TO TRADE LIMIT SIGNALS:\n1. Copy Entry Price\n2. Binance Futures -> LIMIT order\n3. Set SL as Conditional Market\n4. Set TP as Conditional Limit\n5. Leverage 10x Cross\nAlways use LIMIT - Low fees + No sl
