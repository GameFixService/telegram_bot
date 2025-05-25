from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

TOKEN = "ТУТ_ВСТАВ_ТОКЕН_БОТА"
CHAT_ID = -1002555460055

# Стан діалогу
DEVICE, ISSUE, CONTACT = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привіт! Я бот GameFix. Що зламалось?")
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

    # Формуємо повідомлення
    msg = (
        "📩 *Нова заявка GameFix:*\n\n"
        f"🛠️ Пристрій: {context.user_data['device']}\n"
        f"⚠️ Проблема: {context.user_data['issue']}\n"
        f"📞 Контакт: {context.user_data['contact']}\n"
        "#GameFix #заявка"
    )

    # Надсилаємо в групу
    await context.bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

    await update.message.reply_text("Дякую! Заявку прийнято ✅")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скасовано.")
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            DEVICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, device)],
            ISSUE: [MessageHandler(filters.TEXT & ~filters.COMMAND, issue)],
            CONTACT: [MessageHandler(filters.TEXT & ~filters.COMMAND, contact)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
