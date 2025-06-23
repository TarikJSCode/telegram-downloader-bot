from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os
import logging
import browser_cookie3  # Для отримання cookies з браузера

if __name__ == '__main__':
    from keep_alive import keep_alive
    keep_alive()  # Це запускає Flask на 0.0.0.0:8080

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

    # Якщо файл cookies існує, додаємо його до параметрів
    if cookies_file and os.path.exists(cookies_file):
        ydl_opts['cookiefile'] = cookies_file
    else:
        # Отримуємо cookies з браузера
        cookies = browser_cookie3.chrome()  # можна використовувати firefox() для Firefox
        ydl_opts['cookies'] = cookies  # додаємо cookies в параметри

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        raise Exception(f"Помилка при завантаженні відео: {str(e)}")

    return output_path

# Обробник повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Перевірка на наявність посилання
    if "http" in text and ("tiktok.com" in text or "instagram.com" in text):
        await update.message.reply_text("⏳ Зачекайте, йде завантаження відео...")

        try:
            file_path = download_video(text)
            await update.message.reply_video(video=open(file_path, 'rb'))
            os.remove(file_path)
        except Exception as e:
            await update.message.reply_text(f"❌ Сталася помилка:\n{e}")
    else:
        await update.message.reply_text("Будь ласка, надішліть правильне посилання на відео з TikTok або Instagram.")

# Запуск бота
if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    # Додаємо обробник, який реагує тільки на текстові повідомлення з посиланням
    app.add_handler(MessageHandler(filters.TEXT & filters.regex(r'http.*(?:tiktok|instagram)\.com'), handle_message))

    print("Bot is running...")
    app.run_polling()
