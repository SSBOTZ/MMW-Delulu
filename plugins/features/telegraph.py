import os
import base64
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

IMGBB_API_KEY = "105fdbfcf44b0e13a53a6d238418012f"

def upload_to_imgbb(file_path):
    url = "https://api.imgbb.com/1/upload"

    with open(file_path, "rb") as f:
        img = base64.b64encode(f.read()).decode()

    payload = {
        "key": IMGBB_API_KEY,
        "image": img
    }

    r = requests.post(url, data=payload, timeout=30)
    r.raise_for_status()
    data = r.json()

    if data.get("success"):
        d = data["data"]
        return {
            "url": d["url"],
            "display_url": d["display_url"],
            "delete_url": d.get("delete_url")
        }

    return None


@Client.on_message(filters.command(["catbox", "telegraph"]) & filters.reply)
async def upload_handler(client, message: Message):

    reply = message.reply_to_message

    if not reply.media:
        return await message.reply_text(
            "❌ **𝑹𝒆𝒑𝒍𝒚 𝒕𝒐 𝒂 𝒎𝒆𝒅𝒊𝒂 𝒇𝒊𝒍𝒆 𝒕𝒐 𝒖𝒑𝒍𝒐𝒂𝒅.**"
        )

    cmd = message.command[0].lower()

    if cmd == "catbox":
        msg = await message.reply_text("⏳ **𝑼𝒑𝒍𝒐𝒂𝒅𝒊𝒏𝒈 𝒕𝒐 𝑪𝒂𝒕𝒃𝒐𝒙...**")
    else:
        msg = await message.reply_text("⏳ **𝑼𝒑𝒍𝒐𝒂𝒅𝒊𝒏𝒈 𝒕𝒐 𝑰𝒎𝒈𝑩𝑩...**")

    try:
        file_path = await reply.download()

        if cmd == "catbox":
            with open(file_path, "rb") as f:
                r = requests.post(
                    "https://catbox.moe/user/api.php",
                    data={"reqtype": "fileupload"},
                    files={"fileToUpload": f}
                )

            if r.status_code == 200:
                text = (
                    "✅ **𝑼𝒑𝒍𝒐𝒂𝒅 𝑺𝒖𝒄𝒄𝒆𝒔𝒔!**\n\n"
                    f"🔗 **𝑳𝒊𝒏𝒌 :** `{r.text}`"
                )
            else:
                text = "❌ **𝑼𝒑𝒍𝒐𝒂𝒅 𝑭𝒂𝒊𝒍𝒆𝒅.**"

            await msg.edit_text(text)

        elif cmd == "telegraph":

            result = upload_to_imgbb(file_path)

            if not result:
                return await msg.edit_text(
                    "❌ **𝑼𝒑𝒍𝒐𝒂𝒅 𝑭𝒂𝒊𝒍𝒆𝒅. 𝑻𝒓𝒚 𝑨𝒈𝒂𝒊𝒏.**"
                )

            reply_text = (
                "✅ **𝑼𝒑𝒍𝒐𝒂𝒅𝒆𝒅 𝑺𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚!**\n\n"
                f"🔗 **𝑫𝒊𝒓𝒆𝒄𝒕 𝑳𝒊𝒏𝒌 :** `{result['url']}`\n"
                f"🖼️ **𝑫𝒊𝒔𝒑𝒍𝒂𝒚 𝑳𝒊𝒏𝒌 :** `{result['display_url']}`\n"
            )

            if result.get("delete_url"):
                reply_text += f"🗑️ **𝑫𝒆𝒍𝒆𝒕𝒆 𝑳𝒊𝒏𝒌 :** `{result['delete_url']}`"

            await msg.edit_text(reply_text)

        os.remove(file_path)

    except Exception as e:
        await msg.edit_text(
            f"⚠️ **𝑬𝒓𝒓𝒐𝒓 𝑶𝒄𝒄𝒖𝒓𝒓𝒆𝒅**\n`{e}`"
        )

@Client.on_message(filters.command('ilink'))
async def img_2_link(bot, message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply('Reply to photo')
    path = await message.reply_to_message.download()
    with open(path, 'rb') as f:
        r = requests.post("https://uguu.se/upload", files={'files[]': f})
    os.remove(path)
    if r.status_code == 200:
        url = r.json()['files'][0]['url']
        await message.reply(f"Link: {url}")

@Client.on_message(filters.command('img_2_link'))
async def imglink(bot, message):
    # ❗ Check if user replied to a photo
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply(
            "⚠️ **Oops!**\n"
            "👉 Please reply to an image to convert it into a link 🖼️🔗"
        )

    # ⬇️ Download the image
    path = await message.reply_to_message.download()

    # ⬆️ Upload to Uguu
    with open(path, 'rb') as f:
        r = requests.post("https://uguu.se/upload", files={'files[]': f})

    # 🧹 Remove local file
    os.remove(path)

    # ✅ Handle response
    if r.status_code == 200:
        url = r.json()['files'][0]['url']
        await message.reply(
            "✨ **Upload Successful!** ✨\n\n"
            f"🔗 **Your Image Link:**\n`{url}`\n\n"
            "🚀 Share it anywhere you like!"
        )
    else:
        await message.reply(
            "❌ **Upload Failed!**\n"
            "😓 Please try again later."
        )
