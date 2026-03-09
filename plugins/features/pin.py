from pyrogram import Client, filters, enums
from pyrogram.types import Message

async def admin_check(message: Message) -> bool:
    if not message.from_user:
        return False

    if message.chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return False

    if message.from_user.id in [777000, 1087968824]:
        return True

    client = message._client
    chat_id = message.chat.id
    user_id = message.from_user.id

    check_status = await client.get_chat_member(chat_id=chat_id, user_id=user_id)

    if check_status.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
        return False
    return True


async def admin_filter_f(filt, client, message):
    return await admin_check(message)


admin_filter = filters.create(func=admin_filter_f, name="AdminFilter")


@Client.on_message(filters.command("pin") & admin_filter)
async def pin(_, message: Message):
    if not message.reply_to_message:
        await message.reply_text("⚠️ 𝑹𝒆𝒑𝒍𝒚 𝒕𝒐 𝒂 𝒎𝒆𝒔𝒔𝒂𝒈𝒆 𝒕𝒐 𝒑𝒊𝒏 𝒊𝒕.")
        return

    await message.reply_to_message.pin()
    await message.reply_text("📌 **𝑴𝒆𝒔𝒔𝒂𝒈𝒆 𝑷𝒊𝒏𝒏𝒆𝒅 𝑺𝒖𝒄𝒄𝒆𝒔𝒔𝒇𝒖𝒍𝒍𝒚!**")


@Client.on_message(filters.command("unpin") & admin_filter)
async def unpin(_, message: Message):
    if not message.reply_to_message:
        await message.reply_text("⚠️ 𝑹𝒆𝒑𝒍𝒚 𝒕𝒐 𝒂 𝒎𝒆𝒔𝒔𝒂𝒈𝒆 𝒕𝒐 𝒖𝒏𝒑𝒊𝒏 𝒊𝒕.")
        return

    await message.reply_to_message.unpin()
    await message.reply_text("📍 **𝑴𝒆𝒔𝒔𝒂𝒈𝒆 𝑼𝒏𝒑𝒊𝒏𝒏𝒆𝒅!**")


@Client.on_message(filters.command("unpin_all") & filters.group)
async def unpinall_handler(client, message: Message):
    try:
        user = await client.get_chat_member(message.chat.id, message.from_user.id)

        if user.status not in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
            raise PermissionError("❌ 𝒀𝒐𝒖 𝒂𝒓𝒆 𝒏𝒐𝒕 𝒂𝒏 𝒂𝒅𝒎𝒊𝒏.")

        await client.unpin_all_chat_messages(message.chat.id)
        await message.reply_text("🧹 **𝑨𝒍𝒍 𝑷𝒊𝒏𝒏𝒆𝒅 𝑴𝒆𝒔𝒔𝒂𝒈𝒆𝒔 𝑯𝒂𝒗𝒆 𝑩𝒆𝒆𝒏 𝑪𝒍𝒆𝒂𝒓𝒆𝒅!**")

    except Exception as e:
        await message.reply_text(f"⚠️ **𝑬𝒓𝒓𝒐𝒓:** `{e}`")
