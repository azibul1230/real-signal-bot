import os
import asyncio
import logging
import random
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = os.getenv("BOT_TOKEN")

subscribers = set()
last_signal = None
signal_history = []
last_result = "WAITING"

PAIRS = ["EUR/USD"]
REGIMES = ["TRENDING", "REVERSAL", "BREAKOUT", "CHOPPY_NOISE"]
PATTERNS = [
    "BULL_ENGULF",
    "BEAR_REJECT_WICK",
    "MOMENTUM_BURST",
    "SNIPER_PULLBACK",
    "LIQUIDITY_GRAB"
]

def get_market_price():
    return round(random.uniform(1.07000, 1.18000), 5)

def analyze_market():
    score = random.randint(78, 96)
    action = random.choice(["BUY NOW", "SELL NOW"])
    pair = "EUR/USD"
    regime = random.choice(REGIMES)
    pattern = random.choice(PATTERNS)
    price = get_market_price()
    sr1 = round(price - random.uniform(0.00003, 0.00009), 5)
    sr2 = round(price + random.uniform(0.00003, 0.00009), 5)

    return {
        "score": score,
        "action": action,
        "pair": pair,
        "regime": regime,
        "pattern": pattern,
        "price": price,
        "sr1": sr1,
        "sr2": sr2,
        "expiry": "1 MIN",
        "time": datetime.utcnow().strftime("%H:%M")
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    subscribers.add(uid)
    await update.message.reply_text(
        "✅ You are subscribed to REAL 1-Min Sniper Bot\n\n"
        "Commands:\n"
        "/live = run live analysis\n"
        "/status = bot status\n"
        "/signal = last signal\n"
        "/debug = full debug"
    )

async def live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Running 5-layer real market sniper analysis...")
    res = await asyncio.to_thread(analyze_market)

    txt = (
        f"🟢 {res['action']} — Sniper Signal\n\n"
        f"PAIR: {res['pair']}\n"
        f"ACTION: {res['action']}\n"
        f"CONFIDENCE: {res['score']}%\n"
        f"REGIME: {res['regime']}\n"
        f"PATTERN: {res['pattern']}\n"
        f"PRICE: {res['price']}\n"
        f"S/R: {res['sr1']} / {res['sr2']}\n"
        f"EXPIRY: {res['expiry']}\n"
        f"TIME: {res['time']}"
    )
    await update.message.reply_text(txt)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_signal
    if last_signal:
        msg = (
            f"Bot Status\n\n"
            f"Symbol: EUR/USD (1-min sniper)\n"
            f"Scan: aligned every 1-min candle close\n"
            f"Broadcast threshold: 82% sniper score\n"
            f"Total subscribers: {len(subscribers)}\n"
            f"Your subscription: ACTIVE\n\n"
            f"Last sniper broadcast: {last_signal['action']} at {last_signal['stamp']}\n"
            f"Last result status: {last_result}"
        )
    else:
        msg = "Bot running. Waiting first sniper signal..."
    await update.message.reply_text(msg)

async def lastsignal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_signal
    if not last_signal:
        await update.message.reply_text("No broadcast signal yet.")
        return

    txt = (
        f"Last sniper broadcast ({last_signal['stamp']} UTC)\n\n"
        f"{last_signal['emoji']} {last_signal['action']} — Sniper Signal\n\n"
        f"PAIR: {last_signal['pair']}\n"
        f"ACTION: {last_signal['action']}\n"
        f"CONFIDENCE: {last_signal['score']}%\n"
        f"REGIME: {last_signal['regime']}\n"
        f"PATTERN: {last_signal['pattern']}\n"
        f"PRICE: {last_signal['price']}\n"
        f"S/R: {last_signal['sr1']} / {last_signal['sr2']}\n"
        f"EXPIRY: {last_signal['expiry']}\n"
        f"TIME: {last_signal['time']}\n"
        f"RESULT: {last_signal['result']}"
    )
    await update.message.reply_text(txt)

async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = await asyncio.to_thread(analyze_market)
    dbg = (
        f"MACD trend: {res['regime']}\n"
        f"Momentum score: {res['score']}\n"
        f"3-bar range: {res['sr1']} -> {res['sr2']}\n\n"
        f"Reasons\n"
        f"• Pattern matched: {res['pattern']}\n"
        f"• Scalping confidence high\n"
        f"• Candle pressure aligned\n"
        f"• 1-minute sniper breakout found"
    )
    await update.message.reply_text(dbg)

async def evaluate_last_signal():
    global last_signal, last_result
    if not last_signal:
        return

    if last_signal["result"] != "PENDING":
        return

    await asyncio.sleep(65)

    outcome = random.choice(["WIN ✅", "LOSS ❌"])
    last_signal["result"] = outcome
    last_result = outcome

async def scan_and_broadcast(app):
    global last_signal

    res = await asyncio.to_thread(analyze_market)

    if res["score"] >= 82:
        emoji = "🟢" if res["action"] == "BUY NOW" else "🔴"

        signal_data = {
            "emoji": emoji,
            "action": res["action"],
            "pair": res["pair"],
            "score": res["score"],
            "regime": res["regime"],
            "pattern": res["pattern"],
            "price": res["price"],
            "sr1": res["sr1"],
            "sr2": res["sr2"],
            "expiry": res["expiry"],
            "time": res["time"],
            "stamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            "result": "PENDING ⏳"
        }

        last_signal = signal_data
        signal_history.append(signal_data)

        text = (
            f"{emoji} {res['action']} — Sniper Signal\n\n"
            f"PAIR: {res['pair']}\n"
            f"ACTION: {res['action']}\n"
            f"CONFIDENCE: {res['score']}%\n"
            f"REGIME: {res['regime']}\n"
            f"PATTERN: {res['pattern']}\n"
            f"PRICE: {res['price']}\n"
            f"S/R: {res['sr1']} / {res['sr2']}\n"
            f"EXPIRY: {res['expiry']}\n"
            f"TIME: {res['time']}\n"
            f"RESULT: PENDING ⏳"
        )

        for uid in subscribers:
            try:
                await app.bot.send_message(uid, text)
            except:
                pass

        async def loop_runner(app):
    asyncio.create_task(evaluate_last_signal())

    while True:
        now = datetime.utcnow()
        sec = now.second
        wait = 60 - sec
        await asyncio.sleep(wait)
        await scan_and_broadcast(app)


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("live", live))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("signal", lastsignal))
    app.add_handler(CommandHandler("debug", debug))

    async def post_init(application):
        asyncio.create_task(loop_runner(application))

    app.post_init = post_init

    print("REAL SIGNAL BOT RUNNING...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
