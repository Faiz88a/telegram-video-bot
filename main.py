import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import yt_dlp
import os

TOKEN = "7867872356:AAE6KTT4FY9ysr3zpxVvZgiU2u8kHO9kOEY"
logging.basicConfig(level=logging.INFO)

# زر البداية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحبًا 👋\nأرسل رابط يوتيوب وسأعطيك خيارات التحميل 🎵📹"
    )

# لما المستخدم يرسل رابط
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    keyboard = [
        [InlineKeyboardButton("🎵 تحميل صوت", callback_data="audio|" + url),
         InlineKeyboardButton("📹 تحميل فيديو", callback_data="video|" + url)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر نوع التحميل:", reply_markup=reply_markup)

# لما يضغط زر
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, url = query.data.split("|", 1)

    msg = await query.edit_message_text("⏳ جاري التحميل، انتظر قليلاً...")

    ydl_opts = {
        "outtmpl": "%(title)s.%(ext)s"
    }

    if action == "audio":
        ydl_opts.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            }]
        })
    else:
        ydl_opts.update({"format": "best"})

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if action == "audio":
                filename = filename.rsplit(".", 1)[0] + ".mp3"

        with open(filename, "rb") as f:
            if action == "audio":
                await context.bot.send_audio(chat_id=query.message.chat.id, audio=f)
            else:
                await context.bot.send_video(chat_id=query.message.chat.id, video=f)

        os.remove(filename)
        await msg.edit_text("✅ تم الإرسال!")
    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ: {e}")

# تشغيل البوت
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == "__main__":
    main()
