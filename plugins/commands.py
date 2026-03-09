import os
import sys
import re
import time
import json
import base64
import shutil
import random
import asyncio
import logging
import datetime
from os import environ, execle, system
from typing import List, Tuple
import psutil
import pytz
import pymongo
from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery
)
from pyrogram.errors import ChatAdminRequired, PeerIdInvalid, FloodWait
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
from database.ia_filterdb import*
from database.connections_mdb import active_connection
from plugins.fsub import ForceSub

media_filter = filters.document | filters.video

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):    
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
               InlineKeyboardButton('➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘs ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup)
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘs ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
            InlineKeyboardButton('👥 ᴄᴏᴍᴍᴜɴɪᴛʏ 👥', callback_data='commun'),
            InlineKeyboardButton('🤖 ʙᴏᴛ ɪɴғᴏ 🤖', callback_data='about')
            ],[
            InlineKeyboardButton('🎁 ʜᴇʟᴘ 🎁', callback_data='help'),            
            InlineKeyboardButton('🪬 ᴀʙᴏᴜᴛ 🪬', callback_data='botinfo')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)      
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
   
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help", "start", "hehe"]:
        if message.command[1] == "subscribe":
            await ForceSub(client, message)
            return        
        buttons = [[
            InlineKeyboardButton('➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘs ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
            InlineKeyboardButton('👥 ᴄᴏᴍᴍᴜɴɪᴛʏ 👥', callback_data='commun'),
            InlineKeyboardButton('🤖 ʙᴏᴛ ɪɴғᴏ 🤖', callback_data='about')
            ],[
            InlineKeyboardButton('🎁 ʜᴇʟᴘ 🎁', callback_data='help'),            
            InlineKeyboardButton('🪬 ᴀʙᴏᴜᴛ 🪬', callback_data='botinfo')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)      
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    kk, file_id = message.command[1].split("_", 1) if "_" in message.command[1] else (False, False)
    pre = ('checksubp' if kk == 'filep' else 'checksub') if kk else False

    status = await ForceSub(client, message, file_id=file_id, mode=pre)
    if not status:
        return

    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""
    files_ = await get_file_details(file_id)           
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        try:
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True if pre == 'filep' else False,
                )
            filetype = msg.media
            file = getattr(msg, filetype.value)
            title = file.file_name
            size=get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption, mention=message.from_user.mention)
                except:
                    return
            await msg.edit_caption(f_caption)
            return
        except:
            pass
        return await message.reply('No such file exist.')
    files = files_[0]
    title = files.file_name
    size=get_size(files.file_size)
    f_caption=files.file_name
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption, mention=message.from_user.mention)
        except Exception as e:
            logger.exception(e)
            f_caption=f_caption
    if f_caption is None:
        f_caption = f"{files.file_name}"
    ok = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=True if pre == 'filep' else False,
        reply_markup=InlineKeyboardMarkup([InlineKeyboardButton('𝗠𝗼𝘃𝗶𝗲 𝗚𝗿𝗼𝘂𝗽', url=GRP_LNK)])) 
    
