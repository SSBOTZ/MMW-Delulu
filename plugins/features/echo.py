from pyrogram import Client, filters, enums
from pyrogram.types import *

@Client.on_message(filters.command("echo") & filters.group)
async def echo(client, message):
    try:
        user = await client.get_chat_member(message.chat.id, message.from_user.id)
        if user.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
            await message.reply_text("🚫 𝖠𝖼𝖼𝖾𝗌𝗌 𝖣𝖾𝗇𝗂𝖾𝖽!\n\n👮‍♂️ 𝖮𝗇𝗅𝗒 𝖦𝗋𝗈𝗎𝗉 𝖠𝖽𝗆𝗂𝗇𝗌 𝖼𝖺𝗇 𝗎𝗌𝖾 𝗍𝗁𝗂𝗌 𝖼𝗈𝗆𝗆𝖺𝗇𝖽.")
            return
    except Exception as error:
        await message.reply_text(f"⚠️ 𝖤𝗋𝗋𝗈𝗋 𝖮𝖼𝖼𝗎𝗋𝗋𝖾𝖽!\n\n🤖 𝖨 𝗆𝖺𝗒 𝗇𝗈𝗍 𝗁𝖺𝗏𝖾 𝗉𝖾𝗋𝗆𝗂𝗌𝗌𝗂𝗈𝗇𝗌.\n\n📄 {error}")
        return

    reply = message.reply_to_message

    if not reply:
        await message.reply_text("💬 𝖯𝗅𝖾𝖺𝗌𝖾 𝗋𝖾𝗉𝗅𝗒 𝗍𝗈 𝖺 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗍𝗈 𝖾𝖼𝗁𝗈 𝗂𝗍.")
        return

    await reply.reply_text(f"📢 𝖤𝖼𝗁𝗈:\n\n{message.text.split(None, 1)[1]}")
    await message.delete()


@Client.on_message(filters.command("echo") & filters.private)
async def echoptp(client, message):
    await message.reply_text("🚫 𝖲𝗈𝗋𝗋𝗒!\n\n👥 𝖳𝗁𝗂𝗌 𝖼𝗈𝗆𝗆𝖺𝗇𝖽 𝗈𝗇𝗅𝗒 𝗐𝗈𝗋𝗄𝗌 𝗂𝗇 𝗀𝗋𝗈𝗎𝗉𝗌.")
