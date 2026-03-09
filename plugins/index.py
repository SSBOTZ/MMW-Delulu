import time as timer
import os, pytz, re, asyncio, math
from datetime import datetime
from pyrogram import Client, filters, enums
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import *
from database.ia_filterdb import *
from utils import temp
import pymongo

lock = asyncio.Lock()

inclient = pymongo.MongoClient(DATABASE_URI)
indb = inclient[DATABASE_NAME]
incol = indb['index']

ALL_MEDIA = [Media, Media2, Media3, Media4, Media5]


@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Cᴀɴᴄᴇʟʟɪɴɢ Iɴᴅᴇxɪɴɢ", show_alert=True)

    perfx, chat, lst_msg_id = query.data.split("#")

    if lock.locked():
        return await query.answer('Wᴀɪᴛ Uɴᴛɪʟ Pʀᴇᴠɪᴏᴜs Pʀᴏᴄᴇss Cᴏᴍᴘʟᴇᴛᴇ', show_alert=True)

    msg = query.message

    button = InlineKeyboardMarkup([
        [InlineKeyboardButton('🚫 ᴄᴀɴᴄᴇʟʟ ', "index_cancel")]
    ])

    await msg.edit("ɪɴᴅᴇxɪɴɢ ɪs sᴛᴀʀᴛᴇᴅ ✨", reply_markup=button)

    try:
        chat = int(chat)
    except:
        chat = chat

    await index_files_to_db(int(lst_msg_id), chat, msg, bot)


@Client.on_message(
    (filters.forwarded | (filters.regex("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")) & filters.text)
    & filters.private
    & filters.incoming
    & filters.user(ADMINS.copy() + [5130458445])
)
async def send_for_index(bot, message):

    if message.text:
        regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(message.text)

        if not match:
            return await message.reply('Invalid link')

        chat_id = match.group(4)
        last_msg_id = int(match.group(5))

        if chat_id.isnumeric():
            chat_id = int("-100" + chat_id)

    elif message.forward_from_chat.type == enums.ChatType.CHANNEL:
        last_msg_id = message.forward_from_message_id
        chat_id = message.forward_from_chat.username or message.forward_from_chat.id
    else:
        return

    try:
        await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await message.reply('This may be a private channel / group. Make me an admin over there to index the files.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link specified.')
    except Exception as e:
        return await message.reply(f'Errors - {e}')

    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except:
        return await message.reply('Make Sure That Iam An Admin In The Channel, if channel is private')

    if k.empty:
        return await message.reply('This may be group and iam not a admin of the group.')

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton('✨ ʏᴇꜱ', callback_data=f'index#{chat_id}#{last_msg_id}')],
        [InlineKeyboardButton('🚫 ᴄʟᴏꜱᴇ', callback_data='close_data')]
    ])

    await message.reply(
        f'Do You Want To Index This Channel/ Group ?\n\nChat ID/ Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>',
        reply_markup=buttons
    )


@Client.on_message(filters.command('setskip') & filters.user(ADMINS.copy() + [5130458445]))
async def set_skip_number(bot, message):

    if len(message.command) == 2:

        try:
            skip = int(message.text.split(" ", 1)[1])
        except:
            return await message.reply(
                "❌ **ɪɴᴠᴀʟɪᴅ ɪɴᴘᴜᴛ!**\n"
                "📌 ᴛʜᴇ ꜱᴋɪᴘ ɴᴜᴍʙᴇʀ ꜱʜᴏᴜʟᴅ ʙᴇ ᴀɴ **ɪɴᴛᴇɢᴇʀ**.\n\n"
            )

        temp.CURRENT = int(skip)

        await message.reply(
            f"✅ **ꜱᴜᴄᴄᴇꜱꜱ!**\n"
            f"⏭️ ꜱᴋɪᴘ ɴᴜᴍʙᴇʀ ꜱᴇᴛ ᴛᴏ **{skip}**\n\n"
        )

    else:
        await message.reply(
            "⚠️ **ɴᴏ ɴᴜᴍʙᴇʀ ɢɪᴠᴇɴ!**\n"
            "📌 ᴜꜱᴀɢᴇ: `/setskip 5`\n\n"
        )



