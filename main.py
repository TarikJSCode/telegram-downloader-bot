# main.py
import os
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
import requests

BOT_TOKEN = os.environ.get("BOT_TOKEN")
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

VALID_SOURCES = [
    'tiktok.com', 'instagram.com', 'facebook.com', 'fb.watch', 'pinterest.com', 'pin.it'
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("\ud83d\udcc5 Як скачати відео", callback_data="how_to")],
        [InlineKeyboardButton("\u2795 Додати мене в чат", url="https://t.me/videomoment_bot?startgroup=true")],
        [InlineKeyboardButton("\ud83d\udcec Звʼязок з автором", url="https://t.me/shadow_tar")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "\ud83d\udc4b Привіт! Я допоможу тобі скачати відео з TikTok, Instagram, Facebook або Pinterest.\n\nНатисни кнопку нижче:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "how_to":
        await query.edit_message_text(
            "\ud83d\udcc5 *Як скачати відео:*\n\n"
            "1. Знайди відео в TikTok, Instagram, Facebook або Pinterest\n"
            "2. Скопіюй посилання\n"
            "3. Надішли мені в цей чат\n"
            "4. Я пришлю тобі готове відео ✅",
            parse_mode="Markdown"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.strip()
    if "pin.it/" in message_text:
        try:
            response = requests.head(message_text, allow_redirects=True)
            message_text = response.url
        except:
            return

    if not any(src in message_text for src in VALID_SOURCES):
        return

    await update.message.reply_text("⏳ Завантажую відео, зачекай трохи...")

    try:
        ydl_opts = {
            'outtmpl': f'{DOWNLOAD_DIR}/%(title).70s.%(ext)s',
            'format': 'mp4',
            'quiet': True,
            'noplaylist': True,
        }
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
        print(f"[ERROR] {e}")
        await update.message.reply_text("❌ Помилка при завантаженні відео.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущено через polling")
    app.run_polling()
