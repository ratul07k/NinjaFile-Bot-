
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

TOKEN = os.environ["BOT_TOKEN"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 স্বাগতম! আমাকে ছবি, PDF, ZIP বা ভিডিও পাঠাও।\n"
        "আমি ফাইলের তথ্য ও পুনরায় পাঠানোর অপশন দেখাব।"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📁 File Bot Help\n"
        "১. আমাকে একটি ফাইল পাঠাও\n"
        "২. ফাইলের তথ্য দেখো\n"
        "৩. Send Again বোতাম চাপো"
    )

async def receive_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    media = msg.document or msg.video or msg.audio

    if media is None and msg.photo:
        media = msg.photo[-1]

    if media is None:
        await msg.reply_text("একটি ছবি, ভিডিও, অডিও বা ডকুমেন্ট পাঠাও।")
        return

    file_name = getattr(media, "file_name", None) or "Telegram media"
    size = getattr(media, "file_size", 0) or 0
    file_id = media.file_id

    context.user_data["last_file"] = file_id
    context.user_data["last_type"] = (
        "document" if msg.document else
        "video" if msg.video else
        "audio" if msg.audio else "photo"
    )

    keyboard = [[InlineKeyboardButton(
        "📤 Send Again", callback_data="send_again"
    )]]

    await msg.reply_text(
        f"✅ ফাইল পেয়েছি!\n"
        f"নাম: {file_name}\n"
        f"সাইজ: {size / (1024 * 1024):.2f} MB",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def send_again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    file_id = context.user_data.get("last_file")
    file_type = context.user_data.get("last_type")

    if not file_id:
        await query.message.reply_text("আগে আমাকে একটি ফাইল পাঠাও।")
        return

    methods = {
        "document": query.message.reply_document,
        "video": query.message.reply_video,
        "audio": query.message.reply_audio,
        "photo": query.message.reply_photo,
    }

    await methods[file_type](file_id)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(send_again, pattern="^send_again$"))
    app.add_handler(MessageHandler(
        filters.Document.ALL | filters.PHOTO |
        filters.VIDEO | filters.AUDIO, receive_file
    ))
    app.run_polling()

if __name__ == "__main__":
    main()
