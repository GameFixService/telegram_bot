import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ConversationHandler, ContextTypes
)

TOKEN = os.getenv("TOKEN")
CHAT_ID = -1002555460055  # Замініть на ваш Chat ID
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Наприклад: https://your-app.onrender.com/webhook

# Стан діалогу
DEVICE, ISSUE, CONTACT = range(3)

app = Flask(__name__)
application = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привіт! Що зламалось?")
    return DEVICE

async def device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['device'] = update.message.text
    await update.message.reply_text("Опиши коротко проблему:")
    return ISSUE

async def issue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['issue'] = update.message.text
    await update.message.reply_text("Залиши контакт (телефон або @username):")
    return CONTACT

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['contact'] = update.message.text

    msg = (
        "📩 *Нова заявка GameFix:*\n\n"
        f"🛠️ Пристрій: {context.user_data['device']}\n"
        f"⚠️ Проблема: {context.user_data['issue']}\n"
        f"📞 Контакт: {context.user_data['contact']}\n"
        "#GameFix #заявка"
    )

    await context.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")
    await update.message.reply_text("Дякую! Заявку прийнято ✅")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скасовано.")
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        DEVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, device)],
        ISSUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, issue)],
        CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

application.add_handler(conv_handler)

@app.route("/")
def index():
    return "Bot is running."

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        asyncio.run(application.update_queue.put(Update.de_json(request.get_json(force=True), application.bot)))
        return "ok"

if __name__ == "__main__":
    import telegram
    bot = telegram.Bot(token=TOKEN)
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
