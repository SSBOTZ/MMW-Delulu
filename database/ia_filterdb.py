import logging
from struct import pack
import re
import base64
import asyncio
from typing import List, Tuple, Optional, Dict, Any, Union
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from info import *
from umongo import Document
from umongo.fields import StrField
from sample_info import tempDict

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]
instance = Instance.from_db(db)

client2 = AsyncIOMotorClient(DATABASE_URI2)
db2 = client2[DATABASE_NAME]
instance2 = Instance.from_db(db2)

client3 = AsyncIOMotorClient(DATABASE_URI3)
db3 = client3[DATABASE_NAME]
instance3 = Instance.from_db(db3)

client4 = AsyncIOMotorClient(DATABASE_URI4)
db4 = client4[DATABASE_NAME]
instance4 = Instance.from_db(db4)

client5 = AsyncIOMotorClient(DATABASE_URI5)
db5 = client5[DATABASE_NAME]
instance5 = Instance.from_db(db5)

@instance.register
class Media(Document):
    file_id = fields.StrField(attribute="_id")
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = StrField(allow_none=True) 

    class Meta:
        collection_name = COLLECTION_NAME
        indexes = ["$file_name"]

@instance2.register
class Media2(Document):
    file_id = fields.StrField(attribute="_id")
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = StrField(allow_none=True) 

    class Meta:
        collection_name = COLLECTION_NAME
        indexes = ["$file_name"]

@instance3.register
class Media3(Document):
    file_id = fields.StrField(attribute="_id")
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = StrField(allow_none=True) 
    
    class Meta:
        collection_name = COLLECTION_NAME
        indexes = ["$file_name"]

@instance4.register
class Media4(Document):
    file_id = fields.StrField(attribute="_id")
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = StrField(allow_none=True) 
    
    class Meta:
        collection_name = COLLECTION_NAME
        indexes = ["$file_name"]

@instance5.register
class Media5(Document):
    file_id = fields.StrField(attribute="_id")
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = StrField(allow_none=True) 
    
    class Meta:
        collection_name = COLLECTION_NAME
        indexes = ["$file_name"]

ALL_MEDIA = [Media, Media2, Media3, Media4, Media5]
saveMedia: Optional[Document] = None

async def choose_mediaDB() -> None:
    global saveMedia

    uri = tempDict['indexDB']

    db_mapping = {
        DATABASE_URI: (Media, "𝗣𝗿𝗶𝗺𝗮𝗿𝘆 𝗗𝗕"),
        DATABASE_URI2: (Media2, "𝗦𝗲𝗰𝗼𝗻𝗱𝗮𝗿𝘆 𝗗𝗕"),
        DATABASE_URI3: (Media3, "𝗧𝗵𝗶𝗿𝗱 𝗗𝗕"),
        DATABASE_URI4: (Media4, "𝗙𝗼𝘂𝗿𝘁𝗵 𝗗𝗕"),
        DATABASE_URI5: (Media5, "𝗙𝗶𝗳𝘁𝗵 𝗗𝗕"),
    }

    if uri in db_mapping:
        cls, name = db_mapping[uri]
        saveMedia = cls
    else:
        saveMedia = Media  # Fallback to primary
        
async def check_file(media):
    file_id, file_ref = unpack_new_file_id(media.file_id)
    tasks = [m.collection.find_one({"_id": file_id}) for m in ALL_MEDIA]
    results = await asyncio.gather(*tasks)
    for r in results:
        if r:
            return None
    return "okda"

async def save_file(media):
    global saveMedia
    file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"(_|\+|\-|\.|\[.*?\]|\@.*?|www.*?|MLM)", " ", str(media.file_name))

    try:
        caption_obj = getattr(media, "caption", None)
        caption_html = caption_obj.html if caption_obj else None
        file = saveMedia(
            file_id=file_id,
            file_ref=file_ref,
            file_name=file_name,
            file_size=media.file_size,
            file_type=media.file_type,
            mime_type=media.mime_type,
            caption=caption_html
        )
        await file.commit()
        logger.info(f"Saved {file_name}")
        return True
    except DuplicateKeyError:
        return False
    except ValidationError:
        logger.exception("Validation error")
        return False

async def get_search_results(query, file_type=None, max_results=10, offset=0, filter=False):
    query = query.strip()

    if not query:
        raw_pattern = "."
    elif " " not in query:
        raw_pattern = r"(\b|[\.\+\-_]|\s)" + query + r"(\b|[\.\+\-_]|\s)"
    else:
        raw_pattern = query.replace(" ", r".*[\s\.\+\-_]")

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return [], "", 0

    if USE_CAPTION_FILTER:
        filter = {"$or": [{"file_name": regex}, {"caption": regex}]}
    else:
        filter = {"file_name": regex}

    if file_type:
        filter["file_type"] = file_type

    tasks = [m.find(filter).sort("$natural", -1).to_list(length=50) for m in ALL_MEDIA]
    results = await asyncio.gather(*tasks)

    merged = []
    for r in results:
        merged.extend(r)

    merged = merged[offset:offset + max_results]
    total = sum(len(r) for r in results)

    next_offset = offset + len(merged)
    if next_offset >= total:
        next_offset = ""

    return merged, next_offset, total

