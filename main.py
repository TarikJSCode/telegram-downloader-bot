import os
import requests
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    CallbackQueryHandler,
    filters
)
from yt_dlp import YoutubeDL
from flask import Flask, request
import threading

# === Налаштування ===
BOT_TOKEN = os.environ.get("BOT_TOKEN")
RENDER_HOST = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
WEBHOOK_PATH = f"/{BOT_TOKEN}"
WEBHOOK_URL = f"https://{RENDER_HOST}{WEBHOOK_PATH}"
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

VALID_SOURCES = [
    'tiktok.com', 'instagram.com', 'facebook.com', 'fb.watch', 'pinterest.com', 'pin.it'
]

# === Flask для webhook ===
flask_app = Flask(__name__)

@flask_app.route("/", methods=["GET"])
def index():
    return "Bot is alive!"

@flask_app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, app.bot)
    asyncio.run(app.process_update(update))
    return "ok", 200

# === Хендлери ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📅 Як скачати відео", callback_data="how_to")],
        [InlineKeyboardButton("➕ Додати мене в чат", url="https://t.me/videomoment_bot?startgroup=true")],
        [InlineKeyboardButton("📬 Звʼязок з автором", url="https://t.me/shadow_tar")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Привіт! Я допоможу тобі скачати відео з TikTok, Instagram, Facebook або Pinterest.\n\nНатисни кнопку нижче:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "how_to":
        await query.edit_message_text(
            "📅 *Як скачати відео:*\n\n"
            "1. Знайди відео в TikTok, Instagram, Facebook або Pinterest\n"
            "2. Скопіюй посилання\n"
            "3. Надішли мені в цей чат\n"
            "4. Я пришлю тобі готове відео ✅",
            parse_mode="Markdown"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.strip()
    print(f"[LOG] Отримано повідомлення: {message_text}")

    if "pin.it/" in message_text:
        try:
            response = requests.head(message_text, allow_redirects=True)
            message_text = response.url
        except Exception as e:
            print(f"[ERROR] Розширення pin.it: {e}")
            return

    if not any(src in message_text for src in VALID_SOURCES):
        return

    await update.message.reply_text("⏳ Завантажую відео, зачекай трохи...")

    try:
        cookie_file = None
        if 'instagram.com' in message_text:
            cookie_file = 'instagram_cookies.txt'
        elif 'pinterest.com' in message_text:
            cookie_file = 'pinterest_cookies.txt'

        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/%(title).70s.%(ext)s',
            'format': 'mp4',
            'quiet': True,
            'noplaylist': True,
        }

        if cookie_file:
            ydl_opts['cookiefile'] = cookie_file

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(message_text, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as video:
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=video,
                caption="✅ Готово!"
            )
        os.remove(filename)

    except Exception as e:
        print(f"[ERROR] Завантаження відео: {e}")
        await update.message.reply_text("❌ Сталася помилка при завантаженні відео.")

# === Telegram Application ===
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# === Flask запуск окремо ===
PORT = int(os.environ.get("PORT", 8080))
threading.Thread(target=lambda: flask_app.run(host="0.0.0.0", port=PORT)).start()

# === Webhook запуск ===
async def setup():
    await app.bot.set_webhook(WEBHOOK_URL)
    print(f"✅ Webhook встановлено: {WEBHOOK_URL}")

asyncio.run(setup())
