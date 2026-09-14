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

Analyze this trading chart screenshot carefully.

Give an educational technical analysis only. Never claim certainty
and never guarantee profit.

Return the analysis in this format:

📊 CHART ANALYSIS

Asset:
Timeframe:

📈 Trend:
- Overall trend
- Short-term momentum

🧱 Support:
- Important support levels

🚧 Resistance:
- Important resistance levels

🕯 Price Action:
- Candle structure
- Breakout/rejection if visible

🎯 SIGNAL:
BUY / SELL / WAIT

📍 Possible Entry:
Only if a reasonable setup is visible.

🛑 Stop Loss:
Only if a reasonable level can be estimated.

🎯 Take Profit:
Only if a reasonable level can be estimated.

📊 Confidence:
Low / Medium / High

⚠️ Risk:
Explain why the setup may fail.

IMPORTANT:
- If confirmation is weak, choose WAIT.
- Do not invent prices that are not visible.
- Do not promise profit.
- This is educational analysis, not financial advice.
"""

    payload = {
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ],
        "max_tokens": 1500
    }

    data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + OPENAI_API_KEY
        },
        method="POST"
    )

    with urllib.request.urlopen(request, timeout=120) as response:
        result = json.loads(response.read().decode("utf-8"))

    if "choices" in result and len(result["choices"]) > 0:
        return result["choices"][0]["message"]["content"]
    
    return ""


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
            "���� Chart analysis চলছে...\n⏳ একটু অপেক্ষা করুন।"
        )

        file_info = bot.get_file(message.photo[-1].file_id)
        image_bytes = bot.download_file(file_info.file_path)

        analysis = analyze_chart(image_bytes)

        if not analysis:
            analysis = "❌ Analysis পাওয়া যায়নি। আবার screenshot পাঠান।"

        bot.reply_to(message, analysis)

    except urllib.error.HTTPError as e:
        error = e.read().decode("utf-8", errors="ignore")
        print("OpenAI API Error:", error)
        bot.reply_to(
            message,
            "❌ OpenAI API error হয়েছে। Railway Variables এবং API credits check করুন।"
        )

    except Exception as e:
        print("Bot Error:", str(e))
        bot.reply_to(
            message,
            "❌ Analysis করতে সমস্যা হয়েছে। আবার chart screenshot পাঠান।"
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
