import datetime
import time
import asyncio
import logging
from pyrogram import Client, filters
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [BROADCAST] - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def user_broadcast(bot, message):
    logger.info("User broadcast initiated")

    users = await db.get_all_users()
    b_msg = message.reply_to_message

    sts = await message.reply_text(
        "🚀 **𝑩𝒓𝒐𝒂𝒅𝒄𝒂𝒔𝒕 𝑺𝒕𝒂𝒓𝒕𝒆𝒅**\n"
    )

    start_time = time.time()
    total_users = await db.total_users_count()

    done = 0
    success = 0
    blocked = 0
    deleted = 0
    failed = 0

    logger.info(f"Total users: {total_users}")

    batch_size = 40

    for i in range(0, len(users), batch_size):
        batch = users[i:i + batch_size]

        tasks = []
        for user in batch:
            user_id = int(user["id"])
            tasks.append(broadcast_messages(user_id, b_msg))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for user, result in zip(batch, results):
            user_id = int(user["id"])

            try:
                if isinstance(result, Exception):
                    failed += 1
                    logger.error(f"Failed for {user_id}")
                else:
                    pti, sh = result

                    if pti:
                        success += 1
                        logger.info(f"Sent to {user_id}")
                    else:
                        if sh == "Blocked":
                            blocked += 1
                            logger.warning(f"Blocked by {user_id}")
                        elif sh == "Deleted":
                            deleted += 1
                            logger.warning(f"Deleted account {user_id}")
                        else:
                            failed += 1
                            logger.error(f"Failed for {user_id}")

            except Exception as e:
                failed += 1
                logger.exception(f"Error sending to {user_id}: {e}")

            done += 1

        if done % 20 == 0:
            await sts.edit(
                "📊 **𝑩𝒓𝒐𝒂𝒅𝒄𝒂𝒔𝒕 𝑷𝒓𝒐𝒈𝒓𝒆𝒔𝒔**\n"
                f"👥 𝑻𝒐𝒕𝒂𝒍: {total_users}\n"
                f"✅ 𝑺𝒆𝒏𝒕: {success}\n"
                f"🚫 𝑩𝒍𝒐𝒄𝒌𝒆𝒅: {blocked}\n"
                f"❌ 𝑫𝒆𝒍𝒆𝒕𝒆𝒅: {deleted}\n"
                f"⚠️ 𝑭𝒂𝒊𝒍𝒆𝒅: {failed}\n"
                f"🔄 𝑷𝒓𝒐𝒄𝒆𝒔𝒔𝒆𝒅: {done}/{total_users}\n"
                "━━━━━━━━━━━━━━━\n"
            )

        await asyncio.sleep(1)

    time_taken = datetime.timedelta(seconds=int(time.time() - start_time))

    
    await sts.edit(
        "🎉 **𝑩𝒓𝒐𝒂𝒅𝒄𝒂𝒔𝒕 𝑪𝒐𝒎𝒑𝒍𝒆𝒕𝒆𝒅**\n"
        f"⏱️ 𝑻𝒊𝒎𝒆: {time_taken}\n\n"
        f"👥 𝑻𝒐𝒕𝒂𝒍: {total_users}\n"
        f"✅ 𝑺𝒖𝒄𝒄𝒆𝒔𝒔: {success}\n"
        f"🚫 𝑩𝒍𝒐𝒄𝒌𝒆𝒅: {blocked}\n"
        f"❌ 𝑫𝒆𝒍𝒆𝒕𝒆𝒅: {deleted}\n"
        f"⚠️ 𝑭𝒂𝒊𝒍𝒆𝒅: {failed}\n"
    )
