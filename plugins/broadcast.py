from pyrogram import Client, filters
from pyrogram.errors import InputUserDeactivated, FloodWait, UserIsBlocked
import datetime
import time
from database.users_chats_db import db
from info import ADMINS
import asyncio

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast(bot, message):
    if len(message.command) == 1:
        delulu = 0
    else:
        try:
            delulu = int(message.text.split(None, 1)[1])
        except:
            await message.reply("❌ Invalid number")
            return

    start_time = time.time()
    b_msg = message.reply_to_message
    sts = await message.reply("🚀 Broadcasting started...")

    users = await db.get_all_users()
    users_list = await users.to_list(None)
    total_users = len(users_list)

    users = await db.get_all_users()

    skipped_count = 0
    success = 0
    failed = 0
    batch = []

    async for user in users:
        if skipped_count < delulu:
            skipped_count += 1
            continue

        batch.append(int(user["id"]))

        if len(batch) == 20:
            tasks = [b_msg.copy(chat_id=u) for u in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for i, result in enumerate(results):
                if isinstance(result, FloodWait):
                    await asyncio.sleep(result.x)
                    try:
                        await b_msg.copy(chat_id=batch[i])
                        success += 1
                    except:
                        failed += 1
                elif isinstance(result, (InputUserDeactivated, UserIsBlocked)):
                    await db.delete_user(batch[i])
                    failed += 1
                elif isinstance(result, Exception):
                    failed += 1
                else:
                    success += 1

            batch = []

        process = success + failed

        if process % 500 == 1:
            elapsed = datetime.timedelta(seconds=int(time.time() - start_time))
            await sts.edit(
                f"📢 Broadcast Running\n\n"
                f"👥 Total: {total_users}\n"
                f"⏩ Progress: {process+matrix}\n"
                f"✅ Success: {success}\n"
                f"❌ Failed: {failed}\n"
                f"⏳ Time: {elapsed}"
            )

    if batch:
        tasks = [b_msg.copy(chat_id=u) for u in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, (InputUserDeactivated, UserIsBlocked)):
                await db.delete_user(batch[i])
                failed += 1
            elif isinstance(result, Exception):
                failed += 1
            else:
                success += 1

    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))

    await sts.edit(
        f"✅ Broadcast Completed\n\n"
        f"👥 Total Users: {total_users}\n"
        f"⏭ Skipped: {skipped_count}\n"
        f"✅ Success: {success}\n"
        f"❌ Failed: {failed}\n"
        f"⏱ Time Taken: {time_taken}"
    )
