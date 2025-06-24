
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
import yt_dlp

BOT_TOKEN = "7867872356:AAFeLpiH8ha7ptDOJMwfhUyrItkLmisZjKs"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("أرسل رابط فيديو من YouTube أو TikTok")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    keyboard = [
        [
            InlineKeyboardButton("📥 تحميل الفيديو", callback_data=f"video|{url}"),
            InlineKeyboardButton("🎧 تحميل الصوت", callback_data=f"audio|{url}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("اختر نوع التحميل:", reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    action, url = data.split("|")

    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'format': 'bestvideo+bestaudio/best' if action == 'video' else 'bestaudio/best',
        'quiet': True,
    }

    file_path = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        await query.edit_message_text(text="جاري الإرسال...")
        await query.message.reply_document(document=open(file_path, 'rb'))
    except Exception as e:
        await query.edit_message_text(f"حدث خطأ: {e}")
    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app.add_handler(CallbackQueryHandler(button))
    print("البوت يعمل الآن...")
    app.run_polling()