async def index_files_to_db(lst_msg_id, chat, msg, bot):

    total_files = 0
    duplicate = 0
    no_media = 0
    errors = 0

    fst_msg_id = temp.CURRENT
    start_time = timer.time()

    remaining_time_str = "N/A"
    remaining_index = 0
    elapsed_time_str = "0s"

    current = temp.CURRENT

    tz = pytz.timezone('Asia/Kolkata')
    ttime = datetime.now(tz).strftime("%I:%M:%S %p - %d %b, %Y")

    async with lock:

        try:

            temp.CANCEL = False

            async for message in bot.iter_messages(chat, lst_msg_id, temp.CURRENT):

                if temp.CANCEL:

                    elapsed_time = timer.time() - start_time
                    elapsed_time_str = get_readable_time(elapsed_time)

                    remaining_index = lst_msg_id - current

                    await msg.edit(
                        f"<b>❌ 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗖𝗮𝗻𝗰𝗲𝗹𝗹𝗲𝗱!!</b>\n\n"
                        f"<b>├ ▸ Last Updated: <i>{ttime}</i></b>\n\n"
                        f"<b>╭ ▸ Fetched:</b> <code>{current}</code>\n"
                        f"<b>├ ▸ Saved:</b> <code>{total_files}</code>\n"
                        f"<b>├ ▸ Duplicate:</b> <code>{duplicate}</code>\n"
                        f"<b>╰ ▸ Non:</b> <code>{no_media}</code>\n"
                        f"<b>╰ ▸ Remaining:</b> <code>{remaining_index}</code>\n"
                    )

                    break

                current += 1

                now = datetime.now(tz)
                ttime = now.strftime("%I:%M:%S %p - %d %b, %Y")

                if current % 60 == 0:

                    can = [[InlineKeyboardButton('𝗖𝗮𝗻𝗰𝗲𝗹', callback_data='index_cancel')]]
                    reply = InlineKeyboardMarkup(can)

                    await asyncio.sleep(1)

                    elapsed_time = timer.time() - start_time

                    if current - fst_msg_id > 0:
                        remaining_time = (lst_msg_id - current - 1) * elapsed_time / (current - fst_msg_id + 1)
                        remaining_time_str = get_readable_time(remaining_time)

                    elapsed_time_str = get_readable_time(elapsed_time)

                    remaining_index = lst_msg_id - current

                    incol.update_one(
                        {"_id": "index_progress"},
                        {"$set": {"last_indexed_file": current, "last_msg_id": lst_msg_id, "chat_id": chat}},
                        upsert=True
                    )

                    await msg.edit_text(
                        text=f"<b>╭ ▸ ETC: </b>{remaining_time_str} ❙ <b>Remaining:</b> <code>{remaining_index}</code>\n"
                             f"<b>├ ▸ Last Updated: <i>{ttime}</i></b>\n"
                             f"<b>╰ ▸ Time Taken: </b>{elapsed_time_str}\n\n"
                             f"<b>╭ ▸ Fetched:</b> <code>{current}</code>\n"
                             f"<b>├ ▸ Saved:</b> <code>{total_files}</code>\n"
                             f"<b>├ ▸ Duplicate:</b> <code>{duplicate}</code>\n"
                             f"<b>╰ ▸ Non:</b> <code>{no_media}</code>\n",
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

                media.file_type = message.media.value
                media.caption = message.caption

                check = await check_file(media)

                if check:
                    saved = await save_file(media)

                    if saved:
                        total_files += 1
                    else:
                        errors += 1
                else:
                    duplicate += 1

        except Exception as e:

            elapsed_time = timer.time() - start_time
            elapsed_time_str = get_readable_time(elapsed_time)

            remaining_index = lst_msg_id - current

            return await bot.send_message(
                msg.chat.id,
                f'<b>🚫 𝗘𝗿𝗿𝗼𝗿:</b> {e}\n\n'
                f'<b>╭ ▸ ETC: </b>{remaining_time_str} ❙ <b>Remaining:</b> <code>{remaining_index}</code>\n'
                f'<b>├ ▸ Last Updated: <i>{ttime}</i></b>\n\n'
                f'<b>╭ ▸ Fetched:</b> <code>{current}</code>\n'
                f'<b>├ ▸ Saved:</b> <code>{total_files}</code>\n'
                f'<b>├ ▸ Duplicate:</b> <code>{duplicate}</code>\n'
                f'<b>╰ ▸ Non:</b> <code>{no_media}</code>\n'
            )

        else:

            elapsed_time = timer.time() - start_time
            elapsed_time_str = get_readable_time(elapsed_time)

            remaining_index = 0
            remaining_time_str = "0s"

            await bot.send_message(
                msg.chat.id,
                f'<b>✅ 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗖𝗼𝗺𝗽𝗹𝗲𝘁𝗲𝗱!!</b>\n\n'
                f'<b>╭ ▸ ETC: </b>{remaining_time_str} ❙ <b>Remaining:</b> <code>{remaining_index}</code>\n'
                f'<b>├ ▸ Last Updated: <i>{ttime}</i></b>\n'
                f'<b>╰ ▸ Time Taken: </b>{elapsed_time_str}\n\n'
                f'<b>╭ ▸ Fetched:</b> <code>{current}</code>\n'
                f'<b>├ ▸ Saved:</b> <code>{total_files}</code>\n'
                f'<b>├ ▸ Duplicate:</b> <code>{duplicate}</code>\n'
                f'<b>╰ ▸ Non:</b> <code>{no_media}</code>\n'
            )

            incol.delete_one({"_id": "index_progress"})
