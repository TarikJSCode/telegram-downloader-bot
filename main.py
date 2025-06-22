
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
import os
import logging
if __name__ == '__main__':
    from keep_alive import keep_alive
    keep_alive()  # Це запускає Flask на 0.0.0.0:8080


# Логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Функція завантаження відео
def download_video(url: str, output_path: str = "video.mp4") -> str:
    ydl_opts = {
        'outtmpl': output_path,
        'format': 'mp4',
        'quiet': True,
        'cookiefile': 'instagram_cookies.txt', 
        'cookiefile': 'pinterest_cookies.txt',# Файл cookies для Instagram
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path

# Обробник повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "tiktok.com" in text or "instagram.com" in text:
        await update.message.reply_text("⏳ Зачекайте, йде завантаження відео...")

        try:
            file_path = download_video(text)
            await update.message.reply_video(video=open(file_path, 'rb'))
            os.remove(file_path)
        except Exception as e:
            await update.message.reply_text(f"❌ Сталася помилка:\n{e}")
    else:
        await update.message.reply_text("Будь ласка, надішліть посилання на відео з TikTok або Instagram.")

# Запуск бота
if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()
