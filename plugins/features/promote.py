from pyrogram import Client, filters
from pyrogram.types import ChatPrivileges

@Client.on_message(filters.command("promote") & filters.group)
async def promote_user(client, message):

    if not message.reply_to_message:
        return await message.reply("⚠️ 𝗥𝗲𝗽𝗹𝘆 𝘁𝗼 𝗮 𝘂𝘀𝗲𝗿 𝘁𝗼 𝗽𝗿𝗼𝗺𝗼𝘁𝗲")

    reply = message.reply_to_message
    chat_id = message.chat.id
    new_admin = reply.from_user
    admin = message.from_user

    user_stats = await client.get_chat_member(chat_id, admin.id)
    bot_stats = await client.get_chat_member(chat_id, "self")

    if not bot_stats.privileges:
        return await message.reply("🤖 𝗜 𝗮𝗺 𝗻𝗼𝘁 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻")

    if not user_stats.privileges:
        return await message.reply("🚫 𝗬𝗼𝘂 𝗺𝘂𝘀𝘁 𝗯𝗲 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻")

    if not bot_stats.privileges.can_promote_members:
        return await message.reply("❌ 𝗜 𝗱𝗼𝗻’𝘁 𝗵𝗮𝘃𝗲 𝗽𝗿𝗼𝗺𝗼𝘁𝗲 𝗽𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻")

    if not user_stats.privileges.can_promote_members:
        return await message.reply("⚠️ 𝗬𝗼𝘂 𝗻𝗲𝗲𝗱 𝗽𝗿𝗼𝗺𝗼𝘁𝗲 𝗿𝗶𝗴𝗵𝘁𝘀")

    msg = await message.reply("⏳ **𝗣𝗿𝗼𝗺𝗼𝘁𝗶𝗻𝗴 𝗨𝘀𝗲𝗿...**")

    await client.promote_chat_member(
        chat_id,
        new_admin.id,
        privileges=ChatPrivileges(
            can_change_info=True,
            can_delete_messages=True,
            can_pin_messages=True,
            can_invite_users=True,
            can_manage_video_chats=True,
            can_restrict_members=True
        )
    )

    await msg.edit("✅ **𝗨𝘀𝗲𝗿 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗣𝗿𝗼𝗺𝗼𝘁𝗲𝗱** 🎉")


@Client.on_message(filters.command("demote") & filters.group)
async def demote_user(client, message):

    if not message.reply_to_message:
        return await message.reply("⚠️ 𝗥𝗲𝗽𝗹𝘆 𝘁𝗼 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻 𝘁𝗼 𝗱𝗲𝗺𝗼𝘁𝗲")

    reply = message.reply_to_message
    chat_id = message.chat.id
    new_admin = reply.from_user
    admin = message.from_user

    user_stats = await client.get_chat_member(chat_id, admin.id)
    bot_stats = await client.get_chat_member(chat_id, "self")

    if not bot_stats.privileges:
        return await message.reply("🤖 𝗜 𝗮𝗺 𝗻𝗼𝘁 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻")

    if not user_stats.privileges:
        return await message.reply("🚫 𝗬𝗼𝘂 𝗺𝘂𝘀𝘁 𝗯𝗲 𝗮𝗻 𝗮𝗱𝗺𝗶𝗻")

    if not bot_stats.privileges.can_promote_members:
        return await message.reply("❌ 𝗜 𝗱𝗼𝗻’𝘁 𝗵𝗮𝘃𝗲 𝗱𝗲𝗺𝗼𝘁𝗲 𝗽𝗲𝗿𝗺𝗶𝘀𝘀𝗶𝗼𝗻")

    if not user_stats.privileges.can_promote_members:
        return await message.reply("⚠️ 𝗬𝗼𝘂 𝗻𝗲𝗲𝗱 𝗱𝗲𝗺𝗼𝘁𝗲 𝗿𝗶𝗴𝗵𝘁𝘀")

    msg = await message.reply("⏳ **𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴...**")

    await client.promote_chat_member(
        chat_id,
        new_admin.id,
        privileges=ChatPrivileges(
            can_change_info=False,
            can_invite_users=False,
            can_delete_messages=False,
            can_restrict_members=False,
            can_pin_messages=False,
            can_promote_members=False,
            can_manage_chat=False,
            can_manage_video_chats=False
        )
    )

    await msg.edit("🥺 **𝗨𝘀𝗲𝗿 𝗗𝗲𝗺𝗼𝘁𝗲𝗱**")
