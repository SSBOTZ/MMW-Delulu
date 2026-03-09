import motor.motor_asyncio
from info import JOIN_REQS_DB, REQ_CHANNEL


class JoinReqs:

    def __init__(self):

        if DATABASE_URI:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(JOIN_REQS_DB)

            self.db = self.client["JoinReqs"]

            self.users = self.db[str(REQ_CHANNEL)]

            self.chat = self.db["ChatId"]

        else:
            self.client = None
            self.db = None
            self.users = None
            self.chat = None


    def is_active(self):
        return self.client is not None


    async def add_user(self, user_id, first_name, username, date):

        if not self.users:
            return

        data = {
            "_id": int(user_id),
            "user_id": int(user_id),
            "first_name": first_name,
            "username": username,
            "date": date
        }

        try:
            await self.users.insert_one(data)
        except:
            pass


    async def get_user(self, user_id):

        if not self.users:
            return None

        return await self.users.find_one({"user_id": int(user_id)})


    async def get_all_users(self):

        if not self.users:
            return []

        return await self.users.find().to_list(length=None)


    async def delete_user(self, user_id):

        if not self.users:
            return

        await self.users.delete_one({"user_id": int(user_id)})


    async def delete_all_users(self):

        if not self.users:
            return

        await self.users.delete_many({})


    async def total_users_count(self):

        if not self.users:
            return 0

        return await self.users.count_documents({})


    async def add_fsub_chat(self, chat_id):

        if not self.chat:
            return

        try:
            await self.chat.delete_many({})
            await self.chat.insert_one({"chat_id": int(chat_id)})
        except:
            pass


    async def get_fsub_chat(self):

        if not self.chat:
            return None

        return await self.chat.find_one({})


    async def delete_fsub_chat(self, chat_id):

        if not self.chat:
            return

        await self.chat.delete_one({"chat_id": int(chat_id)})
