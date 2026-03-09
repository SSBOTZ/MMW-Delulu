import os
from urllib.parse import quote
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


@Client.on_message(filters.command(["share_text", "share", "sharetext"]))
async def share_text(client, message):

    ask_msg = await client.ask(
        chat_id=message.from_user.id,
        text="📝 **Send the text you want to share.**"
    )

    if ask_msg and (ask_msg.text or ask_msg.caption):
        input_text = ask_msg.text or ask_msg.caption
    else:
        await ask_msg.reply_text(
            text=(
                "⚠️ **Invalid Input**\n\n"
                "• Please send a **text message only**.\n"
                "• **Media files are not supported.**"
            )
        )
        return

    share_link = f"https://t.me/share/url?url={quote(input_text)}"

    await ask_msg.reply_text(
        text=(
            "✨ **Your Share Link Is Ready!**\n\n"
            "🔗 Click the button below to share your text."
        ),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🚀 Share Text",
                        url=share_link
                    )
                ]
            ]
        )
    )
