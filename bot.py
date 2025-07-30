import logging
import requests
import os
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# --- API KEYS from ENV ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TMDB_API_KEY = os.environ.get("TMDB_API_KEY")

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Movie Search Function ---
def search_movie(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["results"]:
            return data["results"][0]
    return None

# --- /start handler ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Welcome! Send me a movie name and I’ll get the info + download link.")

# --- Message handler ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    movie = search_movie(query)

    if movie:
        title = movie.get("title", "No Title")
        overview = movie.get("overview", "No Description Available.")
        poster_path = movie.get("poster_path")
        poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
        download_link = f"https://newzbysms.com/?s={'+'.join(title.split())}"
        caption = f"🎬 *{title}*\n\n📝 {overview}\n\n🔗 [Download Here]({download_link})"

        if poster_url:
            await update.message.reply_photo(
                photo=poster_url,
                caption=caption,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔗 Download from Newzbysms", url=download_link)]
                ])
            )
        else:
            await update.message.reply_text(caption, parse_mode="Markdown")
    else:
        await update.message.reply_text("😔 Sorry, movie not found.")

# --- Main ---
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
