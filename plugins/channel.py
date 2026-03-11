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
from info import ADMINS

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
    
@Client.on_message(filters.command("stats") & filters.incoming)
async def get_stats(bot, message):
    if message.from_user.id not in ADMINS:
        k = await message.reply_text("<b>🚫 ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.</b>")
        await asyncio.sleep(10)
        await k.delete()
        await message.delete()
        return
    msg = await message.reply("<b>♻️ 𝚂𝚃𝙰𝚃𝚄𝚂 𝙳𝙴𝚃𝙰𝙸𝙻𝚂... ♻️</b>")

    users = await db.total_users_count()
    chats = await db.total_chat_count()

    tot1 = await Media.count_documents({})
    tot2 = await Media2.count_documents({})
    tot3 = await Media3.count_documents({})
    tot4 = await Media4.count_documents({})
    tot5 = await Media5.count_documents({})

    total_files = tot1 + tot2 + tot3 + tot4 + tot5

    s1 = await clientDB.command("dbStats")
    s2 = await clientDB2.command("dbStats")
    s3 = await clientDB3.command("dbStats")
    s4 = await clientDB4.command("dbStats")
    s5 = await clientDB5.command("dbStats")

    def calc(stat):
        used = (stat["dataSize"] + stat["indexSize"]) / (1024 * 1024)
        free = 512 - used
        return f"{used:.2f}", f"{free:.2f}"

    used1, free1 = calc(s1)
    used2, free2 = calc(s2)
    used3, free3 = calc(s3)
    used4, free4 = calc(s4)
    used5, free5 = calc(s5)

    text = script.STATUS_TXT.format(
        total_files,
        users,
        chats,

        tot1, used1, free1,
        tot2, used2, free2,
        tot3, used3, free3,
        tot4, used4, free4,
        tot5, used5, free5
    )

    await msg.edit(text)
