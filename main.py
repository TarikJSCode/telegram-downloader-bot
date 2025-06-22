import os
import requests
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    ContextTypes, CallbackQueryHandler, filters
)
from yt_dlp import YoutubeDL

BOT_TOKEN = os.environ['BOT_TOKEN']
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

VALID_SOURCES = ['tiktok.com', 'instagram.com', 'facebook.com', 'fb.watch', 'pinterest.com', 'pin.it']

# Flask server
flask_app = Flask(__name__)
telegram_app = Application.builder().token(BOT_TOKEN).build()

# --- Команди бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📥 Як скачати відео", callback_data="how_to")],
        [InlineKeyboardButton("➕ Додати в чат", url="https://t.me/videomoment_bot?startgroup=true")],
        [InlineKeyboardButton("📬 Звʼязок з автором", url="https://t.me/shadow_tar")]
    ]
    await update.message.reply_text(
        "👋 Привіт! Я допоможу тобі скачати відео з TikTok, Instagram, Facebook або Pinterest.\n\nНатисни кнопку нижче:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "how_to":
        await query.edit_message_text(
            "📥 *Як скачати відео:*\n\n"
            "1. Знайди відео\n"
            "2. Скопіюй посилання\n"
            "3. Надішли мені\n"
            "4. Отримай готове відео ✅",
            parse_mode="Markdown"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.strip()

    if "pin.it/" in message_text:
        try:
            message_text = requests.head(message_text, allow_redirects=True).url
        except Exception as e:
            print(f"[ERROR] pin.it: {e}")
            return

    if not any(src in message_text for src in VALID_SOURCES):
        return

    await update.message.reply_text("⏳ Завантажую відео...")

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
            await context.bot.send_video(chat_id=update.effective_chat.id, video=video, caption="✅ Готово!")
        os.remove(filename)

    except Exception as e:
        print(f"[ERROR] {e}")

# --- Flask маршрут ---
@flask_app.post(f"/{BOT_TOKEN}")
async def webhook():
    data = await request.get_json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK"

# --- Запуск ---
if __name__ == "__main__":
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CallbackQueryHandler(button_handler))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8080)),
        webhook_url=f"https://telegram-downloader-bot.fly.dev/{BOT_TOKEN}"
    )
