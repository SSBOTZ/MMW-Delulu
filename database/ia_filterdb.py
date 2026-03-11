import asyncio
import re
import base64
from struct import pack
from typing import Optional
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorClient
from umongo import Instance, Document, fields
from marshmallow.exceptions import ValidationError
from info import *
from sample_info import tempDict

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

def create_media_model(instance):
    @instance.register
    class Media(Document):
        file_id = fields.StrField(attribute="_id")
        file_ref = fields.StrField(allow_none=True)
        file_name = fields.StrField(required=True)
        file_size = fields.IntField(required=True)
        file_type = fields.StrField(allow_none=True)
        mime_type = fields.StrField(allow_none=True)
        caption = fields.StrField(allow_none=True)

        class Meta:
            collection_name = COLLECTION_NAME
            indexes = ["$file_name"]
            strict = False

    return Media

Media = create_media_model(instance)
Media2 = create_media_model(instance2)
Media3 = create_media_model(instance3)
Media4 = create_media_model(instance4)
Media5 = create_media_model(instance5)

ALL_MEDIA = [Media, Media2, Media3, Media4, Media5]

saveMedia: Optional[Document] = None

async def choose_mediaDB():
    global saveMedia

    db_map = {
        DATABASE_URI: Media,
        DATABASE_URI2: Media2,
        DATABASE_URI3: Media3,
        DATABASE_URI4: Media4,
        DATABASE_URI5: Media5,
    }

    uri = tempDict.get("indexDB")
    saveMedia = db_map.get(uri, Media)

async def check_file(media):
    file_id, file_ref = unpack_new_file_id(media.file_id)

    tasks = [
        model.collection.find_one({"_id": file_id})
        for model in ALL_MEDIA
    ]

    results = await asyncio.gather(*tasks)

    if any(results):
        return None

    return "okda"

async def save_file(media):

    global saveMedia

    if saveMedia is None:
        await choose_mediaDB()

    file_id, file_ref = unpack_new_file_id(media.file_id)

    file_name = re.sub(
        r"(_|\+|\-|\.|\[.*?\]|\@.*?|www.*?|MLM)",
        " ",
        str(media.file_name)
    )

    try:

        caption = getattr(media, "caption", None)
        caption_html = caption.html if caption else None

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
        return True

    except DuplicateKeyError:
        return False

    except ValidationError:
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
        regex = re.compile(raw_pattern, re.IGNORECASE)
    except:
        return [], "", 0

    search_filter = {"file_name": regex}

    if USE_CAPTION_FILTER:
        search_filter = {
            "$or": [
                {"file_name": regex},
                {"caption": regex}
            ]
        }

    if file_type:
        search_filter["file_type"] = file_type

    tasks = [
        model.find(search_filter).sort("$natural", -1).to_list(length=50)
        for model in ALL_MEDIA
    ]

    results = await asyncio.gather(*tasks)

    merged = []
    for r in results:
        merged.extend(r)

    total = len(merged)

    merged = merged[offset:offset + max_results]

    next_offset = offset + len(merged)

    if next_offset >= total:
        next_offset = ""

    return merged, next_offset, total


async def get_bad_files(query, file_type=None, filter=False):

    query = query.strip()

    if not query:
        raw_pattern = "."
    elif " " not in query:
        raw_pattern = r"(\b|[\.\+\-_])" + query + r"(\b|[\.\+\-_])"
    else:
        raw_pattern = query.replace(" ", r".*[\s\.\+\-_]")

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return []

    filter = {"file_name": regex}

    if file_type:
        filter["file_type"] = file_type

    total_results_media1 = await Media.count_documents(filter)
    total_results_media2 = await Media2.count_documents(filter)
    total_results_media3 = await Media3.count_documents(filter)
    total_results_media4 = await Media4.count_documents(filter)
    total_results_media5 = await Media5.count_documents(filter)

    total_results = (
        total_results_media1
        + total_results_media2
        + total_results_media3
        + total_results_media4
        + total_results_media5
    )

    cursor_media1 = Media.find(filter).sort("$natural", -1)
    files_media1 = await cursor_media1.to_list(length=total_results_media1)

    cursor_media2 = Media2.find(filter).sort("$natural", -1)
    files_media2 = await cursor_media2.to_list(length=total_results_media2)

    cursor_media3 = Media3.find(filter).sort("$natural", -1)
    files_media3 = await cursor_media3.to_list(length=total_results_media3)

    cursor_media4 = Media4.find(filter).sort("$natural", -1)
    files_media4 = await cursor_media4.to_list(length=total_results_media4)

    cursor_media5 = Media5.find(filter).sort("$natural", -1)
    files_media5 = await cursor_media5.to_list(length=total_results_media5)

    return (
        files_media1,
        files_media2,
        files_media3,
        files_media4,
        files_media5,
        total_results,
    )


async def delete_files_below_threshold(threshold_size_mb=40, batch_size=20):

    threshold = threshold_size_mb * 1024 * 1024
    deleted = 0

    for model in ALL_MEDIA:

        cursor = model.find(
            {"file_size": {"$lt": threshold}}
        ).limit(batch_size)

        async for doc in cursor:

            try:
                await model.collection.delete_one(
                    {"_id": doc["file_id"]}
                )
                deleted += 1
            except:
                pass

    return deleted


async def get_file_details(file_id):

    for model in ALL_MEDIA:

        result = await model.collection.find_one({"_id": file_id})

        if result:
            return result

    return None


def encode_file_id(s: bytes):

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


def encode_file_ref(file_ref: bytes):

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
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days:
        result += f"{int(days)}d "

    if hours:
        result += f"{int(hours)}h "

    if minutes:
        result += f"{int(minutes)}m "

    result += f"{int(seconds)}s"

    return result

