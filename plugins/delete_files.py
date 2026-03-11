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


@Client.on_message(filters.command("del_channel") & filters.user(ADMINS))
async def deletechannelmedia(bot, message):

    if not message.reply_to_message:
        return await message.reply("Reply to a channel link or forwarded message.")

    reply = message.reply_to_message

    if reply.text:
        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?([\w\d_]+)/(\d+)")
        match = regex.search(reply.text)

        if not match:
            return await message.reply("❌ Invalid link")

        chat = match.group(4)
        lst_msg_id = int(match.group(5))

        if chat.isnumeric():
            chat = int("-100" + chat)

    elif reply.forward_from_chat and reply.forward_from_chat.type == enums.ChatType.CHANNEL:
        chat = reply.forward_from_chat.username or reply.forward_from_chat.id
        lst_msg_id = reply.forward_from_message_id

    else:
        return await message.reply("❌ Provide channel post link or forward message.")

    status = await message.reply("⚡ Starting deletion process...")

    total_files = 0
    not_found = 0
    no_media = 0
    processed = 0

    start_time = time.time()

    async with lock:
        try:
            async for msg in bot.iter_messages(chat, limit=lst_msg_id):

                processed += 1

                if not msg.media:
                    no_media += 1
                    continue

                if msg.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.DOCUMENT]:
                    no_media += 1
                    continue

                media = getattr(msg, msg.media.value, None)

                if not media:
                    no_media += 1
                    continue

                file_id, _ = unpack_new_file_id(media.file_id)

                deleted = await delete_file(file_id)

                if deleted:
                    total_files += 1
                else:
                    not_found += 1

                if processed % 60 == 0:
                    elapsed = get_readable_time(time.time() - start_time)

                    await status.edit(
                        f"⏳ **Deleting Files...**\n\n"
                        f"📥 Checked: `{processed}`\n"
                        f"🗑 Deleted: `{total_files}`\n"
                        f"❓ Not Found: `{not_found}`\n"
                        f"🚫 Non Media: `{no_media}`\n"
                        f"⌛ Time: `{elapsed}`"
                    )

        except Exception as e:
            return await status.edit(f"❌ Error:\n`{e}`")

    elapsed = get_readable_time(time.time() - start_time)

    await status.edit(
        f"✅ **Deletion Completed**\n\n"
        f"📥 Checked: `{processed}`\n"
        f"🗑 Deleted: `{total_files}`\n"
        f"❓ Not Found: `{not_found}`\n"
        f"🚫 Non Media: `{no_media}`\n"
        f"⌛ Time: `{elapsed}`"
    )
