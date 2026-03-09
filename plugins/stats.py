import asyncio
from pyrogram import Client, filters
from database.users_chats_db import db
import script
from info import ADMINS
from database.ia_filterdb import (
    save_file,
    Media, Media2, Media3, Media4, Media5,
    db as clientDB,
    db2 as clientDB2,
    db3 as clientDB3,
    db4 as clientDB4,
    db5 as clientDB5
)

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