async def get_bad_files(query, file_type=None, filter=False):
    """For given query return (results, next_offset)"""
    query = query.strip()

    if not query:
        raw_pattern = '.'
    elif ' ' not in query:
        raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])'
    else:
        raw_pattern = query.replace(' ', r'.*[\s\.\+\-_]')

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return []

    if USE_CAPTION_FILTER:
        filter = {'file_name': regex}
    else:
        filter = {'file_name': regex}

    if file_type:
        filter['file_type'] = file_type

    total_results_media1 = await Media.count_documents(filter)
    total_results_media2 = await Media2.count_documents(filter)
    total_results_media3 = await Media3.count_documents(filter)
    total_results_media4 = await Media4.count_documents(filter)
    total_results_media5 = await Media5.count_documents(filter)
    total_results = total_results_media1 + total_results_media2 + total_results_media3 + total_results_media4 + total_results_media5

    cursor_media1 = Media.find(filter)
    cursor_media1.sort('$natural', -1)
    files_media1 = await cursor_media1.to_list(length=total_results_media1)

    cursor_media2 = Media2.find(filter)
    cursor_media2.sort('$natural', -1)
    files_media2 = await cursor_media2.to_list(length=total_results_media2)

    cursor_media3 = Media3.find(filter)
    cursor_media3.sort('$natural', -1)
    files_media3 = await cursor_media3.to_list(length=total_results_media3)

    cursor_media4 = Media4.find(filter)
    cursor_media4.sort('$natural', -1)
    files_media4 = await cursor_media4.to_list(length=total_results_media4)

    cursor_media5 = Media5.find(filter)
    cursor_media5.sort('$natural', -1)
    files_media5 = await cursor_media5.to_list(length=total_results_media4)
    
    return files_media1, files_media2, files_media3, files_media4, files_media5, total_results
    
async def delete_files_below_threshold(db, threshold_size_mb: int = 40, batch_size: int = 20, chat_id: int = None, message_id: int = None):
    cursor_media1 = Media.find({"file_size": {"$lt": threshold_size_mb * 1024 * 1024}}).limit(batch_size // 2)
    cursor_media2 = Media2.find({"file_size": {"$lt": threshold_size_mb * 1024 * 1024}}).limit(batch_size // 2)
    cursor_media3 = Media3.find({"file_size": {"$lt": threshold_size_mb * 1024 * 1024}}).limit(batch_size // 2)
    cursor_media4 = Media4.find({"file_size": {"$lt": threshold_size_mb * 1024 * 1024}}).limit(batch_size // 2)
    cursor_media5 = Media5.find({"file_size": {"$lt": threshold_size_mb * 1024 * 1024}}).limit(batch_size // 2)
    
    deleted_count_media1 = 0
    deleted_count_media2 = 0
    deleted_count_media3 = 0
    deleted_count_media4 = 0
    deleted_count_media5 = 0
    
    async for document in cursor_media1:
        try:
            await Media.collection.delete_one({"_id": document["file_id"]})
            deleted_count_media1 += 1
            print(f'Deleted file from Media: {document["file_name"]}')
        except Exception as e:
            print(f'Error deleting file from Media: {document["file_name"]}, {e}')

    async for document in cursor_media2:
        try:
            await Media2.collection.delete_one({"_id": document["file_id"]})
            deleted_count_media2 += 1
            print(f'Deleted file from Mediaa: {document["file_name"]}')
        except Exception as e:
            print(f'Error deleting file from Mediaa: {document["file_name"]}, {e}')

    async for document in cursor_media3:
        try:
            await Media3.collection.delete_one({"_id": document["file_id"]})
            deleted_count_media3 += 1
            print(f'Deleted file from Media: {document["file_name"]}')
        except Exception as e:
            print(f'Error deleting file from Media: {document["file_name"]}, {e}')

    async for document in cursor_media4:
        try:
            await Media4.collection.delete_one({"_id": document["file_id"]})
            deleted_count_media4 += 1
            print(f'Deleted file from Media: {document["file_name"]}')
        except Exception as e:
            print(f'Error deleting file from Media: {document["file_name"]}, {e}')

    async for document in cursor_media5:
        try:
            await Media5.collection.delete_one({"_id": document["file_id"]})
            deleted_count_media5 += 1
            print(f'Deleted file from Media: {document["file_name"]}')
        except Exception as e:
            print(f'Error deleting file from Media: {document["file_name"]}, {e}')
            

    deleted_count = deleted_count_media1 + deleted_count_media2 + deleted_count_media3 + deleted_count_media4 + deleted_count_media4
    return deleted_count

async def get_file_details(file_id):
    for model in ALL_MEDIA:
        result = await model.find({"file_id": file_id}).to_list(length=1)
        if result:
            return result

def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")

def unpack_new_file_id(new_file_id):
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref

def get_readable_time(seconds):
    result = ""
    days, remainder = divmod(seconds, 86400)
    if days:
        result += f"{int(days)}d"
    hours, remainder = divmod(remainder, 3600)
    if hours:
        result += f"{int(hours)}h"
    minutes, seconds = divmod(remainder, 60)
    if minutes:
        result += f"{int(minutes)}m"
    result += f"{int(seconds)}s"
    return result

