import os
import telebot

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set")

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):
    bot.reply_to(
        message,
        "🤖 Hello! I'm your Telegram bot.\n\n"
        "Bot is working successfully! ✅"
    )


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


print("🤖 Bot started successfully!")

bot.delete_webhook(drop_pending_updates=True)
bot.infinity_polling()
