import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler, filters
from yt_dlp import YoutubeDL
from keep_alive import keep_alive
keep_alive()

BOT_TOKEN = os.environ['BOT_TOKEN']
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

VALID_SOURCES = ['tiktok.com', 'instagram.com', 'facebook.com', 'fb.watch', 'pinterest.com', 'pin.it']

# /start команда з кнопками
# /start команда з кнопками
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📥 Як скачати відео", callback_data="how_to")],
        [InlineKeyboardButton("➕ Додати мене в чат", url="https://t.me/videomoment_bot?startgroup=true")],
        [InlineKeyboardButton("📬 Звʼязок з автором", url="https://t.me/shadow_tar")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👋 Привіт! Я допоможу тобі скачати відео з TikTok, Instagram, Facebook або Pinterest.\n\nНатисни кнопку нижче:",
        reply_markup=reply_markup
    )

    

# Обробка натискання кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "how_to":
        await query.edit_message_text(
            "📥 *Як скачати відео:*\n\n"
            "1. Знайди відео в TikTok, Instagram, Facebook або Pinterest\n"
            "2. Скопіюй посилання\n"
            "3. Надішли мені в цей чат\n"
            "4. Я пришлю тобі готове відео ✅",
            parse_mode="Markdown"
        )

# Обробка повідомлень з посиланнями
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text.strip()
    print(f"[LOG] Отримано повідомлення: {message_text}")

    # Розширити коротке посилання pin.it
    if "pin.it/" in message_text:
        try:
            response = requests.head(message_text, allow_redirects=True)
            message_text = response.url
            print(f"[LOG] Розширено pin.it до: {message_text}")
        except Exception as e:
            print(f"[ERROR] Не вдалося розширити pin.it: {e}")
            return

    if not any(src in message_text for src in VALID_SOURCES):
        return

    await update.message.reply_text("⏳ Завантажую відео, зачекай трохи...")

    try:
        # Обираємо відповідний cookie-файл
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
        # Бот не відповідає, щоб не засмічувати чат

# Запуск
if __name__ == '__main__':
    print("🚀 Запускаємо бота...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
