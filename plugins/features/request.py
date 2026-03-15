from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import RPCError
from info import LOG_CHANNEL

@Client.on_message(filters.command("request") & filters.private)
async def request_movie(client: Client, message: Message):

    if len(message.command) < 2:
        return await message.reply_text("**Please Provide A Description After The Command.**")

    movie_name = " ".join(message.command[1:])

    user = message.from_user
    user_name = user.first_name if user else "Unknown"
    user_id = user.id if user else 0

    text = f"""
#Request
👤 **User:** [{user_name}](tg://user?id={user_id})
🆔 **User ID:** `{user_id}`

📌 **Requested Movie:** `{movie_name}` """

    try:
        await client.send_message(LOG_CHANNEL, text, disable_web_page_preview=True)
        await message.reply_text(
            "**📝 Your Request Has Been Sent. Thank You... ❤️**"
        )

    except RPCError:
        await message.reply_text(
            "❌ **Failed to send request.**\nPlease try again later."
        )
