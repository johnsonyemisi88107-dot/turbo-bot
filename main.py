import os, time, requests, pytz, random
from datetime import datetime
from threading import Thread
from flask import Flask
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

app = Flask(__name__)

# --- CONFIG FROM RENDER ENV ---
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("CHAT_ID")

# 35 COINS INCLUDING ZEC + HYPE
COINS = [
    "BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT","XRPUSDT","ADAUSDT","DOGEUSDT",
    "SHIBUSDT","AVAXUSDT","DOTUSDT","LINKUSDT","MATICUSDT","LTCUSDT","BCHUSDT",
    "UNIUSDT","ATOMUSDT","ETCUSDT","XLMUSDT","FILUSDT","TRXUSDT",
    "NEARUSDT","APTUSDT","ARBUSDT","OPUSDT","PEPEUSDT","SUIUSDT","SEIUSDT",
    "WIFUSDT","BONKUSDT","FLOKIUSDT","ZECUSDT","HYPEUSDT","MAGMAUSDT",
    "ENAUSDT","TAOUSDT"
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
        print(f"Sent: {text[:50]}")
    except Exception as e:
        print(f"Send error: {e}")

def get_price(coin):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={coin}"
        r = requests.get(url, timeout=5).json()
        return float(r['price'])
    except:
        return None

def get_24h_stats(coin):
    try:
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={coin}"
        r = requests.get(url, timeout=5).json()
        return {
            "high": float(r['highPrice']),
            "low": float(r['lowPrice']),
            "change": float(r['priceChangePercent'])
        }
    except:
        return None

def scanning_loop():
    print("Scanning loop started - 35 coins")
    send_msg(f"✅ SUNNY VIP BOT STARTED - LIVE {get_dj_time()}\n📡 UptimeRobot: Active\n💰 Scanning {len(COINS)} coins with LIMIT strategy!")
    while True:
        for coin in COINS:
            try:
                price = get_price(coin)
                stats = get_24h_stats(coin)
                if not price or not stats:
                    continue

                # Support / Resistance Logic (Simple but powerful)
                support = stats['low']
                resistance = stats['high']
                range_size = resistance - support
                if range_size == 0:
                    continue

                position = (price - support) / range_size

                signal = None
                # Near support -> LONG LIMIT
                if position < 0.15 and stats['change'] < -2:
                    # Cooldown 1 hour per coin
                    if coin in last_signal_time and time.time() - last_signal_time[coin] < 3600:
                        continue
                    entry = price
                    sl = entry * 0.97  # -3%
                    tp1 = entry * 1.02
                    tp2 = entry * 1.04
                    tp3 = entry * 1.06
                    signal = f"""🚀 <b>{coin} LONG SIGNAL 🔥</b>

📊 <b>Order Type: LIMIT ✅ BEST FOR TRADING</b>

💰 <b>Entry:</b> LIMIT at {entry:.5f}
   Set Order Type -> Limit -> Price {entry:.5f}

🛡️ <b>Stop Loss:</b> {sl:.5f}
   Set as: Conditional Market

🎯 <b>Take Profits:</b>
   TP1: {tp1:.5f} (+2%)
   TP2: {tp2:.5f} (+4%)
   TP3: {tp3:.5f} (+6%)

⏰ Time: {get_dj_time()}
📈 Reason: Price at STRONG SUPPORT + Dip - Oversold bounce expected
⚡ Leverage: 10x Cross | Margin: 5-10% of balance
💡 Fees: Limit = 0.02% (cheap!)

⚠️ Use isolated TP/SL!
"""
                # Near resistance -> SHORT LIMIT
                elif position > 0.85 and stats['change'] > 2:
                    if coin in last_signal_time and time.time() - last_signal_time[coin] < 3600:
                        continue
                    entry = price
                    sl = entry * 1.03  # +3%
                    tp1 = entry * 0.98
                    tp2 = entry * 0.96
                    tp3 = entry * 0.94
                    signal = f"""📉 <b>{coin} SHORT SIGNAL 🔥</b>

📊 <b>Order Type: LIMIT ✅ BEST FOR TRADING</b>

💰 <b>Entry:</b> LIMIT at {entry:.5f}
   Set Order Type -> Limit -> Price {entry:.5f}

🛡️ <b>Stop Loss:</b> {sl:.5f}
   Set as: Conditional Market

🎯 <b>Take Profits:</b>
   TP1: {tp1:.5f} (-2%)
   TP2: {tp2:.5f} (-4%)
   TP3: {tp3:.5f} (-6%)

⏰ Time: {get_dj_time()}
📉 Reason: Price at STRONG RESISTANCE + Pump - Drop expected
⚡ Leverage: 10x Cross | Margin: 5-10% of balance
💡 Fees: Limit = 0.02% (cheap!)

⚠️ Use isolated TP/SL!
"""

                if signal:
                    send_msg(signal)
                    last_signal_time[coin] = time.time()
                    time.sleep(5)

                time.sleep(1)
            except Exception as e:
                print(f"Error {coin}: {e}")
                time.sleep(1)
        print(f"Full scan done {get_dj_time()} - Sleeping 60 sec")
        time.sleep(60)

# --- TELEGRAM COMMANDS /start /trade ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"👋 Welcome to SUNNY VIP Crypto PREMIUM 🔥\n\n"
        f"✅ Bot LIVE - {get_dj_time()}\n"
        f"📡 Scanning {len(COINS)} coins 24/7\n\n"
        f"Commands:\n"
        f"/start - This message\n"
        f"/trade - Force latest signal 🚀\n"
        f"/status - Check bot status ✅\n"
        f"/help - How to trade\n\n"
        f"💰 Order Type: Always use LIMIT for entry!\n"
        f"Channel signals come automatically!"
    )

