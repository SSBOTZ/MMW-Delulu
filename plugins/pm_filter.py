import asyncio
lock = asyncio.Lock()
import re
import ast
import random
import math
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from info import *
from pyrogram.types import *
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, send_all, imdb
from database.users_chats_db import db
from database.ia_filterdb import Media, Media2, Media3, Media4, Media5, get_file_details, get_search_results, get_bad_files, db as clientDB, db2 as clientDB2, db3 as clientDB3, db4 as clientDB4, db5 as clientDB5from database.filters_mdb import find_gfilter, get_gfilters
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}
SEASON = {}

# Choose Option Settings 
LANGUAGES = ["malayalam", "mal", "tamil", "tam" ,"english", "eng", "hindi", "hin", "telugu", "tel", "kannada", "kan"]
SEASONS = ["season 1", "season 2", "season 3", "season 4", "season 5", "season 6", "season 7", "season 8", "season 9", "season 10"]
EPISODES = ["E 01", "E 02", "E 03", "E 04", "E 05", "E 06", "E 07", "E 08", "E 09", "E 10", "E 11", "E 12", "E 13", "E 14", "E 15", "E 16", "E 17", "E 18", "E 19", "E 20", "E 21", "E 22", "E 23", "E 24", "E 25", "E 26", "E 27", "E 28", "E 29", "E 30", "E 31", "E 32", "E 33", "E 34", "E 35", "E 36", "E 37", "E 38", "E 39", "E 40"]
QUALITIES = ["360p", "480p", "720p", "1080p", "1440p", "2160p"]
YEARS = ["1900", "1991", "1992", "1993", "1994", "1995", "1996", "1997", "1998", "1999", "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]

NON_IMG = """<b>‼️ FILE NOT FOUND ? ‼️

1️⃣ സിനിമയുടെ സ്പെല്ലിങ്ങ് ഗൂഗിളിൽ ഉള്ളത് പോലെ ആണോ നിങ്ങൾ അടിച്ചത് എന്ന് ഉറപ്പ് വരുത്തുക..!!

2️⃣ നിങ്ങൾ ചോദിച്ച സിനിമ OTT റിലീസ് ആയതാണോ എന്ന് <a href=https://t.me/mallumovieworldmain2> MMW BOTZ 𝐔𝐏𝐃𝐀𝐓𝐄𝐒 </a> യിൽ ചെക്ക് ചെയ്യുക..!!

3️⃣ മൂവിക്ക് വേണ്ടി മെസ്സേജ് അയക്കുമ്പോൾ മൂവിയുടെ പേര് ഇറങ്ങിയ വർഷം മാത്രം അയക്കുക..!!</b>"""


CAPTIONS = [
    lambda u, s: f"<b>👋🏻 𝐇𝐞𝐲 {u}\n📂 𝐘𝐨𝐮𝐫 {s} 𝐟𝐢𝐥𝐞𝐬 𝐚𝐫𝐞 𝐫𝐞𝐚𝐝𝐲 ✅</b>",
    lambda u, s: f"<b>✨ ʜᴇʏ {u}\n📁 ʏᴏᴜʀ {s} ꜰɪʟᴇꜱ ᴀʀᴇ ʀᴇᴀᴅʏ 🚀</b>",
    lambda u, s: f"<b>👑 𝓗𝓮𝔂 {u}\n📫 𝓨𝓸𝓾𝓻 {s} 𝓯𝓲𝓵𝓮𝓼 𝓪𝓻𝓮 𝓻𝓮𝓪𝓭𝔂 ✨</b>",
    lambda u, s: f"<b>⚡ ʜᴇʏ 👋 {u}\n📦 ʏᴏᴜʀ {s} ꜰɪʟᴇꜱ ᴀʀᴇ ʀᴇᴀᴅʏ 🔥</b>",
    lambda u, s: f"<b>🌈 Ｈｅｙ {u}\n📥 Ｙｏｕｒ {s} Ｆｉｌｅｓ ａｒｅ Ｒｅａｄｙ ✅</b>",
    lambda u, s: f"<b>🔥 𝙃𝙚𝙮 {u}\n📫 𝙔𝙤𝙪𝙧 {s} 𝙛𝙞𝙡𝙚𝙨 𝙖𝙧𝙚 𝙧𝙚𝙖𝙙𝙮 ✅</b>",
    lambda u, s: f"<b>🌸 Ｈｅｙ {u}\n📫 Ｙｏᴜʀ {s} Ｆｉｌᴇs Ａʀᴇ Ｒᴇａᴅｙ ✅</b>",
    lambda u, s: f"<b>💫 𝓗𝓮𝔂 {u}\n📦 𝓨𝓸𝓾𝓻 {s} 𝓯𝓲𝓵𝓮𝓼 𝓪𝓻𝓮 𝓻𝓮𝓪𝓭𝔂 💎</b>",
    lambda u, s: f"<b>🖤 ʜᴇʏ 👋 {u}\n📂 ʏᴏᴜʀ {s} ꜰɪʟᴇꜱ ᴀʀᴇ ʀᴇᴀᴅʏ 🎉</b>",
    lambda u, s: f"<b>🎬 ʜᴇʏ 👋 {u}\n📂 ʏᴏᴜʀ {s} ꜰɪʟᴇꜱ ᴀʀᴇ ᴡᴀɪᴛɪɴɢ ✨</b>"
]

async def auto_delete(original_msg: Message, reply_msg: Message):
    try:
        await asyncio.sleep(600)
        await original_msg.delete()
        await reply_msg.delete()
    except:
        pass

async def spell_check(original_msg: Message, reply_msg: Message):
    try:
        await asyncio.sleep(10)
        await original_msg.delete()
        await reply_msg.delete()
    except:
        pass

@Client.on_message((filters.group | filters.private) & filters.text & filters.incoming)
async def give_filter(client, message):
    await auto_filter(client, message)
    
@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("😁 𝗛𝗲𝘆 𝗙𝗿𝗶𝗲𝗻𝗱, 𝗣𝗹𝗲𝗮𝘀𝗲 𝗦𝗲𝗮𝗿𝗰𝗵 𝗬𝗼𝘂𝗿𝘀𝗲𝗹𝗳.", show_alert=True)

    try:
        offset = int(offset)
    except:
        offset = 0

    search = BUTTONS.get(key)
    if not search:
        return await query.answer("𝐋𝐢𝐧𝐤 𝐄𝐱𝐩𝐢𝐫𝐞𝐝. 𝗣𝗹𝗲𝗮𝘀𝗲 𝗦𝗲𝗮𝗿𝗰𝗵 𝗔𝗴𝗮𝗶𝗻 🙂.", show_alert=True)

    files, n_offset, total = await get_search_results(search.lower(), offset=offset, filter=True)
    settings = await get_settings(query.message.chat.id)

    if settings['button']:
        btn = [
            [InlineKeyboardButton(f"[{get_size(file.file_size)}] ⊳ {file.file_name}", callback_data=f'files#{file.file_id}')]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(f"{file.file_name}", callback_data=f'files#{file.file_id}'),
                InlineKeyboardButton(f"{get_size(file.file_size)}", callback_data=f'files_#{file.file_id}')
            ]
            for file in files
        ]

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10

    page_num = math.ceil(int(offset) / 10) + 1
    total_pages = math.ceil(total / 10)

    if n_offset == 0:
        if off_set is not None:
            btn.append([
                InlineKeyboardButton("↲ Bᴀᴄ𝗄", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton("➥ 𝗣𝗮𝗴𝗲", callback_data="pages"),
                InlineKeyboardButton(f"{page_num}/{total_pages}", callback_data="pages")
            ])
        else:
            btn.append([InlineKeyboardButton(f"{page_num}/{total_pages}", callback_data="pages")])
    elif off_set is None:
        btn.append([
            InlineKeyboardButton("➥ 𝗣𝗮𝗴𝗲", callback_data="pages"),
            InlineKeyboardButton(f"{page_num}/{total_pages}", callback_data="pages"),
            InlineKeyboardButton("Nᴇxᴛ ⤷", callback_data=f"next_{req}_{key}_{n_offset}")
        ])
    else:
        btn.extend([
            [InlineKeyboardButton(f"{page_num} / {total_pages}", callback_data="pages")],
            [
                InlineKeyboardButton("↲ Bᴀᴄ𝗄", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton("Nᴇxᴛ ⤷", callback_data=f"next_{req}_{key}_{n_offset}")
            ]
        ])

    try:
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(btn))
    except MessageNotModified:
        pass

    await query.answer()
    temp.SEND_ALL_TEMP[key] = files
    
async def auto_filter(client, msg):
    if not msg.text:
        return

    settings = await get_settings(msg.chat.id)

    if msg.text.startswith("/"):
        await asyncio.sleep(5)
        await msg.delete()
        return

    if re.search(r'(?im)(?:https?://|www\.|t\.me/|telegram\.dog/)\S+|@[a-z0-9_]{5,32}\b', msg.text):
        await msg.delete()
        return

    if re.findall(r"((^/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", msg.text):
        await msg.delete()
        return

    if len(msg.text) < 2:
        await msg.delete()
        return

    search = msg.text.lower().strip()
    files, offset, total_results = await get_search_results(search, offset=0, filter=True)

    if not files:
        reqst_gle = search.replace(" ", "+")
        btn_google = InlineKeyboardButton(
            "🔍 𝗖𝗼𝗿𝗿𝗲𝗰𝘁 𝗦𝗽𝗲𝗹𝗹𝗶𝗻𝗴 (𝖦𝗈𝗈𝗴𝗅𝖾) 🔎",
            url=f"https://www.google.com/search?q={reqst_gle}"
        )
        keyboard = InlineKeyboardMarkup([[btn_google]])
        warn_msg = await msg.reply_text(
            text=(
                f"<b>❝ 𝖧𝖾𝗒 {msg.from_user.mention} താഴെ ഉള്ള കാര്യങ്ങൾ ശ്രദ്ധിക്കുക ❞\n\n"
                f"🔹കറക്റ്റ് സ്പെല്ലിംഗിൽ ചോദിക്കുക. (ഇംഗ്ലീഷിൽ മാത്രം)\n\n"
                f"🔸സിനിമകൾ ഇംഗ്ലീഷിൽ Type ചെയ്ത് മാത്രം ചോദിക്കുക.\n\n"
                f"🔹OTT റിലീസ് ആകാത്ത സിനിമകൾ ചോദിക്കരുത്.\n\n"
                f"🔸സിനിമയുടെ പേര് [വർഷം ഭാഷ] ഈ രീതിയിൽ ചോദിക്കുക.\n\n"
                f"🔹സിനിമ Request ചെയ്യുമ്പോൾ Symbols ഒഴിവാക്കുക. [+:;'*!-&.. etc !!!</b>"
            ),
            reply_markup=keyboard
        )
        asyncio.create_task(spell_check(msg, warn_msg))
        return

    pre = 'filep' if settings['file_secure'] else 'file'

    if settings["button"]:
        btn = [
            [InlineKeyboardButton(f"[{get_size(file.file_size)}] ⊳ {file.file_name}", callback_data=f'{pre}#{file.file_id}')]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(file.file_name, callback_data=f'{pre}#{file.file_id}'),
                InlineKeyboardButton(get_size(file.file_size), callback_data=f'{pre}#{file.file_id}')
            ]
            for file in files
        ]

    if offset:
        key = f"{msg.chat.id}-{msg.id}"
        BUTTONS[key] = search
        req = msg.from_user.id if msg.from_user else 0
        btn.append([
            InlineKeyboardButton("➥ 𝗣𝗮𝗴𝗲", callback_data="pages"),
            InlineKeyboardButton(f"1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
            InlineKeyboardButton("Nᴇxᴛ ⤷", callback_data=f"next_{req}_{key}_{offset}")
        ])

    cap_func = random.choice(CAPTIONS)
    caption = cap_func(msg.from_user.mention if msg.from_user else "Sir", search.replace(" ", "_"))

    result_msg = await msg.reply_text(caption, reply_markup=InlineKeyboardMarkup(btn))
    asyncio.create_task(auto_delete(msg, result_msg))


    
@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT, show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer(script.OLD_ALRT_TXT, show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer(script.TOP_ALRT_MSG)
    k = await manual_filters(bot, query.message, text=movie)
    if k == False:
        files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            k = await query.message.edit(script.MVE_NT_FND)
    
@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return await query.answer('Piracy Is Crime')
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return await query.answer('Piracy Is Crime')

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer('Piracy Is Crime')

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("That's not for you!!", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer('Piracy Is Crime')
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer('Piracy Is Crime')
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('Piracy Is Crime')
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('Piracy Is Crime')
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer('Piracy Is Crime')
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name        
        size = get_size(files.file_size)   
        f_caption = files.file_name
        settings = await get_settings(query.message.chat.id)     
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption, mention=query.from_user.mention)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"
        try:
            if (AUTH_CHANNEL or REQ_CHANNEL) and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            elif settings['botpm']:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            else:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
        except UserIsBlocked:
            await query.answer('Unblock the bot mahn !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
    elif query.data.startswith("checksub"):
        if (AUTH_CHANNEL or REQ_CHANNEL) and not await is_subscribed(client, query):
            await query.answer("I Like Your Smartness, But Don't Be Oversmart 😒", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.file_name
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption, mention=query.from_user.mention)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False
        )
    elif query.data.startswith("killfilesdq"):
        ident, keyword = query.data.split("#")
        await query.message.edit_text(f"<b>Fᴇᴛᴄʜɪɴɢ Fɪʟᴇs ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} ᴏɴ DB... Pʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
        files_media1, files_media2, files_media3, files_media4, files_media5, total_media = await get_bad_files(keyword)        
        await query.message.edit_text(f"<b>Fᴏᴜɴᴅ {total_media} Fɪʟᴇs ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nFɪʟᴇ ᴅᴇʟᴇᴛɪᴏɴ ᴘʀᴏᴄᴇss ᴡɪʟʟ sᴛᴀʀᴛ ɪɴ 5 sᴇᴄᴏɴᴅs!</b>")
        await asyncio.sleep(2)
        deleted = 0
        async with lock:
            try:
                # Delete files from Media collection
                for file in files_media1:
                    file_ids = file.file_id
                    file_name = file.file_name
                    result = await Media.collection.delete_one({
                        '_id': file_ids,
                    })
                    if result.deleted_count:
                        logger.info(f'Fɪʟᴇ Fᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}! Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {file_name} ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ.')
                    deleted += 1
                    if deleted % 100 == 0:
                        await query.message.edit_text(f"<b>Pʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ ғᴏʀ ᴅᴇʟᴇᴛɪɴɢ ғɪʟᴇs ғʀᴏᴍ DB. Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nPʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
                # Delete files from Media2 collection
                for file in files_media2:
                    file_ids = file.file_id
                    file_name = file.file_name
                    result = await Media2.collection.delete_one({
                        '_id': file_ids,
                    })
                    if result.deleted_count:
                        logger.info(f'Fɪʟᴇ Fᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}! Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {file_name} ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ.')
                    deleted += 1
                    if deleted % 100 == 0:
                        await query.message.edit_text(f"<b>Pʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ ғᴏʀ ᴅᴇʟᴇᴛɪɴɢ ғɪʟᴇs ғʀᴏᴍ DB. Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nPʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
                for file in files_media3:
                    file_ids = file.file_id
                    file_name = file.file_name
                    result = await Media3.collection.delete_one({
                        '_id': file_ids,
                    })
                    if result.deleted_count:
                        logger.info(f'Fɪʟᴇ Fᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}! Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {file_name} ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ.')
                    deleted += 1
                    if deleted % 100 == 0:
                        await query.message.edit_text(f"<b>Pʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ ғᴏʀ ᴅᴇʟᴇᴛɪɴɢ ғɪʟᴇs ғʀᴏᴍ DB. Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nPʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
                # Delete files from Media4 collection
                for file in files_media4:
                    file_ids = file.file_id
                    file_name = file.file_name
                    result = await Media4.collection.delete_one({
                        '_id': file_ids,
                    })
                    if result.deleted_count:
                        logger.info(f'Fɪʟᴇ Fᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}! Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {file_name} ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ.')
                    deleted += 1
                    if deleted % 100 == 0:
                        await query.message.edit_text(f"<b>Pʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ ғᴏʀ ᴅᴇʟᴇᴛɪɴɢ ғɪʟᴇs ғʀᴏᴍ DB. Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nPʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
                for file in files_media5:
                    file_ids = file.file_id
                    file_name = file.file_name
                    result = await Media5.collection.delete_one({
                        '_id': file_ids,
                    })
                    if result.deleted_count:
                        logger.info(f'Fɪʟᴇ Fᴏᴜɴᴅ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}! Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {file_name} ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ.')
                    deleted += 1
                    if deleted % 100 == 0:
                        await query.message.edit_text(f"<b>Pʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ ғᴏʀ ᴅᴇʟᴇᴛɪɴɢ ғɪʟᴇs ғʀᴏᴍ DB. Sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword} !\n\nPʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>")
            except Exception as e:
                logger.exception
                await query.message.edit_text(f'Eʀʀᴏʀ: {e}')
            else:       
                await query.message.edit_text(f"<b>Pʀᴏᴄᴇss Cᴏᴍᴘʟᴇᴛᴇᴅ ғᴏʀ ғɪʟᴇ ᴅᴇʟᴇᴛɪᴏɴ !\n\nSᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ {str(deleted)} ғɪʟᴇs ғʀᴏᴍ DB ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {keyword}.</b>")

    elif query.data == "mfna":
        await query.answer("𝑴𝒂𝒏𝒖𝒂𝒍 𝑭𝒊𝒍𝒕𝒆𝒓 𝒊𝒔 𝑪𝒖𝒓𝒓𝒆𝒏𝒕𝒍𝒚 𝑫𝒊𝒔𝒂𝒃𝒍𝒆𝒅..!!", show_alert=True)
    
    elif query.data == "qinfo":
        await query.answer("𝑮𝒍𝒐𝒃𝒂𝒍 𝑭𝒊𝒍𝒕𝒆𝒓𝒔 𝒊𝒔 𝑪𝒖𝒓𝒓𝒆𝒏𝒕𝒍𝒚 𝑫𝒊𝒔𝒂𝒃𝒍𝒆𝒅..!!", show_alert=True)
        
    elif query.data.startswith("send_fall"):
        temp_var, userid = query.data.split("#")
        if int(query.from_user.id) not in [query.message.reply_to_message.from_user.id, 0]:
            return await query.answer("This is not Your Request 🚫\n\nDo Search your own ✅", show_alert=True)
        files = temp.SEND_ALL_TEMP.get(userid)
        is_over = await send_all(client, query.from_user.id, files)
        if is_over == 'done':
            return await query.answer(f"Hᴇʏ {query.from_user.first_name}, Aʟʟ ғɪʟᴇs ᴏɴ ᴛʜɪs ᴘᴀɢᴇ ʜᴀs ʙᴇᴇɴ sᴇɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ ᴛᴏ ʏᴏᴜʀ PM !", show_alert=True)
        elif is_over == 'fal':
            file_id = "none"
            return await query.answer(url=f"https://t.me/{temp.U_NAME}?start={userid}_{file_id}")
        else:
            return await query.answer(f"Eʀʀᴏʀ: {is_over}", show_alert=True)
            

        
    elif query.data == "pages":
        await query.answer('Piracy Is Crime ✨')
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘs ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
            InlineKeyboardButton('👥 ᴄᴏᴍᴍᴜɴɪᴛʏ 👥', callback_data='commun'),
            InlineKeyboardButton('🤖 ʙᴏᴛ ɪɴғᴏ 🤖', callback_data='about')
            ],[
            InlineKeyboardButton('🎁 ʜᴇʟᴘ 🎁', callback_data='help'),            
            InlineKeyboardButton('🪬 ᴀʙᴏᴜᴛ 🪬', callback_data='botinfo')
            ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer('Piracy Is Crime ✨')    
    elif query.data == "commun":
        buttons = [[
            InlineKeyboardButton("👥 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐆𝐫𝐨𝐮𝐩", url=GRP_LNK),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.COMMUN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "movedow":
        buttons = [[
            InlineKeyboardButton("👥 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐆𝐫𝐨𝐮𝐩", url=GRP_LNK),
            InlineKeyboardButton('⬅️ 𝑩𝒂𝒄𝒌', callback_data='help')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MOVDOW_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "movereqs":
        buttons = [[
            InlineKeyboardButton("👥 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐆𝐫𝐨𝐮𝐩", url=GRP_LNK),
            InlineKeyboardButton('⬅️ 𝑩𝒂𝒄𝒌', callback_data='help')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MOVREQ_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "movereq":
        buttons = [[
            InlineKeyboardButton("👥 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐆𝐫𝐨𝐮𝐩", url=GRP_LNK),
            InlineKeyboardButton('⬅️ 𝑩𝒂𝒄𝒌', callback_data='commun')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MOVREQ_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('🕹 𝑴𝒂𝒏𝒖𝒂𝒍 𝑭𝒊𝒍𝒕𝒆𝒓', 'mfna'),
            InlineKeyboardButton('🌏 𝑮𝒍𝒐𝒃𝒂𝒍 𝑭𝒊𝒍𝒕𝒆𝒓𝒔', 'qinfo'),
            InlineKeyboardButton('𝑨𝒖𝒕𝒐 𝒇𝒊𝒍𝒕𝒆𝒓 📥', callback_data='autofilter')                   
            ],[
            InlineKeyboardButton('🤷‍♂️ 𝐇𝐎𝐖 𝐓𝐎 𝐑𝐄𝐐𝐔𝐄𝐒𝐓 🤷🏻', callback_data='movereqs')
            ],[
            InlineKeyboardButton('🤷‍♂️ 𝐇𝐎𝐖 𝐓𝐎 𝐃𝐎𝐖𝐍𝐋𝐎𝐀𝐃 🤷🏻', callback_data='movedow')           
            ],[
            InlineKeyboardButton('⬅️ 𝑩𝒂𝒄𝒌', callback_data='start'),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "botinfo":
        buttons = [[                             
            InlineKeyboardButton('📈 𝑺𝒕𝒂𝒕𝒖𝒔', callback_data='stats'),
            InlineKeyboardButton('☠ 𝑺𝒐𝒖𝒓𝒄𝒆', callback_data='sorce')
            ],[
            InlineKeyboardButton("𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐆𝐫𝐨𝐮𝐩", url=GRP_LNK),
            ],[
            InlineKeyboardButton('🪬 𝑯𝒐𝒎𝒆 🪬', callback_data='start'),
            InlineKeyboardButton('⬅️ 𝑩𝒂𝒄𝒌', callback_data='help')                       
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BOTINFO_TXT.format(temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        buttons = [[            
            InlineKeyboardButton('🪬 𝑯𝒐𝒎𝒆 🪬', callback_data='start'),
            InlineKeyboardButton('⬅️ 𝑩𝒂𝒄𝒌', callback_data='help')                                    
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )        
    elif query.data == "sorce":
        buttons = [[
            InlineKeyboardButton('⬅️ 𝑩𝒂𝒄𝒌', callback_data='botinfo')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SORCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('⬅️ 𝑩𝒂𝒄𝒌', callback_data='help')
        ]]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "stats":
        if query.from_user.id not in ADMINS:
            await query.answer(
                "⚠ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ⚠\n\nIᴛꜱ ᴏɴʟʏ ғᴏʀ ᴍʏ ADMINS",
                show_alert=True
            )
            return

        await query.message.edit_text("ᴡᴀɪᴛ.....")

        buttons = [[
            InlineKeyboardButton("⬅️ 𝑩𝒂𝒄𝒌", callback_data="botinfo"),
            InlineKeyboardButton('⟲ Rᴇғʀᴇsʜ', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)

        tot1 = await Media.count_documents()
        tot2 = await Media2.count_documents()
        tot3 = await Media3.count_documents()
        tot4 = await Media4.count_documents()
        tot5 = await Media5.count_documents()

        total_files = tot1 + tot2 + tot3 + tot4 + tot5

        users = await db.total_users_count()
        chats = await db.total_chat_count()

        s1 = await clientDB.command("dbStats")
        s2 = await clientDB2.command("dbStats")
        s3 = await clientDB3.command("dbStats")
        s4 = await clientDB4.command("dbStats")
        s5 = await clientDB5.command("dbStats")

        def calc(stat):
            used = (stat.get("dataSize", 0) + stat.get("indexSize", 0)) / (1024 * 1024)
            storage = stat.get("storageSize", 0) / (1024 * 1024)
            free = max(storage - used, 0)
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

        await query.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rfrsh":
        if query.from_user.id not in ADMINS:
            await query.answer(
                "⚠ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ⚠\n\nIᴛꜱ ᴏɴʟʏ ғᴏʀ ᴍʏ ADMINS",
                show_alert=True
            )
            return

        await query.message.edit_text("ᴡᴀɪᴛ.....")

        buttons = [[
            InlineKeyboardButton("⬅️ 𝑩𝒂𝒄𝒌", callback_data="botinfo"),
            InlineKeyboardButton('⟲ Rᴇғʀᴇsʜ', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)

        tot1 = await Media.count_documents()
        tot2 = await Media2.count_documents()
        tot3 = await Media3.count_documents()
        tot4 = await Media4.count_documents()
        tot5 = await Media5.count_documents()

        total_files = tot1 + tot2 + tot3 + tot4 + tot5

        users = await db.total_users_count()
        chats = await db.total_chat_count()

        s1 = await clientDB.command("dbStats")
        s2 = await clientDB2.command("dbStats")
        s3 = await clientDB3.command("dbStats")
        s4 = await clientDB4.command("dbStats")
        s5 = await clientDB5.command("dbStats")

        def calc(stat):
            used = (stat.get("dataSize", 0) + stat.get("indexSize", 0)) / (1024 * 1024)
            storage = stat.get("storageSize", 0) / (1024 * 1024)
            free = max(storage - used, 0)
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

        await query.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return await query.answer('Piracy Is Crime')

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Filter Button',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Single' if settings["button"] else 'Double',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Bot PM', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["botpm"] else '❌ No',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('File Secure',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["file_secure"] else '❌ No',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["imdb"] else '❌ No',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Spell Check',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["spell_check"] else '❌ No',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Welcome', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["welcome"] else '❌ No',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer('Piracy Is Crime')

