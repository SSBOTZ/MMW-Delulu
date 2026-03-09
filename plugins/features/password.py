import random
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


@Client.on_message(filters.command(["genpassword", 'genpw']))
async def password(bot, update):
    message = await update.reply_text(text="`Processing...`")
    
    lowercase = "abcdefghijklmnopqrstuvwxyz"
    uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "1234567890"
    special = "!@#$%^&*()_+"
    
    all_characters = lowercase + uppercase + digits + special
    
    if len(update.command) > 1:
        try:
            qw = update.text.split(" ", 1)[1]
            limit = int(qw)
            if limit < 4 or limit > 32:  # Ensure the length is reasonable (between 4 and 32 characters)
                raise ValueError("Password length must be between 4 and 32 characters.")
        except (ValueError, IndexError):
            await message.edit_text("Please provide a valid password length (between 4 and 32 characters).")
            return
    else:
        ST = ["5", "7", "6", "9", "10", "12", "14", "16"]
        qw = random.choice(ST)
        limit = int(qw)
    
    random_value = "".join(random.sample(all_characters, limit))
    
    txt = f"<b>Limit:</b> {str(limit)} \n<b>Password: <code>{random_value}</code></b>"

    await message.edit_text(text=txt, parse_mode=enums.ParseMode.HTML)
