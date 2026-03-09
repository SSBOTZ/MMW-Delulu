import motor.motor_asyncio
from info import *

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups


    async def new_user(self, id, name):
        return {
            "id": int(id),
            "name": name,
            "ban_status": {
                "is_banned": False,
                "ban_reason": ""
            }
        }


    async def new_group(self, id, title):
        return {
            "id": int(id),
            "title": title,
            "chat_status": {
                "is_disabled": False,
                "reason": ""
            }
        }


    async def add_user(self, id, name):
        user = await self.new_user(id, name)
        await self.col.insert_one(user)


    async def is_user_exist(self, id):
        user = await self.col.find_one({"id": int(id)})
        return bool(user)


    async def total_users_count(self):
        return await self.col.count_documents({})


    async def remove_ban(self, id):
        ban_status = {
            "is_banned": False,
            "ban_reason": ""
        }
        await self.col.update_one(
            {"id": int(id)},
            {"$set": {"ban_status": ban_status}}
        )


    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = {
            "is_banned": True,
            "ban_reason": ban_reason
        }
        await self.col.update_one(
            {"id": int(user_id)},
            {"$set": {"ban_status": ban_status}}
        )


    async def get_ban_status(self, id):
        default = {
            "is_banned": False,
            "ban_reason": ""
        }

        user = await self.col.find_one({"id": int(id)})

        if not user:
            return default

        return user.get("ban_status", default)


    async def get_all_users(self):
        return self.col.find({})


    async def delete_user(self, user_id):
        await self.col.delete_many({"id": int(user_id)})


    async def get_banned(self):
        users = self.col.find({"ban_status.is_banned": True})
        chats = self.grp.find({"chat_status.is_disabled": True})

        banned_users = [user["id"] async for user in users]
        banned_chats = [chat["id"] async for chat in chats]

        return banned_users, banned_chats


    async def add_chat(self, chat, title):
        chat_data = await self.new_group(chat, title)
        await self.grp.insert_one(chat_data)


    async def get_chat(self, chat):
        chat_data = await self.grp.find_one({"id": int(chat)})

        if not chat_data:
            return False

        return chat_data.get("chat_status")


    async def re_enable_chat(self, id):
        chat_status = {
            "is_disabled": False,
            "reason": ""
        }

        await self.grp.update_one(
            {"id": int(id)},
            {"$set": {"chat_status": chat_status}}
        )


    async def disable_chat(self, chat, reason="No Reason"):
        chat_status = {
            "is_disabled": True,
            "reason": reason
        }

        await self.grp.update_one(
            {"id": int(chat)},
            {"$set": {"chat_status": chat_status}}
        )


    async def update_settings(self, id, settings):
        await self.grp.update_one(
            {"id": int(id)},
            {"$set": {"settings": settings}}
        )


    async def get_settings(self, id):

        default = {
            "button": SINGLE_BUTTON,
            "botpm": P_TTI_SHOW_OFF,
            "file_secure": PROTECT_CONTENT,
            "imdb": IMDB,
            "spell_check": SPELL_CHECK_REPLY,
            "welcome": MELCOW_NEW_USERS,
            "template": IMDB_TEMPLATE
        }

        chat = await self.grp.find_one({"id": int(id)})

        if chat:
            return chat.get("settings", default)

        return default


    async def total_chat_count(self):
        return await self.grp.count_documents({})


    async def get_all_chats(self):
        return self.grp.find({})


    async def get_db_size(self):
        stats = await self.db.command("dbstats")
        return stats["dataSize"]


db = Database(DATABASE_URI, DATABASE_NAME)
