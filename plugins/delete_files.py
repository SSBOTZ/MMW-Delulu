import re
import os
import pytz
import time
import asyncio
import datetime
from os import environ
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.ia_filterdb import Media, Media2, Media3, Media4, Media5, unpack_new_file_id, get_readable_time
from info import id_pattern, ADMINS
from utils import temp

lock = asyncio.Lock()

media_filter = filters.document | filters.video

DELETE_CHANNELS = [int(dch) if id_pattern.search(dch) else dch for dch in environ.get('DELETE_CHANNELS', '-1002354592029').split()]

MEDIA_COLLECTIONS = [
    Media.collection,
    Media2.collection,
    Media3.collection,
    Media4.collection,
    Media5.collection
]

async def delete_file(file_id):
    for collection in MEDIA_COLLECTIONS:
        result = await collection.find_one({'_id': file_id})
        if result:
            await collection.delete_one({'_id': file_id})
            return True
    return False


@Client.on_message(filters.chat(DELETE_CHANNELS) & media_filter)
async def deletemultiplemedia(bot, message):
    for file_type in ("document", "video"):
        media = getattr(message, file_type, None)
        if media:
            break
    else:
        return

    file_id, _ = unpack_new_file_id(media.file_id)
    await delete_file(file_id)


@Client.on_message(filters.command("del_channel") & filters.user(ADMINS))
async def deletechannelmedia(bot, message):

    if not message.reply_to_message:
        return

    if message.reply_to_message.text:
        regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(message.text)
        if not match:
            return await message.reply("❌ Invalid link")

        chat = match.group(4)
        lst_msg_id = int(match.group(5))

        if chat.isnumeric():
            chat = int("-100" + chat)

    elif message.reply_to_message.forward_from_chat.type == enums.ChatType.CHANNEL:
        lst_msg_id = message.reply_to_message.forward_from_message_id
        chat = message.reply_to_message.forward_from_chat.username or message.reply_to_message.forward_from_chat.id

    else:
        return

    msg = await message.reply("⚡ Processing channel messages...")

    total_files = 0
    not_found = 0
    no_media = 0

    fst_msg_id = temp.CURRENT
    start_time = time.time()
    remaining_time_str = "N/A"
    elapsed_time_str = "0s"
    remaining_index = 0

    async with lock:
        try:
            current = temp.CURRENT
            tz = pytz.timezone('Asia/Kolkata')
            temp.CANCEL = False

            async for message in bot.iter_messages(chat, lst_msg_id, temp.CURRENT):

                if temp.CANCEL:
                    now = datetime.datetime.now(tz)
                    ttime = now.strftime("%I:%M:%S %p - %d %b, %Y")

                    await msg.edit(
                        f"🛑 **Process Cancelled**\n\n"
                        f"🕒 Last Update: `{ttime}`\n\n"
                        f"📥 Fetched: `{current}`\n"
                        f"🗑 Deleted: `{total_files}`\n"
                        f"❓ Not Found: `{not_found}`\n"
                        f"🚫 Non Media: `{no_media}`"
                    )
                    break

                current += 1

                now = datetime.datetime.now(tz)
                ttime = now.strftime("%I:%M:%S %p - %d %b, %Y")

                if current % 1000 == 0:

                    elapsed_time = time.time() - start_time
                    remaining_time = (lst_msg_id - current - 1) * elapsed_time / (current - fst_msg_id + 1)

                    remaining_time_str = get_readable_time(remaining_time)
                    elapsed_time_str = get_readable_time(elapsed_time)
                    remaining_index = lst_msg_id - current

                    can = [[InlineKeyboardButton("🛑 Cancel", callback_data="index_cancel")]]
                    reply = InlineKeyboardMarkup(can)

                    await msg.edit_text(
                        text=
                        f"⏳ **Deleting Files...**\n\n"
                        f"⏱ ETC: `{remaining_time_str}`\n"
                        f"📉 Remaining: `{remaining_index}`\n"
                        f"🕒 Updated: `{ttime}`\n"
                        f"⌛ Time Taken: `{elapsed_time_str}`\n\n"
                        f"📥 Fetched: `{current}`\n"
                        f"🗑 Deleted: `{total_files}`\n"
                        f"❓ Not Found: `{not_found}`\n"
                        f"🚫 Non Media: `{no_media}`",
                        reply_markup=reply
                    )

                if message.empty:
                    no_media += 1
                    continue

                if not message.media:
                    no_media += 1
                    continue

                if message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.DOCUMENT]:
                    no_media += 1
                    continue

                media = getattr(message, message.media.value, None)

                if not media:
                    no_media += 1
                    continue

                if media.mime_type not in ['video/x-matroska']:
                    no_media += 1
                    continue

                file_id, _ = unpack_new_file_id(media.file_id)

                deleted = await delete_file(file_id)

                if deleted:
                    total_files += 1
                else:
                    not_found += 1

        except Exception as e:

            await bot.send_message(
                msg.chat.id,
                f"🚫 **Error Occurred**\n\n"
                f"`{e}`\n\n"
                f"⏳ ETC: `{remaining_time_str}`\n"
                f"📉 Remaining: `{remaining_index}`\n\n"
                f"📥 Fetched: `{current}`\n"
                f"🗑 Deleted: `{total_files}`\n"
                f"❓ Not Found: `{not_found}`\n"
                f"🚫 Non Media: `{no_media}`"
            )

        else:

            now = datetime.datetime.now(tz)
            ttime = now.strftime("%I:%M:%S %p - %d %b, %Y")

            await bot.send_message(
                msg.chat.id,
                f"✅ **Deletion Completed Successfully**\n\n"
                f"⏱ ETC: `{remaining_time_str}`\n"
                f"📉 Remaining: `{remaining_index}`\n"
                f"🕒 Updated: `{ttime}`\n"
                f"⌛ Time Taken: `{elapsed_time_str}`\n\n"
                f"📥 Fetched: `{current}`\n"
                f"🗑 Deleted: `{total_files}`\n"
                f"❓ Not Found: `{not_found}`\n"
                f"🚫 Non Media: `{no_media}`"
            )
