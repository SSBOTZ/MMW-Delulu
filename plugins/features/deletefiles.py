import asyncio
import re
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from database.ia_filterdb import Media, Media2, Media3, Media4, Media5
from info import ADMINS

BATCH_SIZE = 20
SLEEP_TIME = 2
DATABASES = [Media, Media2, Media3, Media4, Media5]

@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def deletemultiplefiles(bot: Client, message: Message):

    if message.chat.type != enums.ChatType.PRIVATE:
        return await message.reply_text(
            f"⚠️ <b>{message.from_user.mention}</b>\n\n❌ This command works <b>only in my PM</b>.",
            parse_mode=enums.ParseMode.HTML
        )

    try:
        keyword = message.text.split(" ", 1)[1].strip()
        if not keyword:
            raise IndexError
    except IndexError:
        return await message.reply_text(
            f"⚠️ <b>Keyword Missing</b>\n\n"
            f"Usage:\n<code>/deletefiles keyword</code>\n\n"
            f"Example:\n<code>/deletefiles unwanted_movie</code>",
            parse_mode=enums.ParseMode.HTML
        )

    confirm_button = InlineKeyboardButton("✅ Continue Deletion", callback_data=f"confirm_delete_files#{keyword}")
    abort_button = InlineKeyboardButton("❌ Cancel", callback_data="close_message")

    markup = InlineKeyboardMarkup([[confirm_button], [abort_button]])

    await message.reply_text(
        f"⚠️ <b>Deletion Confirmation</b>\n\n"
        f"Keyword: <code>{keyword}</code>\n\n"
        f"🚨 This action will permanently remove files from database.\n"
        f"Do you want to continue?",
        reply_markup=markup,
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex(r'^confirm_delete_files#'))
async def confirm_and_delete_files_by_keyword(bot: Client, query: CallbackQuery):

    await query.answer()

    _, keyword = query.data.split("#", 1)

    raw_pattern = r'(\b|[\.\+\-_])' + re.escape(keyword) + r'(\b|[\.\+\-_])'
    regex = re.compile(raw_pattern, flags=re.IGNORECASE)

    filter_query = {'file_name': regex}

    await query.message.edit_text(
        f"🔍 <b>Scanning Database...</b>\n\n"
        f"Searching files with keyword:\n<code>{keyword}</code>",
        parse_mode=enums.ParseMode.HTML
    )

    initial_count = 0

    for db in DATABASES:
        initial_count += await db.count_documents(filter_query)

    if initial_count == 0:
        return await query.message.edit_text(
            f"❌ <b>No Files Found</b>\n\nKeyword: <code>{keyword}</code>",
            parse_mode=enums.ParseMode.HTML
        )

    await query.message.edit_text(
        f"📂 <b>Files Found</b>\n\n"
        f"Total: <code>{initial_count}</code>\n"
        f"Keyword: <code>{keyword}</code>\n\n"
        f"🗑 Starting batch deletion...",
        parse_mode=enums.ParseMode.HTML
    )

    deleted_count = 0

    for db in DATABASES:

        while True:

            documents_to_delete = await db.collection.find(
                filter_query, {"_id": 1}
            ).limit(BATCH_SIZE).to_list(length=BATCH_SIZE)

            if not documents_to_delete:
                break

            ids_to_delete = [doc["_id"] for doc in documents_to_delete]

            batch_result = await db.collection.delete_many({"_id": {"$in": ids_to_delete}})

            deleted_in_batch = batch_result.deleted_count
            deleted_count += deleted_in_batch

            await query.message.edit_text(
                f"🗑 <b>Deleting Files...</b>\n\n"
                f"Keyword: <code>{keyword}</code>\n"
                f"Deleted: <code>{deleted_count}</code> / <code>{initial_count}</code>",
                parse_mode=enums.ParseMode.HTML
            )

            if deleted_in_batch == 0:
                break

            await asyncio.sleep(SLEEP_TIME)

    await query.message.edit_text(
        f"✅ <b>Deletion Completed</b>\n\n"
        f"Keyword: <code>{keyword}</code>\n"
        f"Total Deleted: <code>{deleted_count}</code>",
        parse_mode=enums.ParseMode.HTML
    )


@Client.on_callback_query(filters.regex(r'^close_message$'))
async def close_message(bot: Client, query: CallbackQuery):
    await query.answer()
    await query.message.delete()
