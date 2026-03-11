import asyncio
import logging
import re
import time
import datetime
import pytz
from os import environ
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from database.ia_filterdb import (
    Media,
    Media2,
    Media3,
    Media4,
    Media5,
    unpack_new_file_id,
    get_readable_time
)

from info import ADMINS, id_pattern
from utils import temp

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

lock = asyncio.Lock()

MEDIA_COLLECTIONS = [
    Media.collection,
    Media2.collection,
    Media3.collection,
    Media4.collection,
    Media5.collection
]

media_filter = filters.document | filters.video | filters.audio

DELETE_CHANNELS = [
    int(x) if id_pattern.search(x) else x
    for x in environ.get(
        "DELETE_CHANNELS",
        "-1002354592029"
    ).split()
]

def get_time():
    tz = pytz.timezone("Asia/Kolkata")
    return datetime.datetime.now(tz).strftime("%I:%M:%S %p - %d %b, %Y")


async def delete_from_db(file_id: str):
    for col in MEDIA_COLLECTIONS:
        result = await col.find_one({"_id": file_id})
        if result:
            await col.delete_one({"_id": file_id})
            return True
    return False


def get_media(message):
    for m in ("document", "video", "audio"):
        media = getattr(message, m, None)
        if media:
            return media
    return None

@Client.on_message(filters.chat(DELETE_CHANNELS) & media_filter)
async def delete_multiple_media(bot, message):

    media = get_media(message)
    if not media:
        return

    try:

        file_id, _ = unpack_new_file_id(media.file_id)

        deleted = await delete_from_db(file_id)

        if deleted:
            logger.info(f"🗑 File deleted → {file_id}")
        else:
            logger.info("⚠ File not found in DB")

    except Exception as e:
        logger.exception(f"Delete error: {e}")

@Client.on_message(filters.command("del_channel") & filters.user(ADMINS))
async def delete_channel_media(bot, message):

    if not message.reply_to_message:
        return

    regex = re.compile(
        r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[A-Za-z0-9_]+)/(\d+)"
    )

    match = regex.search(message.text)

    if not match:
        return await message.reply("❌ Invalid Telegram link")

    chat = match.group(4)
    lst_msg_id = int(match.group(5))

    if chat.isnumeric():
        chat = int("-100" + chat)

    status = await message.reply("⏳ Processing index cleanup...")

    total_deleted = 0
    not_found = 0
    no_media = 0

    start_time = time.time()

    fst_msg_id = temp.CURRENT
    current = temp.CURRENT

    temp.CANCEL = False

    async with lock:

        try:

            async for msg in bot.iter_messages(chat, lst_msg_id, temp.CURRENT):

                if temp.CANCEL:
                    await status.edit(
                        f"❌ **Process Cancelled**\n\n"
                        f"🕒 Updated : `{get_time()}`\n"
                        f"📥 Fetched : `{current}`\n"
                        f"🗑 Deleted : `{total_deleted}`\n"
                        f"⚠ Not Found : `{not_found}`\n"
                        f"📂 No Media : `{no_media}`"
                    )
                    break

                current += 1

                if current % 1000 == 0:

                    elapsed = time.time() - start_time
                    remaining = (lst_msg_id - current) * elapsed / (
                        current - fst_msg_id + 1
                    )

                    remaining_str = get_readable_time(remaining)
                    elapsed_str = get_readable_time(elapsed)

                    keyboard = InlineKeyboardMarkup(
                        [[InlineKeyboardButton("❌ Cancel", callback_data="index_cancel")]]
                    )

                    await status.edit_text(
                        f"⏳ **Index Cleaning Running**\n\n"
                        f"🕒 Updated : `{get_time()}`\n"
                        f"⌛ Time Taken : `{elapsed_str}`\n"
                        f"🧮 Remaining : `{lst_msg_id-current}`\n"
                        f"⏱ ETC : `{remaining_str}`\n\n"
                        f"📥 Fetched : `{current}`\n"
                        f"🗑 Deleted : `{total_deleted}`\n"
                        f"⚠ Not Found : `{not_found}`\n"
                        f"📂 No Media : `{no_media}`",
                        reply_markup=keyboard
                    )

                if msg.empty or not msg.media:
                    no_media += 1
                    continue

                if msg.media not in (
                        enums.MessageMediaType.VIDEO,
                        enums.MessageMediaType.DOCUMENT
                ):
                    no_media += 1
                    continue

                media = getattr(msg, msg.media.value, None)

                if not media:
                    no_media += 1
                    continue

                if media.mime_type not in [
                    "video/mp4",
                    "video/x-matroska"
                ]:
                    no_media += 1
                    continue

                file_id, _ = unpack_new_file_id(media.file_id)

                deleted = await delete_from_db(file_id)

                if deleted:
                    total_deleted += 1
                else:
                    not_found += 1

        except FloodWait as e:
            await asyncio.sleep(e.value)

        except Exception as e:

            logger.exception(e)

            return await bot.send_message(
                message.chat.id,
                f"🚫 **Error Occurred**\n\n"
                f"`{e}`\n\n"
                f"🕒 Updated : `{get_time()}`\n"
                f"📥 Fetched : `{current}`\n"
                f"🗑 Deleted : `{total_deleted}`\n"
                f"⚠ Not Found : `{not_found}`\n"
                f"📂 No Media : `{no_media}`"
            )

    elapsed = get_readable_time(time.time() - start_time)

    await bot.send_message(
        message.chat.id,
        f"✅ **Index Cleanup Completed**\n\n"
        f"🕒 Updated : `{get_time()}`\n"
        f"⌛ Total Time : `{elapsed}`\n\n"
        f"📥 Fetched : `{current}`\n"
        f"🗑 Deleted : `{total_deleted}`\n"
        f"⚠ Not Found : `{not_found}`\n"
        f"📂 No Media : `{no_media}`"
    )

@Client.on_callback_query(filters.regex("index_cancel"))
async def cancel_index(_, query):

    temp.CANCEL = True

    await query.answer("❌ Cancelling process...", show_alert=True)
