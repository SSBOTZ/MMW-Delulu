import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

@Client.on_message(filters.command(["catbox", "telegraph"], prefixes="/") & filters.reply)
async def catbox_upload(client, message: Message):
    reply = message.reply_to_message

    if not reply.media:
        return await message.reply_text("❌ 𝑹𝒆𝒑𝒍𝒚 𝒕𝒐 𝒂 𝒎𝒆𝒅𝒊𝒂 𝒇𝒊𝒍𝒆 𝒕𝒐 𝒖𝒑𝒍𝒐𝒂𝒅.")

    msg = await message.reply_text("⏳ 𝑼𝒑𝒍𝒐𝒂𝒅𝒊𝒏𝒈 𝒕𝒐 𝑪𝒂𝒕𝒃𝒐𝒙...")

    try:
        file_path = await reply.download()

        with open(file_path, "rb") as f:
            r = requests.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "fileupload"},
                files={"fileToUpload": f}
            )

        if r.status_code == 200:
            await msg.edit_text(
                f"✅ **𝑼𝒑𝒍𝒐𝒂𝒅 𝑺𝒖𝒄𝒄𝒆𝒔𝒔!**\n\n🔗 `{r.text}`"
            )
        else:
            await msg.edit_text("❌ 𝑼𝒑𝒍𝒐𝒂𝒅 𝑭𝒂𝒊𝒍𝒆𝒅.")

        os.remove(file_path)

    except Exception as e:
        await msg.edit_text(f"⚠️ 𝑬𝒓𝒓𝒐𝒓\n`{e}`")
