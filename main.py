import os
import base64
import json
import urllib.request
import urllib.error
import telebot

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")

bot = telebot.TeleBot(TOKEN)


def analyze_chart(image_bytes):
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    image_url = "data:image/jpeg;base64," + image_b64

    prompt = """
You are an expert technical market analyst.

Analyze the trading chart screenshot carefully.

This is educational technical analysis only.
Never guarantee profit or certainty.

Return the analysis in this format:

📊 CHART ANALYSIS

Asset:
Timeframe:

📈 TREND
Overall trend:
Short-term momentum:

🧱 SUPPORT
Important support levels:

🚧 RESISTANCE
Important resistance levels:

🕯 PRICE ACTION
Candle structure:
Breakout/rejection:

🎯 SIGNAL
BUY / SELL / WAIT

📍 POSSIBLE ENTRY
Only give an entry if a clear setup exists.

🛑 STOP LOSS
Only give a reasonable level visible from the chart.

🎯 TAKE PROFIT
Only give a reasonable level visible from the chart.

📊 CONFIDENCE
Low / Medium / High

⚠️ RISK
Explain why the setup could fail.

IMPORTANT RULES:
- If confirmation is weak, choose WAIT.
- Never invent prices.
- Never guarantee profit.
- Never claim certainty.
- Do not encourage reckless risk.
- This is educational technical analysis, not financial advice.
"""

    payload = {
        "model": "gpt-5.6-luna",
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt
                    },
                    {
                        "type": "input_image",
                        "image_url": image_url
                    }
                ]
            }
        ]
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + OPENAI_API_KEY
        },
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))

    texts = []

    for item in result.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                text = content.get("text", "")
                if text:
                    texts.append(text)

    return "\n".join(texts).strip()


@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):
    bot.reply_to(
        message,
        "🤖 Advanced Trading Bot চালু আছে! ✅\n\n"
        "📸 একটি trading chart screenshot পাঠান।\n\n"
        "আমি Trend, Support, Resistance, "
        "BUY/SELL/WAIT, Entry, SL, TP এবং Confidence বিশ্লেষণ করব।"
    )


@bot.message_handler(content_types=["photo"])
def handle_chart(message):
    try:
        bot.reply_to(
            message,
            "🔍 Chart analysis চলছে...\n"
            "⏳ একটু অপেক্ষা করুন।"
        )

        file_info = bot.get_file(message.photo[-1].file_id)
        image_bytes = bot.download_file(file_info.file_path)

        analysis = analyze_chart(image_bytes)

        if not analysis:
            analysis = (
                "❌ Analysis পাওয়া যায়নি।\n"
                "আবার chart screenshot পাঠান।"
            )

        bot.reply_to(message, analysis)

    except urllib.error.HTTPError as e:
        error = e.read().decode("utf-8", errors="ignore")
        print("OpenAI API Error:", error)

        bot.reply_to(
            message,
            "❌ OpenAI API error হয়েছে।\n\n"
            "Railway Variables এবং OpenAI API credits check করুন।"
        )

    except Exception as e:
        print("Bot Error:", str(e))

        bot.reply_to(
            message,
            "❌ Analysis করতে সমস্যা হয়েছে।\n"
            "আবার chart screenshot পাঠান।"
        )


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(
        message,
        "📸 Chart screenshot পাঠান।\n"
        "আমি সেটি analyze করব।"
    )


print("🤖 Advanced Trading Bot started successfully!")

bot.delete_webhook(drop_pending_updates=True)
bot.infinity_polling()
