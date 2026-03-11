import os
from pyrogram import Client, filters, enums
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from info import *
from utils import *
import time
from datetime import datetime
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

@Client.on_message(filters.command(["imdb", "search"]))
async def imdb_search_single(client, message):
    if len(message.command) < 2:
        await message.reply_text("❌ Please provide a movie name.\n\nUsage: `/imdb Loki` or `/search Loki`", parse_mode=enums.ParseMode.HTML)
        return

    movie_name = " ".join(message.command[1:])
    url = f"https://moviedetails.apinepdev.workers.dev/?moviename={movie_name}"
    response = requests.get(url)

    if response.status_code != 200:
        await message.reply_text("⚠️ API request failed. Try again later.")
        return

    mv = response.json()

    if mv.get("Response") == "True":
        caption = f"""✨ <b>{mv.get('Title')}</b> ✨

🎭 <i>{mv.get('Genre')}</i> | ⏳ {mv.get('Runtime')}

<b>🎬 Movie Details</b>

📝 <b>Title:</b> <i>{mv.get('Title')}</i>
📖 <b>Storyline:</b>
<i>{mv.get('Plot')}</i>

📅 <b>Release:</b> {mv.get('Released')}
⏳ <b>Duration:</b> {mv.get('Runtime')}
💠 <b>Genre:</b> {mv.get('Genre')}
🌍 <b>Country:</b> {mv.get('Country')}

🎦 <b>Director:</b> {mv.get('Director')}
✍️ <b>Writer:</b> {mv.get('Writer')}
👥 <b>Actors:</b> {mv.get('Actors')}

💰 <b>Box Office:</b> {mv.get('BoxOffice', 'N/A')}
⭐ <b>IMDB:</b> <i>{mv.get('imdbRating')}/10</i>
"""

        poster = mv.get("Poster")
        if poster and poster != "N/A":
            await message.reply_photo(photo=poster, caption=caption, parse_mode=enums.ParseMode.HTML)
        else:
            await message.reply_text(caption, parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply_text("❌ <b>Movie Not Found!</b>\n\n🔍 Please check the name again.", parse_mode=enums.ParseMode.HTML)

