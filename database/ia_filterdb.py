import re
import asyncio
from itertools import zip_longest
import base64
import logging
from struct import pack
from typing import Optional
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Tuple, Optional, Dict, Any, Union
from umongo import Instance, Document, fields
from marshmallow.exceptions import ValidationError
from info import *
from sample_info import tempDict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

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

LIMIT = 50

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
            indexes = ["$file_name"]
            collection_name = COLLECTION_NAME
            
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

    uri = tempDict['indexDB']
    saveMedia = db_map.get(uri, Media)

async def check_file(media):
    file_id, _ = unpack_new_file_id(media.file_id)
    results = await asyncio.gather(
        Media.collection.find_one({"_id": file_id}, {"_id": 1}),
        Media2.collection.find_one({"_id": file_id}, {"_id": 1}),
        Media3.collection.find_one({"_id": file_id}, {"_id": 1}),
        Media4.collection.find_one({"_id": file_id}, {"_id": 1}),
        Media5.collection.find_one({"_id": file_id}, {"_id": 1}),
    )
    if any(results):
        return None

    return "okda"

async def is_duplicate(file_id: str) -> bool:
    try:
        tasks = [
            coll.find_one({"_id": file_id}, projection={"_id": 1})
            for coll in ALL_MEDIA
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                logger.warning(f"⚠️ Duplicate check failed in {ALL_COLLECTIONS[idx].__name__}: {result}")
                continue

            if result:
                logger.info(f"🔁 Duplicate detected in {ALL_COLLECTIONS[idx].__name__}: {file_id}")
                return True

        return False

    except Exception as e:
        logger.error(f"❌ Duplicate check error: {e}")
        return False

async def save_file(media):

    global saveMedia

    if saveMedia is None:
        await choose_mediaDB()

    file_id, file_ref = unpack_new_file_id(media.file_id)

    file_name = re.sub(r"(_|\+|\-|\.|\[.*?\]|\@.*?|www.*?|MLM)", " ", str(media.file_name))
    file_name = re.sub(r"(_|\+\s|\-|\.|\+|\[MM\]\s|\[MM\]_|\@TvSeriesBay|\@Cinema\sCompany|\@Cinema_Company|\@CC_|\@CC|\@MM_New|\@MM_Linkz|\@MOVIEHUNT|\@CL|\@FBM|\@CKMSERIES|www_DVDWap_Com_|MLM|\@WMR|\[CF\]\s|\[CF\]|\@IndianMoviez|\@tamil_mm|\@infotainmentmedia|\@trolldcompany|\@Rarefilms|\@yamandanmovies|\[YM\]|\@Mallu_Movies|\@YTSLT|\@DailyMovieZhunt|\@I_M_D_B|\@CC_All|\@PM_Old|Dvdworld|\[KMH\]|\@FBM_HW|\@Film_Kottaka|\@CC_X265|\@CelluloidCineClub|\@cinemaheist|\@telugu_moviez|\@CR_Rockers|\@CCineClub|KC_|\[KC\])", " ", str(media.file_name))

    if not file_name.lower().endswith(".mkv"): # Skip File Name Not End With  (.mkv ) Only Add & Support Mkv File Only
        logger.info(f"⏭️ Skipped (not .mkv): {file_name}")
        return False, 0
    if await is_duplicate(file_id): # Duplicate File Never Index
        logger.warning(f"🔁 𝗗𝘂𝗽𝗹𝗶𝗰𝗮𝘁𝗲 | {file_name} | {file_id[:8]}...")
        return False, 0
    if not media or not getattr(media, "file_name", None): # Skip File Without Name
        logger.warning("⚠️ Skipped: Missing filename")
        return False, 0
        
    try:
        if await saveMedia.count_documents({'file_id': file_id}, limit=1):
            logger.warning(f'{getattr(media, "file_name", "NO_FILE")} is already saved in the active DB!')
            return False, 0
        
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
        pattern = '.'
    elif ' ' not in query:
        pattern = rf'(\b|[\.\+\-_:]|\s|&){re.escape(query)}(\b|[\.\+\-_:]|\s|&)'
    else:
        pattern = re.escape(query).replace(r'\ ', r'.*[&\s\.\+\-_()\[\]:]')

    try:
        regex = re.compile(pattern, re.IGNORECASE)
    except re.error:
        return [], "", 0

    if USE_CAPTION_FILTER:
        filter_query = {"$or": [{"file_name": regex}, {"caption": regex}]}
    else:
        filter_query = {"file_name": regex}

    if file_type:
        filter_query["file_type"] = file_type

    offset = max(offset, 0)

    count_tasks = [db.count_documents(filter_query) for db in ALL_MEDIA]
    counts = await asyncio.gather(*count_tasks)
    total_results = sum(counts)

    find_tasks = [
        db.find(filter_query)
        .sort("_id", -1)
        .skip(offset)
        .limit(max_results)
        .to_list(length=max_results)
        for db in ALL_MEDIA
    ]

    results = await asyncio.gather(*find_tasks)

    files = []
    for group in zip_longest(*results):
        for item in group:
            if item:
                files.append(item)
            if len(files) >= max_results:
                break
        if len(files) >= max_results:
            break

    next_offset = offset + len(files)
    if next_offset >= total_results:
        next_offset = ""

    return files, next_offset, total_results

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

async def get_file_details(file_id: str) -> List[Dict[str, Any]]:
    filter_q = {'_id': file_id}

    for idx, coll in enumerate(ALL_MEDIA, 1):
        try:
            doc = await coll.find_one(filter_q)
            if doc:
                return [doc]
        except Exception as e:
            continue

    return []

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

