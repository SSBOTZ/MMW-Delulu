import os
import sys
import asyncio
import aiohttp
import logging
from datetime import datetime
from typing import Union, Optional, AsyncGenerator
from aiohttp import web
from dotenv import load_dotenv
from pyrogram import Client, types, utils as pyroutils
from pyrogram.errors import FloodWait
from database.ia_filterdb import (
    db as clientDB,
    db2 as clientDB2,
    db3 as clientDB3,
    db4 as clientDB4,
    db5 as clientDB5,
    Media, Media2, Media3, Media4, Media5,
    choose_mediaDB,
)
from database.users_chats_db import db
from database.join_reqs import JoinReqs
from plugins.index import index_files_to_db, incol
from plugins.webcode import bot_run
from utils import *
from sample_info import tempDict
from info import *

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S"
)

logger = logging.getLogger("AUTO_FILTER_BOT-MMW-Delulu")

# Load ENV
load_dotenv("./dynamic.env", override=True, encoding="utf-8")

name = "main"

DB_OPTIONS = [
    (clientDB, DATABASE_URI, "🌐 Primary DB"),
    (clientDB2, SECONDDB_URI, "🥈 Second DB"),
    (clientDB3, DATABASE_URI3, "🧩 Third DB"),
    (clientDB4, DATABASE_URI4, "📁 Fourth DB"),
    (clientDB5, DATABASE_URI5, "💾 Fifth DB"),
]

pyroutils.MIN_CHAT_ID = -999999999999
pyroutils.MIN_CHANNEL_ID = -100999999999999

RESTART_INTERVAL = 24 * 60 * 60
DB_SIZE_LIMIT_MB = 160
MAX_DB_CAPACITY_MB = 512
KEEP_ALIVE_URL = "https://moderate-paulie-mmwgoku-46260985.koyeb.app/" #koyeb & render service url
ALIVE_INTERVAL = 12

async def alive():
    if not KEEP_ALIVE_URL:
        return

    timeout = aiohttp.ClientTimeout(total=8)

    while True:
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(KEEP_ALIVE_URL):
                    logger.info("💓 Keep-alive ping successful")
        except Exception as e:
            logger.warning(f"⚠️ Keep-alive failed: {e}")

        await asyncio.sleep(ALIVE_INTERVAL)
        


async def check_db_space(db_client):
    try:
        stats = await db_client.command("dbStats")
        used_mb = (stats["dataSize"] + stats["indexSize"]) / (1024 ** 2)
        free_mb = round(MAX_DB_CAPACITY_MB - used_mb, 2)

        logger.info(f"💾 DB Usage: {round(used_mb,2)} MB | Free: {free_mb} MB")
        return free_mb

    except Exception as e:
        logger.error(f"❌ DB check failed: {e}")
        return 0


async def restart_index(bot):

    progress_document = incol.find_one({"_id": "index_progress"})

    if progress_document:
        last_indexed_file = progress_document.get("last_indexed_file", 0)
        last_msg_id = progress_document.get("last_msg_id")
        chat_id = progress_document.get("chat_id")

        temp.CURRENT = int(last_indexed_file)

        msg = await bot.send_message(
            chat_id=int(LOG_CHANNEL),
            text="♻️ Delulu's 𝙄𝙣𝙙𝙚𝙭 𝙍𝙚𝙨𝙩𝙖𝙧𝙩𝙞𝙣𝙜..."
        )

        await index_files_to_db(last_msg_id, chat_id, msg, bot)


class Bot(Client):

    def __init__(self):

        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=120,
            plugins={"root": "plugins"},
            sleep_threshold=30,
        )
    async def restart_loop(self):

        while True:

            await asyncio.sleep(RESTART_INTERVAL)

            logger.warning("♻️ Delulu Restarting after 1 day")

            os.execl(sys.executable, sys.executable, *sys.argv)
            

    async def start(self):

        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats

        await super().start()

        if REQ_CHANNEL is None:

            with open("./dynamic.env", "wt+") as f:

                req = await JoinReqs().get_fsub_chat()

                if req is None:
                    req = False
                else:
                    req = req["chat_id"]

                f.write(f"REQ_CHANNEL={req}\n")

            os.execl(sys.executable, sys.executable, "bot.py")
            return

        me = await self.get_me()

        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name

        self.username = "@" + me.username

        for media_cls in (Media, Media2, Media3, Media4, Media5):

            try:
                await media_cls.ensure_indexes()
                logger.info(f"📑 Index ensured {media_cls.__name__}")
            except Exception:
                pass

        selected = False

        for db_client, uri, label in DB_OPTIONS:

            if not uri:
                continue

            logger.info(f"🔎 Checking {label}")

            free = await check_db_space(db_client)

            if free > DB_SIZE_LIMIT_MB:

                tempDict["indexDB"] = uri
                logger.info(f"✅ Using {label}")

                selected = True
                break

        if not selected:
            logger.error("❌ No Database Available For Active Delulu")
            raise SystemExit(1)

        await choose_mediaDB()

        await self.send_message(
            chat_id=LOG_CHANNEL,
            text="Delulu 𝙍𝙚𝙨𝙩𝙖𝙧𝙩𝙚𝙙 ❤️‍🩹"
        )

        app = web.AppRunner(await bot_run())
        await app.setup()

        await web.TCPSite(app, "0.0.0.0", 8080).start()

        asyncio.create_task(self.restart_loop())
        asyncio.create_task(alive())
        await restart_index(self)

    async def stop(self, *args):
        await super().stop()

    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:

        current = offset

        while True:

            new_diff = min(200, limit - current)

            if new_diff <= 0:
                return

            messages = await self.get_messages(
                chat_id,
                list(range(current, current + new_diff + 1))
            )

            for message in messages:
                yield message
                current += 1


Bot().run()
