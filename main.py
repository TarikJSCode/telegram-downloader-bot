import os
import re
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import yt_dlp
from dotenv import load_dotenv

# Завантаження токена з .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Функція завантаження відео
def download_video(url: str, output_path: str = "video.mp4", cookies_file: str = None) -> str:
    ydl_opts = {
        'outtmpl': output_path,
        'format': 'mp4',
        'quiet': True,
    }

    if cookies_file and os.path.exists(cookies_file):
        ydl_opts['cookiefile'] = cookies_file

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return output_path

# Обробник повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # Перевірка наявності URL-адреси
    if re.match(r'https?://(www\.)?(tiktok\.com|instagram\.com)/', text):
        await update.message.reply_text("⏳ Зачекайте, йде завантаження відео...")

        try:
            # Вказати шлях до файлу куків
            cookies_file = "path/to/your/cookies.txt"  # Змініть на свій шлях до файлу куків
            file_path = download_video(text, cookies_file=cookies_file)
            await update.message.reply_video(video=open(file_path, 'rb'))
            os.remove(file_path)
        except Exception as e:
            await update.message.reply_text(f"❌ Сталася помилка:\n{e}")
    else:
        await update.message.reply_text("⚠️ Будь ласка, надішліть дійсну URL-адресу на відео з TikTok або Instagram.")

# Запуск бота
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущено...")
    app.run_polling()
