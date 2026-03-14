from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from database.users_chats_db import db
from pyrogram import Client, filters
import asyncio
import datetime
import time
import logging
from info import ADMINS

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def send_msg(bot, user_id, msg):
    try:
        await msg.copy(user_id)
        return "success"

    except FloodWait as e:
        await asyncio.sleep(e.value)
        await msg.copy(user_id)
        return "success"

    except UserIsBlocked:
        return "blocked"

    except InputUserDeactivated:
        return "deleted"

    except PeerIdInvalid:
        return "deleted"

    except Exception:
        return "failed"


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcast(bot, message):

    users = await db.get_all_users()
    b_msg = message.reply_to_message

    sts = await message.reply_text("🚀 **Starting Broadcast...**")

    start_time = time.time()

    total_users = await db.total_users_count()

    success = 0
    blocked = 0
    deleted = 0
    failed = 0
    done = 0

    tasks = []

    async for user in users:
        if "id" not in user:
            continue

        user_id = int(user["id"])

        tasks.append(send_msg(bot, user_id, b_msg))

        if len(tasks) == 50:  # batch sending (FAST)
            results = await asyncio.gather(*tasks)
            tasks = []

            for r in results:
                done += 1

                if r == "success":
                    success += 1
                elif r == "blocked":
                    blocked += 1
                elif r == "deleted":
                    deleted += 1
                else:
                    failed += 1

            await sts.edit(
                f"📡 **Broadcast Running**\n\n"
                f"👥 Total Users: `{total_users}`\n"
                f"✅ Success: `{success}`\n"
                f"🚫 Blocked: `{blocked}`\n"
                f"🗑 Deleted: `{deleted}`\n"
                f"⚠ Failed: `{failed}`\n"
                f"📤 Completed: `{done}/{total_users}`"
            )

    if tasks:
        results = await asyncio.gather(*tasks)

        for r in results:
            done += 1

            if r == "success":
                success += 1
            elif r == "blocked":
                blocked += 1
            elif r == "deleted":
                deleted += 1
            else:
                failed += 1

    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))

    await sts.edit(
        f"✅ **Broadcast Completed**\n\n"
        f"⏱ Time Taken: `{time_taken}`\n\n"
        f"👥 Total Users: `{total_users}`\n"
        f"✅ Success: `{success}`\n"
        f"🚫 Blocked: `{blocked}`\n"
        f"🗑 Deleted: `{deleted}`\n"
        f"⚠ Failed: `{failed}`"
    )
