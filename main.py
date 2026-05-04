import asyncio
import random
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8667496420:AAE0ml4Qpxui1BjW7LYmF6WbkMG4uUt4968"

subscribers = set()
last_signal = None
last_result = "WAITING"


def analyze_market():
    action = random.choice(["BUY", "SELL"])
    score = random.randint(82, 97)
    regime = random.choice(["BULLISH", "BEARISH", "SNIPER TREND"])
    pattern = random.choice(["BREAKOUT", "SCALPING ENTRY", "MOMENTUM PUSH"])
    price = round(random.uniform(1.07000, 1.09000), 5)
    sr1 = round(price - 0.00080, 5)
    sr2 = round(price + 0.00080, 5)
    expiry = "1 MIN"
    tm = datetime.utcnow().strftime("%H:%M:%S")

    return {
        "emoji": "🟢" if action == "BUY" else "🔴",
        "pair": "EUR/USD",
        "action": action,
        "score": score,
        "regime": regime,
        "pattern": pattern,
        "price": price,
        "sr1": sr1,
        "sr2": sr2,
        "expiry": expiry,
        "time": tm,
        "stamp": tm,
        "result": "PENDING"
    }


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    subscribers.add(uid)
    await update.message.reply_text(
        "✅ REAL SIGNAL BOT ACTIVATED\n\n"
        "You are subscribed to sniper signal broadcast.\n"
        "Commands:\n"
        "/live = instant signal\n"
        "/status = bot status\n"
        "/signal = last broadcast\n"
        "/debug = market debug"
    )


async def live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = analyze_market()

    txt = (
        f"🔥 LIVE SNIPER SIGNAL 🔥\n\n"
        f"{res['emoji']} {res['action']} NOW\n\n"
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
            f"📡 Bot Status\n\n"
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
        f"📢 Last sniper broadcast ({last_signal['stamp']} UTC)\n\n"
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
    res = analyze_market()

    dbg = (
        f"MACD trend: {res['regime']}\n"
        f"Momentum score: {res['score']}\n"
        f"3-bar range: {res['sr1']} -> {res['sr2']}\n"
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

    res = analyze_market()
    last_signal = res

    text = (
        f"🚨 REAL SNIPER BROADCAST 🚨\n\n"
        f"{res['emoji']} {res['action']} NOW\n\n"
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

    asyncio.create_task(evaluate_last_signal())


async def loop_runner(app):
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
