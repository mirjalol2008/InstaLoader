import os
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
AUDD_TOKEN = os.getenv("AUDD_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Instagram link yuboring. Men sizga videoni va musiqasini topib beraman.")

async def download_instagram(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith("https://www.instagram.com/"):
        await update.message.reply_text("Iltimos, Instagram post yoki reels link yuboring.")
        return

    try:
        response = requests.get(f"https://api.diegormirhan.com/api/download?url={url}")
        if response.status_code == 200:
            result = response.json()
            for media in result["media"]:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("Musiqani topish", callback_data=f"find_music|{media['url']}")]
                ])
                await update.message.reply_video(media["url"], reply_markup=keyboard)
        else:
            await update.message.reply_text("Media topilmadi.")
    except Exception as e:
        await update.message.reply_text("Xatolik: " + str(e))

async def find_music_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    video_url = query.data.split("|")[1]
    await query.edit_message_caption(caption="Musiqa aniqlanmoqda...")

    try:
        # Videoni vaqtincha saqlash
        response = requests.get(video_url)
        with open("temp_video.mp4", "wb") as f:
            f.write(response.content)

        # Musiqa aniqlash
        files = {'file': open("temp_video.mp4", 'rb')}
        data = {'api_token': AUDD_TOKEN, 'return': 'apple_music,spotify'}
        r = requests.post('https://api.audd.io/', data=data, files=files)
        result = r.json()

        if result['status'] == 'success' and result['result']:
            track = result['result']
            title = track['title']
            artist = track['artist']
            await query.edit_message_caption(caption=f"Musiqa: {title} - {artist}")
        else:
            await query.edit_message_caption(caption="Musiqa aniqlanmadi.")

        os.remove("temp_video.mp4")

    except Exception as e:
        await query.edit_message_caption(caption=f"Xatolik yuz berdi: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_instagram))
    app.add_handler(CallbackQueryHandler(find_music_callback, pattern="^find_music"))
    app.run_polling()