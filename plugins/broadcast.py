from pyrogram import Client, filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
import asyncio
import datetime
import time
from database.users_chats_db import db
from info import ADMINS

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast_handler(bot, message):

    start_time = time.time()

    if len(message.command) == 1:
        delulu = 0
    else:
        try:
            delulu = int(message.text.split(None, 1)[1])
        except ValueError:
            await message.reply("❌ Invalid matrix value.")
            return

    broadcast_msg = message.reply_to_message

    status_msg = await message.reply(
        "🚀 Broadcast Started..."
    )

    users_cursor = await db.get_all_users()
    users_list = await users_cursor.to_list(length=None)
    total_users = len(users_list)

    success = 0
    failed = 0
    skipped = 0

    users_cursor = await db.get_all_users()

    async for user in users_cursor:

        user_id = int(user["id"])

        if skipped < delulu:
            skipped += 1
            continue

        try:

            sent_msg = await broadcast_msg.copy(
                chat_id=user_id
            )

            try:
                await sent_msg.pin(disable_notification=True)
            except Exception:
                pass

            success += 1

        except FloodWait as e:

            await asyncio.sleep(e.value)

            try:
                sent_msg = await broadcast_msg.copy(chat_id=user_id)
                success += 1
            except Exception:
                failed += 1

        except (InputUserDeactivated, UserIsBlocked, PeerIdInvalid):

            await db.delete_user(user_id)
            failed += 1

        except Exception:

            failed += 1

        processed = success + failed

        if processed % 300 == 0:

            elapsed = datetime.timedelta(seconds=int(time.time() - start_time))

            await status_msg.edit(
                f"🚀 Broadcast Running...\n\n"
                f"👥 Total Users: {total_users}\n"
                f"📤 Sent: {success}\n"
                f"❌ Failed: {failed}\n"
                f"⏭ Skipped: {skipped}\n"
                f"📊 Progress: {processed + matrix}/{total_users}\n"
                f"⏱ Elapsed Time: {elapsed}"
            )

    total_time = datetime.timedelta(seconds=int(time.time() - start_time))

    await status_msg.edit(
        f"✅ Broadcast Completed\n\n"
        f"👥 Total Users: {total_users}\n"
        f"📤 Successfully Sent: {success}\n"
        f"❌ Failed: {failed}\n"
        f"⏭ Skipped: {skipped}\n"
        f"⏱ Time Taken: {total_time}"
    )
