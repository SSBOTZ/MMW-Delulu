import os
import sys
import re
import time
import shutil
import asyncio
import logging
import logging.config
import psutil
from pyrogram import Client, filters, enums
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery
)
from pyrogram.errors import ChatAdminRequired, PeerIdInvalid
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
from info import *
from Script import script
from utils import *
from database.users_chats_db import db

logger = logging.getLogger(__name__)
        
@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    r_j_check = [u.id for u in message.new_chat_members]
    if temp.ME in r_j_check:
        if not await db.get_chat(message.chat.id):
            r_j = message.from_user.mention if message.from_user else "Anonymous" 
            await bot.send_message(
                LOG_CHANNEL, 
                script.LOG_TEXT_G.format(
                    message.chat.title, message.chat.id, total, r_j
                )
            )       
            await db.add_chat(message.chat.id, message.chat.title)
        if message.chat.id in temp.BANNED_CHATS:
            buttons = [[
                InlineKeyboardButton('💬 Support', url=f'https://t.me/{SUPPORT_CHAT}')
            ]]
            reply_markup=InlineKeyboardMarkup(buttons)
            k = await message.reply(
                text='🚫 <b>CHAT NOT ALLOWED</b> 🐞\n\nMy admins have restricted me from working here! Contact support to know more.',
                reply_markup=reply_markup,
            )
            try:
                await k.pin()
            except:
                pass
            await bot.leave_chat(message.chat.id)
            return
        buttons = [
               InlineKeyboardButton('➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘs ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ]
        reply_markup=InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=f"🌟 <b>𝐓𝐡𝐚𝐧𝐤𝐲𝐨𝐮 𝐅𝐨𝐫 𝐀𝐝𝐝𝐢𝐧𝐠 𝐌𝐞 𝐢𝐧 {message.chat.title} ❣️</b>\n\nIf you have any questions or doubts about using me, contact support.",
            reply_markup=reply_markup
        )
    else:
        settings = await get_settings(message.chat.id)
        if settings["welcome"]:
            for u in message.new_chat_members:
                if (temp.MELCOW).get('welcome') is not None:
                    try:
                        await (temp.MELCOW['welcome']).delete()
                    except:
                        pass
                temp.MELCOW['welcome'] = await message.reply(
                    f"✨ <b>𝐇𝐞𝐲 {u.mention}, 𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨 {message.chat.title}!</b> 🌈"
                )


@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('❗ Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        chat = chat
    try:
        buttons = [[
            InlineKeyboardButton('💬 Support', url=f'https://t.me/{SUPPORT_CHAT}')
        ]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat,
            text='👋 <b>Hello Friends!</b>\nMy admin has told me to leave this group. Contact support to add me again.',
            reply_markup=reply_markup,
        )
        await bot.leave_chat(chat)
        await message.reply(f"✅ Left the chat `{chat}`")
    except Exception as e:
        await message.reply(f'❌ Error - {e}')

@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('❗ Give me a chat id')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat_ = int(chat)
    except:
        return await message.reply('❌ Give Me A Valid Chat ID')
    cha_t = await db.get_chat(int(chat_))
    if not cha_t:
        return await message.reply("❌ Chat Not Found In DB")
    if cha_t['is_disabled']:
        return await message.reply(f"⚠️ This chat is already disabled:\nReason-<code> {cha_t['reason']} </code>")
    await db.disable_chat(int(chat_), reason)
    temp.BANNED_CHATS.append(int(chat_))
    await message.reply('✅ Chat Successfully Disabled')
    try:
        buttons = [[
            InlineKeyboardButton('💬 Support', url=f'https://t.me/{SUPPORT_CHAT}')
        ]]
        reply_markup=InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat_, 
            text=f'👋 <b>Hello Friends!</b>\nMy admin has told me to leave this group.\nReason: <code>{reason}</code>',
            reply_markup=reply_markup
        )
        await bot.leave_chat(chat_)
    except Exception as e:
        await message.reply(f"❌ Error - {e}")

    
@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def re_enable_chat(bot, message):
    if len(message.command) == 1:
        return await message.reply('❗ Give me a chat id')
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except:
        return await message.reply('❌ Give Me A Valid Chat ID')
    sts = await db.get_chat(int(chat))
    if not sts:
        return await message.reply("❌ Chat Not Found In DB !")
    if not sts.get('is_disabled'):
        return await message.reply('⚠️ This chat is not yet disabled.')
    await db.re_enable_chat(int(chat_))
    temp.BANNED_CHATS.remove(int(chat_))
    await message.reply("✅ Chat Successfully Re-enabled")

        
@Client.on_message(filters.command('invite') & filters.user(ADMINS))
async def gen_invite(bot, message):
    if len(message.command) == 1:
        return await message.reply('❗ Give me a chat id')
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        return await message.reply('❌ Give Me A Valid Chat ID')
    try:
        link = await bot.create_chat_invite_link(chat)
    except ChatAdminRequired:
        return await message.reply("❌ Invite Link Generation Failed, I do not have sufficient rights")
    except Exception as e:
        return await message.reply(f'❌ Error {e}')
    await message.reply(f'🔗 Here is your Invite Link: {link.invite_link}')

@Client.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('❗ Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("❌ Invalid user, make sure I have met them before.")
    except IndexError:
        return await message.reply("❌ This might be a channel, make sure it’s a user.")
    except Exception as e:
        return await message.reply(f'❌ Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if jar['is_banned']:
            return await message.reply(f"⚠️ {k.mention} is already banned\nReason: {jar['ban_reason']}")
        await db.ban_user(k.id, reason)
        temp.BANNED_USERS.append(k.id)
        await message.reply(f"✅ Successfully banned {k.mention}")


@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    if len(message.command) == 1:
        return await message.reply('❗ Give me a user id / username')
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = "No reason Provided"
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply("❌ Invalid user, make sure I have met them before.")
    except IndexError:
        return await message.reply("❌ This might be a channel, make sure it’s a user.")
    except Exception as e:
        return await message.reply(f'❌ Error - {e}')
    else:
        jar = await db.get_ban_status(k.id)
        if not jar['is_banned']:
            return await message.reply(f"⚠️ {k.mention} is not yet banned.")
        await db.remove_ban(k.id)
        temp.BANNED_USERS.remove(k.id)
        await message.reply(f"✅ Successfully unbanned {k.mention}")


@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users(bot, message):
    raju = await message.reply('🔍 Getting List Of Users...')
    users = await db.get_all_users()
    out = "📋 <b>Users Saved In DB:</b>\n\n"
    for user in users:
        out += f"<a href=tg://user?id={user['id']}>{user['name']}</a>"
        if user['ban_status']['is_banned']:
            out += ' ⚠️(Banned User)'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('users.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('users.txt', caption="📄 List Of Users")

@Client.on_message(filters.command('chats') & filters.user(ADMINS))
async def list_chats(bot, message):
    raju = await message.reply('🔍 Getting List Of Chats...')
    chats = await db.get_all_chats()
    out = "📋 <b>Chats Saved In DB:</b>\n\n"
    for chat in chats:
        out += f"**Title:** `{chat['title']}`\n**- ID:** `{chat['id']}`"
        if chat['chat_status']['is_disabled']:
            out += ' ⚠️(Disabled Chat)'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('chats.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('chats.txt', caption="📄 List Of Chats")