async def trade_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🔍 Scanning {len(COINS)} coins for LIMIT setup... {get_dj_time()}")
    # Send force signal
    price = get_price("BTCUSDT")
    msg = f"""🚀 <b>FORCE ACTIVE - Manual Trade Request</b>

💰 BTCUSDT Example LIMIT Trade:
Entry: LIMIT at {price}

📊 Order Type: LIMIT ✅ (Lowest fees)
🛡️ SL: Conditional Market
🎯 TP: Conditional Limit

⏰ {get_dj_time()}
✅ Bot is LIVE and scanning! Real signals post automatically when 85%+ setup found!
"""
    send_msg(msg)
    await update.message.reply_text("✅ Test signal sent to channel! Check SUNNY VIP channel!")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"✅ BOT STATUS: LIVE\n"
        f"⏰ {get_dj_time()}\n"
        f"📡 Render: Active\n"
        f"📡 UptimeRobot: Active (5 min ping)\n"
        f"💰 Coins: {len(COINS)} including ZEC + HYPE + MAGMA\n"
        f"📊 Strategy: LIMIT Order (Best)\n"
        f"📢 Channel: {CHAT_ID}\n"
        f"🔥 Last scan: OK"
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🛠 <b>HOW TO TRADE WITH LIMIT (BEST)</b>\n\n"
        f"1. Signal says: Entry LIMIT at 0.485\n"
        f"2. Open Binance Futures\n"
        f"3. Order Type -> Change Market to Limit\n"
        f"4. Price -> Type 0.485\n"
        f"5. Check TP/SL box -> Set SL and TP as Conditional\n"
        f"6. Buy/Long or Sell/Short\n\n"
        f"Why LIMIT? Lower fees 0.02% + Better price + No slippage!\n"
        f"Commands: /start /trade /status"
    )

async def run_telegram():
    if not BOT_TOKEN:
        print("No BOT_TOKEN, commands disabled")
        return
    try:
        app_tg = Application.builder().token(BOT_TOKEN).build()
        app_tg.add_handler(CommandHandler("start", start_cmd))
        app_tg.add_handler(CommandHandler("trade", trade_cmd))
        app_tg.add_handler(CommandHandler("status", status_cmd))
        app_tg.add_handler(CommandHandler("help", help_cmd))
        print("Telegram commands /start /trade active!")
        await app_tg.initialize()
        await app_tg.start()
        await app_tg.updater.start_polling()
        # Keep running
        while True:
            await asyncio.sleep(3600)
    except Exception as e:
        print(f"Telegram bot error: {e}")

def run_async_bot():
    try:
        asyncio.run(run_telegram())
    except Exception as e:
        print(f"Async error: {e}")

@app.route('/')
def home():
    return f"SUNNY VIP BOT LIVE - {get_dj_time()} - {len(COINS)} coins - LIMIT Strategy - <a href='https://api.binance.com/api/v3/ping'>Binance OK</a>"

@app.route('/health')
def health():
    return "OK"

if __name__ == "__main__":
    # Start Telegram commands in background thread
    Thread(target=run_async_bot, daemon=True).start()
    # Start scanning loop in background thread
    Thread(target=scanning_loop, daemon=True).start()
    # Start Flask web server (for Render + UptimeRobot)
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