@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Pʀᴏᴄᴇssɪɴɢ...⏳", quote=True)
    else:
        await message.reply('Rᴇᴘʟʏ ᴛᴏ ғɪʟᴇ ᴡɪᴛʜ /delete ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ', quote=True)
        return

    for file_type in ("document", "video"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('Tʜɪs ɪs ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ ғɪʟᴇ ғᴏʀᴍᴀᴛ')
        return

    file_id, file_ref = unpack_new_file_id(media.file_id)

    for db in [Media, Media2, Media3, Media4, Media5]:
        if await db.count_documents({'file_id': file_id}):
            result = await db.collection.delete_one({'_id': file_id})
            if result.deleted_count:
                await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
                return
        else:
            file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
            result = await db.collection.delete_many({
                'file_name': file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
                return

    await msg.edit('Fɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ')

@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'This will delete all indexed files.\nDo you want to continue??',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="YES", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="CANCEL", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(client, callback_query):
    for collection in [Media.collection, Media2.collection, Media3.collection]:
        await collection.drop()
    
    await callback_query.answer("Piracy Is Crime", show_alert=True)
    await callback_query.message.edit_text("Successfully deleted all indexed files.")
    
@Client.on_message(filters.command('settings'))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return

    settings = await get_settings(grp_id)

    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton(
                    'Filter Button',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Single' if settings["button"] else 'Double',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Bot PM',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["botpm"] else '❌ No',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'File Secure',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["file_secure"] else '❌ No',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'IMDB',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["imdb"] else '❌ No',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Spell Check',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["spell_check"] else '❌ No',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Welcome',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["welcome"] else '❌ No',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply_text(
            text=f"<b>Change Your Settings for {title} As Your Wish ⚙</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=message.id
        )



@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    sts = await message.reply("Checking template")
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"You are anonymous admin. Use /connect {message.chat.id} in PM")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return

    if len(message.command) < 2:
        return await sts.edit("No Input!!")
    template = message.text.split(" ", 1)[1]
    await save_group_settings(grp_id, 'template', template)
    await sts.edit(f"Successfully changed template for {title} to\n\n{template}")

@Client.on_message(filters.command('restart') & filters.user(ADMINS))
async def restart_bot(client, message):
    msg = await message.reply_text(
        text="<b>Bot Restarting ...</b>"
    )        
    await msg.edit("<b>Restart Successfully Completed ✅</b>")
    system("git pull -f && pip3 install --no-cache-dir -r requirements.txt")
    execle(sys.executable, sys.executable, "bot.py", environ)
    
@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def deletemultiplefiles(bot, message):
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏɴ'ᴛ ᴡᴏʀᴋ ɪɴ ɢʀᴏᴜᴘs. Iᴛ ᴏɴʟʏ ᴡᴏʀᴋs ᴏɴ ᴍʏ PM!</b>")
    else:
        pass
    try:
        keyword = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, Gɪᴠᴇ ᴍᴇ ᴀ ᴋᴇʏᴡᴏʀᴅ ᴀʟᴏɴɢ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ғɪʟᴇs.</b>")
    btn = [[
       InlineKeyboardButton("Yᴇs, Cᴏɴᴛɪɴᴜᴇ !", callback_data=f"killfilesdq#{keyword}")
       ],[
       InlineKeyboardButton("Nᴏ, Aʙᴏʀᴛ ᴏᴘᴇʀᴀᴛɪᴏɴ !", callback_data="close_data")
    ]]
    await message.reply_text(
        text="<b>Aʀᴇ ʏᴏᴜ sᴜʀᴇ? Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ?\n\nNᴏᴛᴇ:- Tʜɪs ᴄᴏᴜʟᴅ ʙᴇ ᴀ ᴅᴇsᴛʀᴜᴄᴛɪᴠᴇ ᴀᴄᴛɪᴏɴ!</b>",
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("deletesmallfiles") & filters.user(ADMINS))
async def process_command(client, message):
    chat_id = message.chat.id
    processing_message = await message.reply_text("<b>Processing: Deleting files...</b>")
    
    total_files_deleted = 0
    batch_size = 250

    while True:
        deleted_files = await delete_files_below_threshold(db, threshold_size_mb=40, batch_size=batch_size)
        
        if deleted_files == 0:
            break

        total_files_deleted += deleted_files

        # Update the message to show progress
        progress_message = f'<b>Processing: Deleted {total_files_deleted} files in {total_files_deleted // batch_size} batches.</b>'
        await processing_message.edit_text(progress_message)
        await asyncio.sleep(3)

    print(f'Total files deleted: {total_files_deleted}')
    await processing_message.edit_text(f'<b>Deletion complete: Deleted {total_files_deleted} files.</b>')

@Client.on_message(filters.command("delete_duplicate") & filters.user(ADMINS))
async def delete_duplicate_files(client, message):
    ok = await message.reply("⏳ Processing duplicates...")
    deleted_count = 0
    batch_count = 0

    async def remove_duplicates(collection, unique_files):
        nonlocal deleted_count, batch_count
        async for doc in collection.find():
            file_size = doc["file_size"]
            file_id = doc["file_id"]
            if file_size in unique_files and unique_files[file_size] != file_id:
                result = await collection.find_one({"_id": file_id})
                if result:
                    await collection.delete_one({"_id": file_id})
                    deleted_count += 1
                    if deleted_count % 100 == 0:
                        batch_count += 1
                        await ok.edit(f"🗑 Deleted {deleted_count} files in {batch_count} batches.")
    
    # Collections
    collections = [Media, Media2, Media3, Media4, Media5]

    # Gather all files
    all_files = []
    for col in collections:
        files = await col.find({}, {"file_id": 1, "file_size": 1}).to_list(length=None)
        all_files += files

    # Keep unique files
    unique_files = {}
    for f in all_files:
        if f["file_size"] not in unique_files:
            unique_files[f["file_size"]] = f["file_id"]

    # Remove duplicates
    for col in collections:
        await remove_duplicates(col, unique_files)

    await message.reply(f"✅ Deleted {deleted_count} duplicate files in {batch_count} batches.")

@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def get_stats(bot, message):

    if message.from_user.id not in ADMINS:
        k = await message.reply_text("<b>🚫 ᴏɴʟʏ ᴀᴅᴍɪɴꜱ ᴄᴀɴ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.</b>")
        await asyncio.sleep(10)
        await k.delete()
        await message.delete()
        return

    msg = await message.reply("<b>♻️ 𝚂𝚃𝙰𝚃𝚄𝚂 𝙳𝙴𝚃𝙰𝙸𝙻𝚂... </b>")

    users = await db.total_users_count()
    chats = await db.total_chat_count()

    tot1 = await Media.count_documents()
    tot2 = await Media2.count_documents()
    tot3 = await Media3.count_documents()
    tot4 = await Media4.count_documents()
    tot5 = await Media5.count_documents()

    total_files = tot1 + tot2 + tot3 + tot4 + tot5

    s1 = await clientDB.command("dbStats")
    s2 = await clientDB2.command("dbStats")
    s3 = await clientDB3.command("dbStats")
    s4 = await clientDB4.command("dbStats")
    s5 = await clientDB5.command("dbStats")

    def calc(stat):
        used = (stat["dataSize"] + stat["indexSize"]) / (1024 * 1024)
        storage = stat["storageSize"] / (1024 * 1024)
        free = max(storage - used, 0)   # prevents negative values
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
