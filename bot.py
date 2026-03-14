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

logging.basicConfig(
    level=logging.INFO,
    format="✨ %(asctime)s | %(levelname)s | 𝘿𝙚𝙡𝙪𝙡𝙪 | %(message)s 🚀",
    datefmt="%d-%m-%Y %H:%M:%S"
)

logger = logging.getLogger("𝘿𝙚𝙡𝙪𝙡𝙪")

load_dotenv("./dynamic.env", override=True, encoding="utf-8")

DB_OPTIONS = [
    (clientDB, DATABASE_URI,  "🌍✨ 𝙋𝙧𝙞𝙢𝙖𝙧𝙮 𝘿𝘽"),
    (clientDB2, DATABASE_URI2, "🥈⚡ 𝙎𝙚𝙘𝙤𝙣𝙙 𝘿𝘽"),
    (clientDB3, DATABASE_URI3, "🧩📊 𝙏𝙝𝙞𝙧𝙙 𝘿𝘽"),
    (clientDB4, DATABASE_URI4, "📁🔐 𝙁𝙤𝙪𝙧𝙩𝙝 𝘿𝘽"),
    (clientDB5, DATABASE_URI5, "💾🚀 𝙁𝙞𝙛𝙩𝙝 𝘿𝘽"),
]

pyroutils.MIN_CHAT_ID = -999999999999
pyroutils.MIN_CHANNEL_ID = -100999999999999

RESTART_INTERVAL = 86400
DB_SIZE_LIMIT_MB = 160
MAX_DB_CAPACITY_MB = 512
KEEP_ALIVE_URL = "https://enchanting-rose-hyderabadmy123enchantin-f889e3ba.koyeb.app/"
ALIVE_INTERVAL = 12


async def alive():

    if not KEEP_ALIVE_URL:
        return

    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(timeout=timeout) as session:

        while True:
            try:
                async with session.get(KEEP_ALIVE_URL):
                    logger.info("💓 Keep Alive Ping Success")
            except Exception as e:
                logger.warning(f"⚠️ Keep Alive Failed → {e}")

            await asyncio.sleep(ALIVE_INTERVAL)


async def check_db_space(db_client):

    try:

        stats = await db_client.command("dbStats")

        used_mb = (stats["dataSize"] + stats["indexSize"]) / (1024 ** 2)

        free_mb = round(MAX_DB_CAPACITY_MB - used_mb, 2)

        logger.info(f"💾 Database Usage → {round(used_mb,2)} MB | Free → {free_mb} MB")

        return free_mb

    except Exception as e:

        logger.error(f"❌ Database Check Failed → {e}")

        return 0


async def restart_index(bot):
    progress_document = incol.find_one({"_id": "index_progress"})
    if not progress_document:
        logger.info("✅ No previous index")
        return
    
    if progress_document:
        last_indexed_file = progress_document.get("last_indexed_file", 0)
        last_msg_id = progress_document.get("last_msg_id")
        chat_id = progress_document.get("chat_id")
        logger.info(f"📂 Restarting Index | LastFile: {last_indexed_file}")

        temp.CURRENT = int(last_indexed_file)

        msg = await bot.send_message(
            chat_id=int(LOG_CHANNEL),
            text="♻ 𝘿𝙚𝙡𝙪𝙡𝙪'𝙨 𝙄𝙣𝙙𝙚𝙭 𝙍𝙚𝙨𝙩𝙖𝙧𝙩𝙞𝙣𝙜... ♻️"
        )

        await index_files_to_db(last_msg_id, chat_id, msg, bot)

class Bot(Client):

    def __init__(self):

        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=20,
        )

    async def restart_loop(self):

        while True:

            await asyncio.sleep(RESTART_INTERVAL)

            logger.warning("♻️ MMW-Delulu Bot restarted successfully after 1 day.")

            os.execl(sys.executable, sys.executable, *sys.argv)

    async def start(self):

        logger.info("🚀 𝘿𝙚𝙡𝙪𝙡𝙪'𝙨 Starting")

        b_users, b_chats = await db.get_banned()

        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats

        await super().start()

        logger.info("✅ 𝘿𝙚𝙡𝙪𝙡𝙪'𝙨 Started")

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

        logger.info(f"🤖 𝘿𝙚𝙡𝙪𝙡𝙪'𝙨 Online → {me.first_name} | @{me.username}")

        for media_cls in (Media, Media2, Media3, Media4, Media5):
            try:
                await media_cls.ensure_indexes()
                logger.info(f"📑 Index Ready → {media_cls.__name__}")
            except Exception as e:
                pass

        selected = False

        for db_client, uri, label in DB_OPTIONS:

            if not uri:
                continue

            logger.info(f"🔍 Checking {label}")

            free = await check_db_space(db_client)

            if free > DB_SIZE_LIMIT_MB:

                tempDict["indexDB"] = uri

                logger.info(f"✅ Selected {label}")

                selected = True

                break

        if not selected:

            logger.error("❌ No Available Database Capacity")

            raise SystemExit(1)

        await choose_mediaDB()

        await self.send_message(
            chat_id=LOG_CHANNEL,
            text="❤️‍🔥✨ 𝘿𝙚𝙡𝙪𝙡𝙪 𝙍𝙚𝙨𝙩𝙖𝙧𝙩𝙚𝙙... ✨💫"
        )

        web_app = await bot_run()

        runner = web.AppRunner(web_app)

        await runner.setup()

        await web.TCPSite(runner, "0.0.0.0", 8080).start()

        logger.info("🌐 Web Server Running on Port 8080")

        asyncio.create_task(self.restart_loop())

        asyncio.create_task(alive())

        await restart_index(self)

        logger.info("🎯 𝘿𝙚𝙡𝙪𝙡𝙪 𝙍𝙚𝙨𝙩𝙖𝙧𝙩𝙚𝙙...")

    async def stop(self, *args):

        logger.info("🛑 𝘿𝙚𝙡𝙪𝙡𝙪 Stopped")

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

            try:

                messages = await self.get_messages(
                    chat_id,
                    list(range(current, current + new_diff + 1))
                )

            except FloodWait as e:

                logger.warning(f"⏳ FloodWait {e.value}s")

                await asyncio.sleep(e.value)

                continue

            for message in messages:

                if message:

                    yield message

                current += 1

Bot().run()
