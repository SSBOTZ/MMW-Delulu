import os
import sys
import re
import time
import shutil
import asyncio
import logging
import logging.config
import psutil

from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery
)
from pyrogram.errors import ChatAdminRequired, PeerIdInvalid
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong

from info import *
from Script import script
from utils import *

from database.users_chats_db import db
from database.ia_filterdb import (
    save_file,
    Media, Media2, Media3, Media4, Media5,
    db as clientDB,
    db2 as clientDB2,
    db3 as clientDB3,
    db4 as clientDB4,
    db5 as clientDB5
)

media_filter = filters.document | filters.video

@Client.on_message(filters.chat(CHANNELS) & media_filter)    
async def media(bot, message):    
    media = message.document or message.video    
    if not media:    
        return    
    
    media.file_type = message.file_type    
    media.caption = message.caption    
    
    try:    
        await save_file(media)    
    except:    
        pass    
    
@Client.on_message(filters.command("channel") & filters.user(ADMINS))    
async def channel_info(bot: Client, message: Message):    
    try:    
        channels = CHANNELS if isinstance(CHANNELS, list) else [CHANNELS]    
    
        text = "📜 **Indexed Channels / Groups:**\n"    
    
        for channel in channels:    
            try:    
                chat = await bot.get_chat(channel)    
                if chat.username:    
                    text += f"\n✅ @{chat.username}"    
                else:    
                    name = chat.title or chat.first_name or "Unnamed"    
                    text += f"\n✅ {name}"    
            except:    
                text += f"\n⚠️ `{channel}`"    
    
        text += f"\n\n📊 **Total Indexed:** {len(channels)}"    
    
        if len(text) < 4096:    
            await message.reply_text(text)    
        else:    
            file_path = "Indexed_Channels.txt"    
            with open(file_path, "w", encoding="utf-8") as f:    
                f.write(text)    
            await message.reply_document(file_path)    
            os.remove(file_path)    
    
    except Exception as e:    
        await message.reply_text(f"❌ Failed to fetch channel info!\nError: {str(e)}")    
    
