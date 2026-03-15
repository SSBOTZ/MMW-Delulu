from pyrogram import Client, filters
from pyrogram.types import Message
from info import LOG_CHANNEL


@Client.on_message(filters.command(["bug", "bugs", "feedback"]))
async def bug_handler(client: Client, message: Message):
    try:
        user = message.from_user
        chat = message.chat

        bug_report = None

        if len(message.command) > 1:
            bug_report = message.text.split(" ", 1)[1].strip()

        elif message.reply_to_message and message.reply_to_message.text:
            bug_report = message.reply_to_message.text.strip()

        if not bug_report:
            return await message.reply_text(
                "⚠️ **Bug Report Required**\n\n"
                "Reply to a message **or** send a description.\n\n"
                "`Example:` `/bug Bot is not responding`",
                quote=True
            )

        await message.reply_text(
            f"✅ **Bug Report Sent Successfully!**\n\n"
            f"👤 **User:** {user.mention}\n"
            f"📩 Your report has been forwarded to the **developer**.\n\n"
            f"Thank you for helping improve the bot!",
            quote=True
        )

        log_text = (
            f"🐞 **New Bug Report**\n\n"
            f"👤 **User:** {user.mention}\n"
            f"🆔 **User ID:** `{user.id}`\n"
            f"💬 **Chat:** `{chat.title if chat.type != 'private' else 'Private Chat'}`\n"
            f"🆔 **Chat ID:** `{chat.id}`\n\n"
            f"📄 **Bug Description:**\n"
            f"```{bug_report}```"
        )

        await client.send_message(LOG_CHANNEL, log_text)

    except Exception as e:
        await message.reply_text(
            "❌ **Error Occurred**\n\n"
            "Something went wrong while processing your report.\n"
            "Please try again later.",
            quote=True
        )

        error_text = (
            f"⚠️ **Bug Handler Error**\n\n"
            f"👤 **User:** {message.from_user.mention}\n"
            f"🆔 **User ID:** `{message.from_user.id}`\n"
            f"💬 **Chat ID:** `{message.chat.id}`\n\n"
            f"🛑 **Error:**\n"
            f"```{str(e)}```"
        )

        await client.send_message(LOG_CHANNEL, error_text)
