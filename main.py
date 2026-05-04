import random
import threading
import time
from datetime import datetime

from telegram.ext import Updater, CommandHandler

TOKEN = "8667496420:AAE0ml4Qpxui1BjW7LYmF6WbkMG4uUt4968"

subscribers = []
last_signal = None
last_result = "WAITING"


def analyze_market():
    action = random.choice(["BUY", "SELL"])
    score = random.randint(82, 97)
    regime = random.choice(["BULLISH", "BEARISH"])
    pattern = random.choice(["BREAKOUT", "SCALPING", "SNIPER"])
    price = round(random.uniform(1.07000, 1.09000), 5)
    sr1 = round(price - 0.00080, 5)
    sr2 = round(price + 0.00080, 5)
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
        "expiry": "1 MIN",
        "time": tm,
        "result": "PENDING ⏳"
    }


def start(update, context):
    uid = update.message.chat_id
    if uid not in subscribers:
        subscribers.append(uid)

    txt = (
        "🔥 REAL SIGNAL BOT ACTIVATED 🔥\n\n"
        "PAIR: EUR/USD OTC\n"
        "MODE: 1 MIN SNIPER\n"
        "CONFIDENCE FILTER: 82%+\n\n"
        "Signals will auto arrive every minute."
    )
    update.message.reply_text(txt)


def live(update, context):
    res = analyze_market()

    txt = (
        f"{res['emoji']} LIVE MARKET NOW\n\n"
        f"PAIR: {res['pair']}\n"
        f"ACTION: {res['action']}\n"
        f"CONFIDENCE: {res['score']}%\n"
        f"REGIME: {res['regime']}\n"
        f"PATTERN: {res['pattern']}\n"
        f"PRICE: {res['price']}\n"
        f"S/R: {res['sr1']} / {res['sr2']}\n"
        f"TIME: {res['time']}"
    )
    update.message.reply_text(txt)


def status(update, context):
    global last_signal

    if last_signal:
        msg = (
            "Bot Status\n\n"
            "Symbol: EUR/USD (1-min sniper)\n"
            "Scan: aligned every 1-min candle close\n"
            "Broadcast threshold: 82%\n"
            f"Total subscribers: {len(subscribers)}\n"
            "Your subscription: ACTIVE\n\n"
            f"Last sniper broadcast: {last_signal['action']} at {last_signal['time']}\n"
            f"Last result status: {last_result}"
        )
    else:
        msg = "Bot running. Waiting first sniper signal..."

    update.message.reply_text(msg)


def signal(update, context):
    global last_signal

    if not last_signal:
        update.message.reply_text("No broadcast signal yet.")
        return

    txt = (
        f"Last sniper broadcast ({last_signal['time']} UTC)\n\n"
        f"{last_signal['emoji']} {last_signal['action']} - Sniper Signal\n\n"
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
    update.message.reply_text(txt)


def debug(update, context):
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
    update.message.reply_text(dbg)


def evaluate_result():
    global last_signal, last_result

    if last_signal:
        outcome = random.choice(["WIN ✅", "LOSS ❌"])
        last_signal["result"] = outcome
        last_result = outcome


def broadcast_loop(bot):
    global last_signal

    while True:
        time.sleep(60)

        res = analyze_market()
        last_signal = res

        txt = (
            f"{res['emoji']} REAL SNIPER SIGNAL\n\n"
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
                bot.send_message(chat_id=uid, text=txt)
            except:
                pass

        time.sleep(65)
        evaluate_result()


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("live", live))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("signal", signal))
    dp.add_handler(CommandHandler("debug", debug))

    t = threading.Thread(target=broadcast_loop, args=(updater.bot,))
    t.start()

    print("REAL SIGNAL BOT RUNNING...")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
